from casbin import Enforcer
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

enforcer = Enforcer(
    os.path.join(BASE_DIR, "casbin/model.conf"),
    os.path.join(BASE_DIR, "casbin/policy.csv")
)

def authorize(role: str, resource: str, action: str):
    if not enforcer.enforce(role, resource, action):
        raise PermissionError(
            f"RBAC DENY → role={role}, resource={resource}, action={action}"
        )
