from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/me")
def get_me(
    token: str = Depends(oauth2_scheme),
    current_user: User = Depends(get_current_user)
):
    return {
        "token": token,
        "user": current_user
    }