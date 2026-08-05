from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.utils.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    email = payload.get("sub")

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


def get_current_admin(
    current_user: User = Depends(get_current_user)
):

    if current_user.role != "Admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user


def get_current_manager(
    current_user: User = Depends(get_current_user)
):

    if current_user.role not in ["Admin", "Manager"]:
        raise HTTPException(
            status_code=403,
            detail="Manager access required"
        )

    return current_user


def get_current_staff(
    current_user: User = Depends(get_current_user)
):

    return current_user