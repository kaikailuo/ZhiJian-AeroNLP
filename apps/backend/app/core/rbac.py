from __future__ import annotations

ROLE_ADMIN = "admin"
ROLE_USER = "user"

PERMISSIONS = {
    ROLE_ADMIN: {"notam", "dashboard", "api-keys", "tasks", "users"},
    ROLE_USER: {"notam", "dashboard"},
}


def has_permission(role: str, resource: str) -> bool:
    return resource in PERMISSIONS.get(role, set())
