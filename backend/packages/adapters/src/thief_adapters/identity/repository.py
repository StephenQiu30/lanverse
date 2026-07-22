from __future__ import annotations

from datetime import datetime
from typing import Any, cast
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from sqlalchemy.orm import Session

from thief_core.identity import Invitation, Role, User


class SqlAlchemyIdentityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_invitation(self, token_hash: str) -> Invitation | None:
        row = (
            self._session.execute(
                text(
                    "SELECT id, email, token_hash, role, invited_by, created_at, "
                    "expires_at, accepted_at, revoked_at "
                    "FROM identity.invitations WHERE token_hash = :token_hash"
                ),
                {"token_hash": token_hash},
            )
            .mappings()
            .one_or_none()
        )
        if row is None:
            return None
        return Invitation(
            id=cast(UUID, row["id"]),
            email=str(row["email"]),
            token_hash=str(row["token_hash"]),
            role=Role(str(row["role"])),
            invited_by=cast(UUID, row["invited_by"]),
            created_at=cast(datetime, row["created_at"]),
            expires_at=cast(datetime, row["expires_at"]),
            accepted_at=cast(datetime | None, row["accepted_at"]),
            revoked_at=cast(datetime | None, row["revoked_at"]),
        )

    def email_exists(self, email: str) -> bool:
        return (
            self._session.execute(
                text("SELECT 1 FROM identity.users WHERE email = :email"),
                {"email": email},
            ).scalar_one_or_none()
            is not None
        )

    def add_user(self, user: User) -> None:
        self._session.execute(
            text(
                "INSERT INTO identity.users "
                "(id, email, password_hash, role, is_active, created_at) "
                "VALUES (:id, :email, :password_hash, :role, :is_active, :created_at)"
            ),
            {
                "id": user.id,
                "email": user.email,
                "password_hash": user.password_hash,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at,
            },
        )

    def accept_invitation(
        self,
        invitation_id: UUID,
        accepted_at: datetime,
    ) -> bool:
        result = cast(
            CursorResult[Any],
            self._session.execute(
                text(
                    "UPDATE identity.invitations SET accepted_at = :accepted_at "
                    "WHERE id = :id AND accepted_at IS NULL AND revoked_at IS NULL "
                    "AND created_at <= :accepted_at AND expires_at > :accepted_at"
                ),
                {"id": invitation_id, "accepted_at": accepted_at},
            ),
        )
        return result.rowcount == 1
