from fastapi import APIRouter, HTTPException,status
from fastapi.params import Depends

from shared.authentication.dependency import authenticate
from shared.authentication.jwt import JWTService
from shared.authentication.password import PasswordService
from user.async_repository import UserRepository
from user.models import User
from user.request import UserAuthRequest
from user.response import UserResponse, UserTokenResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post(
    "/sign-up",
    status_code =status.HTTP_201_CREATED,
    response_model=UserResponse,
)
async def user_sign_up_handler(
    body: UserAuthRequest,
    user_repo: UserRepository = Depends(),
    password_service: PasswordService = Depends(),
):
    if not await user_repo.validate_username(username=body.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )

    new_user = User.create(
        username=body.username,
        password_hash=password_service.hash_password(plain_text=body.password),
    )
    await user_repo.save(user=new_user)
    return UserResponse.build(user=new_user)

@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=UserTokenResponse,
)
async def user_login_handler(
    body: UserAuthRequest,
    user_repo: UserRepository = Depends(),
    jwt_service: JWTService = Depends(),
    password_service: PasswordService = Depends(),
):
    user: User | None = await user_repo.get_user_by_username(username=body.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not password_service.check_password(plain_text=body.password, hashed_password=user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
        )

    access_token = jwt_service.encode_access_token(user_id=user.id)
    return UserTokenResponse.build(access_token=access_token)

@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserResponse,
)
async def get_me_handler(
    me_id: int = Depends(authenticate),
    user_repo: UserRepository = Depends(),
):
    user: User | None = await user_repo.get_user_by_id(user_id=me_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse.build(user=user)
