from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.config import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI

from app.database.database import get_db
from app.models.user import User
from app.schemas.user_schema import (
    UserCreate,
    UserResponse,
    Token,
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter()


# ---------------- REGISTER ---------------- #

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# ---------------- LOGIN ---------------- #

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = (
        db.query(User)
        .filter(User.email == form_data.username)
        .first()
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    if not verify_password(
        form_data.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Email or Password"
        )

    access_token = create_access_token(
        {
            "sub": db_user.email,
            "id": db_user.id,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



# ---------------- GOOGLE LOGIN ---------------- #

class GoogleLoginRequest(BaseModel):
    code: str

@router.post("/google", response_model=Token)
def google_login(request_data: GoogleLoginRequest, db: Session = Depends(get_db)):
    # 1. Exchange auth code for Google access token
    token_url = "https://oauth2.googleapis.com/token"
    payload = {
        "code": request_data.code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    import httpx
    try:
        response = httpx.post(token_url, data=payload)
        response.raise_for_status()
        token_data = response.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to exchange token with Google: {str(e)}"
        )

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=400,
            detail="Google did not return an access token"
        )

    # 2. Fetch user information using access token
    userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        userinfo_response = httpx.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch user profile from Google: {str(e)}"
        )

    email = user_info.get("email")
    name = user_info.get("name", "Google User")

    if not email:
        raise HTTPException(
            status_code=400,
            detail="Google account does not have an email address"
        )

    # 3. Find or create user in local database
    db_user = db.query(User).filter(User.email == email).first()
    if not db_user:
        db_user = User(
            name=name,
            email=email,
            password=hash_password("google_temp_pass"),
            role="Retail Analyst"  # default role for new signups
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    # 4. Generate local JWT access token
    local_token = create_access_token(
        {
            "sub": db_user.email,
            "id": db_user.id,
            "role": db_user.role
        }
    )

    return {
        "access_token": local_token,
        "token_type": "bearer"
    }



# ---------------- TEST ROUTE ---------------- #


@router.get("/hello")
def hello():
    return {
        "message": "Auth Router Working"
    }