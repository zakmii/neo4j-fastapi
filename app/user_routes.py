from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis

from app.crud.user import get_user_by_username, update_user_query_limit_data
from app.models.user import UserPublic, UserQueryLimitUpdate
from app.utils.redis_utils import get_redis_connection
from app.utils.security import get_current_active_user  # Assuming you have this utility

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: UserPublic = Depends(get_current_active_user),
    db: Redis = Depends(get_redis_connection),
):
    """
    Fetch the current logged-in user's details.
    """
    # The get_current_active_user dependency already fetches the user.
    # We might need to re-fetch from DB if query_limits can change outside this session
    # or if get_current_active_user doesn't return the full UserInDB model.
    # For now, assuming current_user from get_current_active_user is sufficient
    # or that it's a UserInDB compatible model that can be validated by UserPublic.

    # If get_current_active_user returns a basic user (e.g. just username from token),
    # you'd need to fetch the full user details here:
    user_in_db = await get_user_by_username(db, username=current_user.username)
    if user_in_db is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserPublic.model_validate(user_in_db)


@router.put("/me/query_limits", response_model=UserPublic)
async def update_current_user_query_limits(
    query_limit_data: UserQueryLimitUpdate,
    current_user: UserPublic = Depends(
        get_current_active_user
    ),  # UserPublic might be too restrictive if it doesn't have id/username
    db: Redis = Depends(get_redis_connection),
):
    """
    Update the query limits for the current logged-in user.
    """
    # Ensure the user performing the update is the one whose limits are being updated.
    # current_user.username should be available from the token via get_current_active_user

    success = await update_user_query_limit_data(
        db,
        username=current_user.username,  # Make sure current_user has a username attribute
        query_limits=query_limit_data.query_limits,
        last_query_reset=query_limit_data.last_query_reset.isoformat(),  # Store as ISO format string
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or update failed",
        )

    # Fetch the updated user details to return
    updated_user = await get_user_by_username(db, username=current_user.username)
    if updated_user is None:
        # This should ideally not happen if update_user_query_limit_data was successful
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve updated user details",
        )
    return UserPublic.model_validate(updated_user)
