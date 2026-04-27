"""
Analysis Engine

This is the core of AccessIQ. It:
1.) Loads all user-permission mappings for an org
2.) Detects SoD violations by checking every user's permissions against a SoD rules
3.) Computes peer group averages (Users grouped by job title + department)
4.) Scores each user 0-100 based on violations and over-provisioning
5.) Saves results to user_risk_scores and sof_violations tables
"""


from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.models.models import (
    User, SodRule, Scan, UserRiskScore, SodViolation,
    UserRoleAssignment, RolePermission
)

# ── Risk weight constants ─────────────────────────────────────
# These control how much each factor contributes to the final score
SOD_VIOLATION_WEIGHT = 50       # SoD violations are the most serious
OVERPROV_WEIGHT = 30            # Over-provisioning also adds significant risk
PRIVILEGE_WEIGHT = 20            # Total permissions add some risk but less than violations

SEVERITY_SCORES = {
    "critical": 50,
    "high": 30,
    "medium": 20,
    "low": 10,
}

RISK_LABELS = [
    (75, "critical"),
    (50, "high"),
    (25, "medium"),
    (0, "low"),
]

def get_risk_label(score: float) -> str:
    for threshold, label in RISK_LABELS:
        if score >= threshold:
            return label
    return "low"  # Default to low if something goes wrong


async def run_scan(db: AsyncSession, org_id: str) -> dict:
    """ 
    Main entry point. Creates a scan record, runs all analysis,
    saves results, and returns the completed scan with stats.
    """

    # Create scan record

    scan = Scan(org_id=org_id, status="running")
    db.add(scan)
    await db.commit()


    try:
        # 1.) Load all user permissions for this org
        user_permissions = await load_user_permissions(db, org_id)

        #2.) Load SoD rules for this org
        sod_rules = await load_sod_rules(db, org_id)

        #3.) Load all users
        result = await db.execute(
            select(User).where(User.org_id == org_id, User.is_active == True)
        )
        users = result.scalars().all()

        # 4.) Build peer groups (group users by department + job title)
        peer_groups = build_peer_groups(users, user_permissions)

        violations_found = 0

        # 5.) Analyze each user

        for user in users:
            perms = user_permissions.get(user.id, {})

            # Detect SoD violations
            user_violations = detect_sod_violations(user.id, perms, sod_rules)
            violations_found += len(user_violations)

            # Save violations to db
            for v in user_violations:
                db.add(SodViolation(
                    scan_id = scan.id,
                    user_id = user.id,
                    rule_id=v["rule_id"],
                    permission_a_id=v["permission_a_id"],
                    permission_b_id=v["permission_b_id"],
                    via_role_a_id=v.get("via_role_a_id"),
                    via_role_b_id=v.get("via_role_b_id"),
                    status="open",
                ))

            # Compute risk score
            score = compute_risk_score(
                user=user,
                perms=perms,
                violations=user_violations,
                peer_groups=peer_groups
            )

            db.add(UserRiskScore(
                user_id=user.id,
                scan_id=scan.id,
                overall_score=score["overall"],
                overprov_score=score["overprov"],
                sod_score=score["sod"],
                privileged_score=score["privileged"],
                permission_count=score["permission_count"],
                peer_avg_permissions=score["peer_avg"],
                sod_violation_count=len(user_violations),
                risk_label=get_risk_label(score["overall"]),
            ))

        # 6.) Update scan record
        scan.status = "completed"
        scan.users_scanned = len(users)
        scan.violtions_found = violations_found
        scan.completed_at = datetime.utcnow()
        await db.flush()

    except Exception as e:
        scan.status = "failed"
        await db.flush()
        raise e
    
    return scan

async def load_user_permissions (
    db: AsyncSession, org_id: str
) -> dict[str, dict]:
    """
    Returns a dict mapping user_id -> {
        permission_id: {
        "permission_name": str,
        "risk_level": int,
        "role_id": str,
        "role_name": str,
        "is_privileged": bool,
    }
    """
    result = await db.execute(text("""
        SELECT
            u.id            AS user_id,
            p.id            AS permission_id,
            p.name          AS permission_name,
            p.risk_level,
            r.id            AS role_id,
            r.name          AS role_name,
            r.is_privileged
        FROM users u
        JOIN user_role_assignments ura ON ura.user_id = u.id AND ura.status = 'active'
        JOIN roles r                   ON r.id = ura.role_id
        JOIN role_permissions rp       ON rp.role_id = r.id
        JOIN permissions p             ON p.id = rp.permission_id
        WHERE u.org_id = :org_id AND u.is_active = TRUE
    """), {"org_id": org_id})

    rows = result.fetchall()
    user_permissions: dict[str, dict] = {}

    for row in rows:
        uid = row.user_id
        if uid not in user_permissions:
            user_permissions[uid] = {}
        user_permissions[uid][row.permission_id] = {
            "permission_name": row.permission_name,
            "risk_level": row.risk_level,
            "role_id": row.role_id,
            "role_name": row.role_name,
            "is_privileges": row.is_privileged,
        }
    return user_permissions

async def load_sod_rules(db: AsyncSession, org_id: str) -> list[dict]:
    """Load all SoD rules for the org."""
    result = await db.execute(
        select(SodRule).where(SodRule.org_id == org_id)
    )
    rules = result.scalars().all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "permission_a_id": r.permission_a_id,
            "permission_b_id": r.permission_b_id,
            "severity": r.severity,
        }
        for r in rules
    ]


def detect_sod_violations(
    user_id: str,
    perms: dict,
    sod_rules: list[dict],
) -> list[dict]:
    """
    Check if a user holds both permissions in any SoD rule.
    Returns a list of violation dicts.
    """
    violations = []
    perms_ids = set(perms.keys())

    for rule in sod_rules:
        a = rule["permission_a_id"]
        b = rule["permission_b_id"]

        if a in perms_ids and b in perms_ids:
            violations.append({
                "rule_id": rule["id"],
                "rule_name": rule["name"],
                "permission_a_id": a,
                "permission_b_id": b,
                "severity": rule["severity"],
                "via_role_a_id": perms[a]["role_id"],
                "via_role_b_id": perms[b]["role_id"],
            })
    
    return violations


def build_peer_groups(
    users: list,
    user_permissions: dict,
) -> dict[str, float]:
    """
    Groups users by (department, job_title) and computes the
    average permission count for each group.

    Returns dict mapping (department, job_title) -> avg_permission_count
    """
    groups: dict[str, list[int]] = {}

    for user in users:
        key = (user.department or "unknown", user.job_title or "unknown")
        count = len(user_permissions.get(user.id, {}))
        if key not in groups:
            groups[key] = []
        groups[key].append(count)

    return {
        key: sum(counts) / len(counts)
        for key, counts in groups.items()
    }


def compute_risk_score(
    user,
    perms: dict,
    violations: list[dict],
    peer_groups: dict,
) -> dict:
    """
    Computes a 0-100 risk score for a user.

    Components:
    - SoD score: based on number and severity of violations
    - Over-provisioning score: how far above peer avg the user is
    - Privileged score: whether user has privileged roles
    """
    permission_count = len(perms)
    peer_key = (user.department or "unknown", user.job_title or "unknown")
    peer_avg = peer_groups.get(peer_key, permission_count)

    # SoD component (0-50)
    sod_raw = sum(SEVERITY_SCORES.get(v["severity"], 10) for v in violations)
    sod_score = min(sod_raw, 50)

    # Over-provisioning component (0-30)
    if peer_avg > 0:
        overprov_ratio = (permission_count - peer_avg) / peer_avg
        overprov_score = min(max(overprov_ratio * 30, 0), 30)
    else:
        overprov_score = 0

    # Privileged access component (0-20)
    has_privileged = any(p.get("is_privileged", False) for p in perms.values())
    privileged_score = 20 if has_privileged else 0

    overall = sod_score + overprov_score + privileged_score

    return {
        "overall": round(min(overall, 100), 2),
        "sod": round(sod_score, 2),
        "overprov": round(overprov_score, 2),
        "privileged": round(privileged_score, 2),
        "permission_count": permission_count,
        "peer_avg": round(peer_avg, 2),
    }