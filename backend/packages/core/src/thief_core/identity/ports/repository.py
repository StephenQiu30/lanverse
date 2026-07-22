from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from thief_core.identity.domain import Invitation, User
from thief_core.shared import UnitOfWork


class IdentityRepository(Protocol):
    def find_invitation(self, token_hash: str) -> Invitation | None: ...

    def email_exists(self, email: str) -> bool: ...

    def add_user(self, user: User) -> None: ...

    def accept_invitation(
        self,
        invitation_id: UUID,
        accepted_at: datetime,
    ) -> bool: ...


class IdentityUnitOfWork(UnitOfWork, Protocol):
    identities: IdentityRepository
