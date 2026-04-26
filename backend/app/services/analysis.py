"""
Analysis Engine

This is the core of AccessIQ. It:
1.) Loads all user-permission mappings for an org
2.) Detects SoD violations by checking every user's permissions against a SoD rules
3.) Computes peer group averages (Users grouped by job title + department)
4.) Scores each user 0-100 based on violations and over-provisioning
5.) Saves results to user_risk_scores and sof_violations tables
"""


from datatime import datetime
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
        user_permissions = await load_user_permission(db, org_id)

        #2.) Load SoD rules for this org
        sod_rules = await load_sod_rules(db, org_id)

        #3.) Load all users
        result = await db.execute(
            select(User).where(User.org_id == org_id, User.is_active == True)
        )
        users = result.scalars().all()

        # 4.) Build peer groups (group users by department + job title)
        peer_groups = build_groups(users, user_permissions)

        violations_found = 0

        # 5.) Analyze each user

        for user in users:
            perms = user_permissions.get(user.id, {})

            # Detect SoD violations
            user_violations = detect_sof_violations(user.id, perms, sod_rules)
            violations_found += len(user_violations)

            # Save violations to db
            for v in user_violations:
                db.add(SodViolation(
                    scan_id = scan.id,
                    user_id = user.id,
                    rule_id=v["rule_id"],
                    permission_a_id=v["permission_a_id"],
                    permission_b_id=v["permission_b_id"],
                    via_role_a_i=v.get("via_role_a_id"),
                    via_role_b_id=v.get("via_role_b_id"),
                    status="open",
                ))

            # Compute risk score
            score = computer_risk_score(
                user=user,
                perms=perms,
                violations=user_violations,
                peer_groups=peer_groups
            )

            db.add(UserRiskScore(
                user_id=user.id,
                scan_id=scan.id,
                overall_score=score["overall"],
                overprov_score=score["overprovisioning"],
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

#async def load_user_permissions ()