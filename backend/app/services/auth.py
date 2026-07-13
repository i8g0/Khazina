"""Authentication service: login and token issuance."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config.auth import AuthSettings
from app.core.jwt import create_access_token
from app.core.security import verify_password
from app.repositories import UserRepository
from app.schemas.auth import TokenResponse
from app.services.base import BaseService
from app.services.exceptions import AuthenticationError


class AuthService(BaseService):
    """Authenticate users and issue JWT access tokens."""

    def __init__(
        self,
        session: Session,
        user_repository: UserRepository,
        auth_settings: AuthSettings,
    ) -> None:
        super().__init__(session)
        self._users = user_repository
        self._auth = auth_settings

    def login(self, *, email: str, password: str) -> TokenResponse:
        email = email.strip().lower()
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            raise AuthenticationError("Invalid email or password")
        if not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")

        access_token = create_access_token(
            subject=str(user.id),
            auth_settings=self._auth,
        )
        return TokenResponse(access_token=access_token, token_type="bearer")
