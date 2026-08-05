from fastapi import APIRouter, Depends

from app.dependencies.auth import get_current_admin
from app.models.user import User

router = APIRouter()


@router.get("/dashboard")
def admin_dashboard(
    current_user: User = Depends(get_current_admin)
):
    return {
        "message": "Welcome Admin",
        "user": current_user.name,
        "role": current_user.role
    }