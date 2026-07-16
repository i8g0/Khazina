from __future__ import annotations

from sqlalchemy import select

from app.db.models import RiskCategory
from app.repositories.base import BaseRepository


class RiskCategoryRepository(BaseRepository):
    """Read-mostly access to seeded risk taxonomy."""

    def get(self, code: str) -> RiskCategory | None:
        return self._session.get(RiskCategory, code)

    def list_active(self) -> list[RiskCategory]:
        stmt = (
            select(RiskCategory)
            .where(RiskCategory.is_active.is_(True))
            .order_by(RiskCategory.sort_order)
        )
        return self._list(stmt)
