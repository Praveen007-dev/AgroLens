from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.schemas.mobile import (
    AuthCredentials,
    AuthLogin,
    AuthSessionResponse,
    BasicUserProfile,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    GenericMessage,
    ResetPasswordRequest,
)
from backend.app.services import auth as auth_service


router = APIRouter(prefix="/auth", tags=["Mobile Authentication"])
_bearer = HTTPBearer(auto_error=False)


def _client_ip(request: Request) -> str:
    return request.client.host if request.client is not None else "unknown"


def _raise_auth_error(error: auth_service.AuthServiceError) -> None:
    raise HTTPException(
        status_code=error.status_code,
        detail=error.detail,
        headers={"WWW-Authenticate": "Bearer"} if error.status_code == 401 else None,
    ) from error


def current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> BasicUserProfile:
    try:
        token = credentials.credentials if credentials else None
        return auth_service.authenticate_token(token)
    except auth_service.AuthServiceError as error:
        _raise_auth_error(error)


def current_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="A valid session is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


@router.post("/register", response_model=AuthSessionResponse, status_code=201)
def register(payload: AuthCredentials):
    try:
        return auth_service.register(payload)
    except auth_service.AuthServiceError as error:
        _raise_auth_error(error)


@router.post("/login", response_model=AuthSessionResponse)
def login(payload: AuthLogin, request: Request):
    try:
        return auth_service.login(payload, _client_ip(request))
    except auth_service.AuthServiceError as error:
        _raise_auth_error(error)


@router.post("/forgot-password", response_model=GenericMessage)
def forgot_password(payload: ForgotPasswordRequest, request: Request):
    try:
        auth_service.request_password_reset(payload.email, _client_ip(request))
    except auth_service.AuthServiceError as error:
        _raise_auth_error(error)
    return GenericMessage(
        message="If an account exists for that email, reset instructions will be sent."
    )


@router.post("/reset-password", response_model=GenericMessage)
def reset_password(payload: ResetPasswordRequest):
    try:
        auth_service.reset_password(payload.reset_token, payload.new_password)
    except auth_service.AuthServiceError as error:
        _raise_auth_error(error)
    return GenericMessage(message="Password has been reset. Please sign in again.")


@router.post("/change-password", response_model=GenericMessage)
def change_password(
    payload: ChangePasswordRequest,
    user: BasicUserProfile = Depends(current_user),
    token: str = Depends(current_token),
):
    try:
        auth_service.change_password(
            user.user_id,
            payload.current_password,
            payload.new_password,
            token,
        )
    except auth_service.AuthServiceError as error:
        _raise_auth_error(error)
    return GenericMessage(message="Password updated successfully.")


@router.get("/me", response_model=BasicUserProfile)
def me(user: BasicUserProfile = Depends(current_user)):
    return user


@router.post("/logout", response_model=GenericMessage)
def logout(
    _: BasicUserProfile = Depends(current_user),
    token: str = Depends(current_token),
):
    try:
        auth_service.logout(token)
    except auth_service.AuthServiceError as error:
        _raise_auth_error(error)
    return GenericMessage(message="Logged out successfully.")
