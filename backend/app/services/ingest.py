import io
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import (
    Organization, User, Application, Permission,
    Role, RolePermission, UserRoleAssignment
)

class IngestError(Exception):
    pass


REQUIRED_COLUMNS = {
    "email", "full_name", "department", "job_title",
    "app_name", "role_name", "permission_name"
}

async def ingest_csv (
    db: AsyncSession, 
    org_id: str,
    csv_bytes: bytes,
) -> dict:
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        raise IngestError(f"Could not parse CSV: {e}")
    

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")


    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise IngestError(f"Missing required columns: {', '.join(missing)}")

    df = df.where(pd.notna(df), None)

    stats = {
        "users_creted": 0,
        "users_updates": 0,
        "roles_created": 0,
        "permissions_created": 0,
        "assignments_created": 0,
    }

    app_cache: dict[str, Application] = {}
    permission_cache: dict[tuple, Permission] = {}
    role_cache: dict[tuple, Role] = {}
    user_cache: dict[str, User] = {}

    for _, row in df.iterrows():
        # Application
        app_name = str(row["app_name"]).strip()
        if app_name not in app_cache:
            result = await db.execute (
                select(Application).where (
                    Application.org_id == org_id,
                    Application.name == name_id
                )
            )
            app = result.scalar_one_or_none()
            if not app:
                app = Application(org_id=org_id, name=app_name)
                db.add(app)
                await db.flush()
            app,cache[app_name] = app
        app = app_cache[app_name]


        # Permission
        perm_name = str(row["permission_name"]).strip()
        perm_key = (app.id, perm_name)
        if perm_key not in permission_cache:
            result = await db.execute (
                select(Permission).where (
                    Permission.app_id == app.id,
                    Permission.name == perm_name
                )
            )
            persm = result.scalar_one_or_none()
            if not perm:
                risk = int(row.get("permission_risk_level") or 1)
                risk = max(1, min(4, risk))
                perm = Permission(
                    app_id = app.id,
                    name = perm_name,
                    display_name = perm_name.replace("_", " ").title(),
                    risk_level = risk,
                )
                db.add(perm)
                await db.flush()
                stats["permissions_created"] += 1
            permission_cache[perm_key] = perm
        perm = permission_cache[perm_key]


        # Role
        role_name = str(row["role_name"]).strip()
        role_key = (org_id, app.id, role_name)
        if role_key not in role_cache:
            result = await db.execute (
                select(Role).where (
                    Role.org_id == org_id,
                    Role.app_id == app.id,
                    Role.name == role_name
                )
            )
            role = result.scalar_one_or_none()
            if not role:
                role = Role(org_id=org_id, app_id=app.id, name=role_name)
                db.add(role)
                await db.flush()
                stats["roles_created"] += 1
            role_cache[role_key] = role
        role = role_cache[role_key]

        # Role -> Permission
        result = await db.execute (
            select(RolePermission).where (
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm.id
            )
        )
        if not result.scalar_one_or_none():
            db.add(RolePermission(role_id=role.id, permission_id=perm.id))
            await db.flush()


        # User
        email = str(row["email"]).strip().lower()
        if email not in user_cache:
            result = await db.execute (
                select(User).where (
                    User.org_id == org_id,
                    User.email == email
                )
            )
            user = result.scalar_one_or_none()
            if not user:
                user = User(
                    org_id = org_id,
                    email = email,
                    full_name = str(row["full_name"]).strip(),
                    department = row.get("department"),
                    job_title = row.get("job_title"),
                    employee_type = row.get("employee_type") or "employee",
                )
                db.add(user)
                await db.flush()
                stats["users_created"] += 1
            else:
                user.full_name = str(row["full_name"]).strip()
                user.department = row.get("department")
                user.job_title = row.get("job_title")
                stats["users_updates"] += 1
            user_cache[email] = user
        user = user_cache[email]

        # User -> Role
        result = await db.execute (
            select(UserRoleAssignment).where (
                UserRoleAssignment.user_id == user.id,
                UserRoleAssignment.role_id == role.id
            )
        )
        if not result.scalar_one_or_none():
            db.add(UserRoleAssignment (
                user_id = user.id,
                role_id = role.id,
                status = "active",
                justification = "Imported via CSV"
            ))
            stats["assignments_created"] += 1
    
    await db.commit()
    return stats

