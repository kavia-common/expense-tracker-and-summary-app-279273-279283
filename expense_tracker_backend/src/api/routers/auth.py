from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from src.api.deps import get_db_dep, get_refresh_token_from_cookie
from src.core.auth import set_refresh_cookie, clear_refresh_cookie, verify_refresh_token, create_access_and_refresh_tokens
from src.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from src.services.auth import AuthService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    summary="Register a new user",
    response_model=TokenResponse,
    status_code=201,
)
def register_user(payload: RegisterRequest, response: Response, db: Session = Depends(get_db_dep)) -> TokenResponse:
    """Register a new user with email and password.

    Parameters:
        payload: RegisterRequest body containing email, password, and optional name.

    Returns:
        TokenResponse with access token and expiry; refresh token set as httpOnly cookie.
    """
    service = AuthService(db)
    try:
        user_id = service.register(email=payload.email, password=payload.password, name=payload.name)
        user_id, access, refresh, access_exp, refresh_exp = service.login(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))  # noqa: B904
    set_refresh_cookie(response, refresh, max_age=refresh_exp)
    return TokenResponse(access_token=access, expires_in=access_exp)


@router.post(
    "/login",
    summary="Login with email and password",
    response_model=TokenResponse,
)
def login_user(payload: LoginRequest, response: Response, db: Session = Depends(get_db_dep)) -> TokenResponse:
    """Authenticate a user and provide tokens.

    Parameters:
        payload: LoginRequest body.

    Returns:
        TokenResponse with access token; refresh cookie set.
    """
    service = AuthService(db)
    try:
        user_id, access, refresh, access_exp, refresh_exp = service.login(email=payload.email, password=payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))  # noqa: B904
    set_refresh_cookie(response, refresh, max_age=refresh_exp)
    return TokenResponse(access_token=access, expires_in=access_exp)


@router.post(
    "/refresh",
    summary="Refresh access token using httpOnly cookie",
    response_model=TokenResponse,
)
def refresh_token(request: Request, response: Response) -> TokenResponse:
    """Use refresh token from cookie to get a new access token."""
    token = get_refresh_token_from_cookie(request)
    payload = verify_refresh_token(token)
    user_id_str = payload.get("sub")
    try:
        user_id = int(user_id_str)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    # Rotate refresh token to mitigate replay
    _, new_refresh, access_exp, refresh_exp = create_access_and_refresh_tokens(user_id)
    set_refresh_cookie(response, new_refresh, max_age=refresh_exp)
    # Also issue a new access
    access, _, _, _ = create_access_and_refresh_tokens(user_id)
    return TokenResponse(access_token=access, expires_in=access_exp)


@router.post(
    "/logout",
    summary="Logout and clear refresh token cookie",
    status_code=204,
)
def logout_user(response: Response) -> None:
    """Clear refresh token cookie to sign out."""
    clear_refresh_cookie(response)
    return None
