"""Executive Timeline services: append-only display event stream."""

from __future__ import annotations

import uuid
from datetime import date

from sqlalchemy.orm import Session

from app.db.models import TimelineEvent
from app.db.models.enums import RelatedEntityType, TimelineEventType
from app.repositories import OrganizationRepository, TimelineRepository
from app.services.base import BaseService
from app.services.exceptions import (
    BusinessValidationError,
    ResourceNotFoundError,
)


class TimelineService(BaseService):
    """Business use cases for the executive timeline.

    Events are append-only display records. The polymorphic reference
    (``related_entity_type`` / ``related_entity_id``) carries no database
    foreign key, so its consistency is validated here at the application
    layer, as approved in the schema design.
    """

    def __init__(
        self,
        session: Session,
        timeline_repository: TimelineRepository,
        organization_repository: OrganizationRepository,
    ) -> None:
        super().__init__(session)
        self._timeline = timeline_repository
        self._organizations = organization_repository

    def record_event(
        self,
        organization_id: uuid.UUID,
        *,
        title: str,
        event_type: str,
        event_date: date | None = None,
        reporting_period_id: uuid.UUID | None = None,
        related_entity_type: str | None = None,
        related_entity_id: uuid.UUID | None = None,
    ) -> TimelineEvent:
        self._require_organization(organization_id)
        title = title.strip()
        if not title:
            raise BusinessValidationError("Event title must not be empty")
        if event_type not in set(TimelineEventType):
            raise BusinessValidationError(f"Unknown event type '{event_type}'")

        # Polymorphic reference integrity (application layer, design §4.22):
        # both parts must be provided together and the type must be approved.
        if (related_entity_type is None) != (related_entity_id is None):
            raise BusinessValidationError(
                "related_entity_type and related_entity_id must be provided together"
            )
        if (
            related_entity_type is not None
            and related_entity_type not in set(RelatedEntityType)
        ):
            raise BusinessValidationError(
                f"Unknown related entity type '{related_entity_type}'"
            )

        if reporting_period_id is not None:
            period = self._organizations.get_reporting_period(reporting_period_id)
            if period is None:
                raise ResourceNotFoundError("ReportingPeriod", reporting_period_id)
            self._check_ownership(period, "ReportingPeriod", organization_id)

        event = TimelineEvent(
            organization_id=organization_id,
            reporting_period_id=reporting_period_id,
            event_date=event_date or date.today(),
            title=title,
            event_type=event_type,
            related_entity_type=related_entity_type,
            related_entity_id=related_entity_id,
        )
        with self._transaction():
            self._timeline.create(event)
        return event

    def get_event(self, event_id: uuid.UUID) -> TimelineEvent:
        return self._found(self._timeline.get(event_id), "TimelineEvent", event_id)

    def list_events(
        self,
        organization_id: uuid.UUID,
        *,
        event_type: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TimelineEvent]:
        self._require_organization(organization_id)
        return self._timeline.list_for_organization(
            organization_id, event_type=event_type, limit=limit, offset=offset
        )

    def delete_event(self, organization_id: uuid.UUID, event_id: uuid.UUID) -> None:
        event = self.get_event(event_id)
        self._check_ownership(event, "TimelineEvent", organization_id)
        with self._transaction():
            self._timeline.delete(event)

    # -- internals ---------------------------------------------------------------------

    def _require_organization(self, organization_id: uuid.UUID) -> None:
        if self._organizations.get_organization(organization_id) is None:
            raise ResourceNotFoundError("Organization", organization_id)
