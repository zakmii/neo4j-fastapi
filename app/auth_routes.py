from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from redis.asyncio import Redis

from app.crud.user import create_user, get_user_by_username
from app.models.user import Token, UserCreate, UserPublic
from app.utils.environment import CONFIG
from app.utils.redis_utils import get_redis_connection
from app.utils.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def signup_new_user(user: UserCreate, db: Redis = Depends(get_redis_connection)):
    """Registers a new user."""
    db_user = await get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    # Check for existing email if desired (optional)
    # email_exists = await check_email_exists(db, user.email) # Implement this if needed
    # if email_exists:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Email already registered",
    #     )

    created_user = await create_user(db=db, user=user)
    # Return UserPublic model which doesn't include the password
    return UserPublic.model_validate(created_user)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Redis = Depends(get_redis_connection),
):
    """Authenticates a user and returns a JWT access token."""
    user = await get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=CONFIG.JWT.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
