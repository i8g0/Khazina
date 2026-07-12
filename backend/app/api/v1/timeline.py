"""Executive timeline REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.api.deps import PaginationDep, TimelineServiceDep
from app.schemas.response import ApiResponse, success_response
from app.schemas.timeline import TimelineEventCreate, TimelineEventResponse

router = APIRouter(
    prefix="/organizations/{organization_id}/timeline/events",
    tags=["timeline"],
)


@router.post(
    "",
    response_model=ApiResponse[TimelineEventResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Record timeline event",
)
def record_timeline_event(
    organization_id: UUID,
    body: TimelineEventCreate,
    service: TimelineServiceDep,
) -> ApiResponse[TimelineEventResponse]:
    event = service.record_event(
        organization_id,
        title=body.title,
        event_type=body.event_type,
        event_date=body.event_date,
        reporting_period_id=body.reporting_period_id,
        related_entity_type=body.related_entity_type,
        related_entity_id=body.related_entity_id,
    )
    return success_response(
        data=TimelineEventResponse.model_validate(event),
        message="Timeline event recorded",
    )


@router.get(
    "",
    response_model=ApiResponse[list[TimelineEventResponse]],
    summary="List timeline events",
)
def list_timeline_events(
    organization_id: UUID,
    service: TimelineServiceDep,
    pagination: PaginationDep,
    event_type: str | None = Query(None),
) -> ApiResponse[list[TimelineEventResponse]]:
    events = service.list_events(
        organization_id,
        event_type=event_type,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[TimelineEventResponse.model_validate(e) for e in events],
        message="Timeline events retrieved",
    )


@router.get(
    "/{event_id}",
    response_model=ApiResponse[TimelineEventResponse],
    summary="Get timeline event by ID",
)
def get_timeline_event(
    organization_id: UUID,
    event_id: UUID,
    service: TimelineServiceDep,
) -> ApiResponse[TimelineEventResponse]:
    event = service.get_event(event_id)
    return success_response(
        data=TimelineEventResponse.model_validate(event),
        message="Timeline event retrieved",
    )


@router.delete(
    "/{event_id}",
    response_model=ApiResponse[None],
    summary="Delete timeline event",
)
def delete_timeline_event(
    organization_id: UUID,
    event_id: UUID,
    service: TimelineServiceDep,
) -> ApiResponse[None]:
    service.delete_event(organization_id, event_id)
    return success_response(data=None, message="Timeline event deleted")
