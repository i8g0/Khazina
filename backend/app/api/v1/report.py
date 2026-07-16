"""Executive reporting REST endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from app.api.deps import (
    PaginationDep,
    ReportBuilderServiceDep,
    ReportExportServiceDep,
    ReportServiceDep,
)
from app.api.permissions import RequireOrgAdmin, RequireOrgExecutive, require_org_role
from app.db.models.enums import UserRole
from app.reports.content import content_fingerprint
from app.schemas.report import (
    ReportContentResponse,
    ReportCreate,
    ReportExportResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    ReportResponse,
    ReportUpdate,
)
from app.schemas.response import ApiResponse, success_response

router = APIRouter(
    prefix="/organizations/{organization_id}/reports",
    tags=["reports"],
    dependencies=[Depends(require_org_role(UserRole.ANALYST))],
)


@router.post(
    "/generate",
    response_model=ApiResponse[ReportGenerateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Generate executive report from completed analysis run",
)
def generate_report(
    organization_id: UUID,
    body: ReportGenerateRequest,
    builder: ReportBuilderServiceDep,
    report_service: ReportServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[ReportGenerateResponse]:
    outcome = builder.generate_report(
        organization_id,
        body.analysis_run_id,
        title=body.title,
        department_id=body.department_id,
        initiating_user_id=current_user.id,
    )
    report = outcome.report
    if outcome.auto_publish_on_generate:
        report = report_service.publish_report(
            organization_id,
            report.id,
            initiating_user_id=current_user.id,
        )
    content = report.content_representation or {}
    extended = content.get("extended_metadata") or {}
    return success_response(
        data=ReportGenerateResponse(
            report=ReportResponse.model_validate(report),
            profile=str(content.get("profile", outcome.content.profile)),
            sections_included=list(extended.get("sections_included") or []),
            export_fingerprint=str(content.get("export_fingerprint", "")),
        ),
        message="Executive report generated",
    )


@router.get(
    "/{report_id}/content",
    response_model=ApiResponse[ReportContentResponse],
    summary="Get persisted Report Content Representation",
)
def get_report_content(
    organization_id: UUID,
    report_id: UUID,
    builder: ReportBuilderServiceDep,
) -> ApiResponse[ReportContentResponse]:
    content = builder.get_content_representation(organization_id, report_id)
    return success_response(
        data=ReportContentResponse(report_id=report_id, content=content),
        message="Report content retrieved",
    )


@router.get(
    "/{report_id}/export",
    summary="Export deterministic Report Content Representation serialization",
)
def export_report(
    organization_id: UUID,
    report_id: UUID,
    builder: ReportBuilderServiceDep,
    export_service: ReportExportServiceDep,
    format: str | None = Query(None, alias="format"),
):
    if format is not None and format.lower() == "pdf":
        outcome = export_service.export_pdf(organization_id, report_id)
        filename = f"report-{report_id}.pdf"
        return Response(
            content=outcome.pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "X-Export-Fingerprint": outcome.export_record.export_fingerprint,
            },
        )
    serialization = builder.export_report(organization_id, report_id)
    return success_response(
        data=ReportExportResponse(
            report_id=report_id,
            serialization=serialization,
            fingerprint=content_fingerprint(serialization),
        ),
        message="Report exported",
    )


@router.post(
    "",
    response_model=ApiResponse[ReportResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create report draft",
)
def create_report_draft(
    organization_id: UUID,
    body: ReportCreate,
    service: ReportServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[ReportResponse]:
    report = service.create_draft(
        organization_id,
        title=body.title,
        report_type=body.report_type,
        summary=body.summary,
        department_id=body.department_id,
        reporting_period_id=body.reporting_period_id,
        source_file_id=body.source_file_id,
        analysis_run_id=body.analysis_run_id,
    )
    return success_response(
        data=ReportResponse.model_validate(report),
        message="Report draft created",
    )


@router.get(
    "",
    response_model=ApiResponse[list[ReportResponse]],
    summary="List reports",
)
def list_reports(
    organization_id: UUID,
    service: ReportServiceDep,
    pagination: PaginationDep,
    report_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    department_id: UUID | None = Query(None),
    reporting_period_id: UUID | None = Query(None),
) -> ApiResponse[list[ReportResponse]]:
    reports = service.list_reports(
        organization_id,
        report_type=report_type,
        status=status_filter,
        department_id=department_id,
        reporting_period_id=reporting_period_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return success_response(
        data=[ReportResponse.model_validate(r) for r in reports],
        message="Reports retrieved",
    )


@router.get(
    "/{report_id}",
    response_model=ApiResponse[ReportResponse],
    summary="Get report by ID",
)
def get_report(
    organization_id: UUID,
    report_id: UUID,
    service: ReportServiceDep,
) -> ApiResponse[ReportResponse]:
    report = service.get_report(report_id)
    return success_response(
        data=ReportResponse.model_validate(report),
        message="Report retrieved",
    )


@router.patch(
    "/{report_id}",
    response_model=ApiResponse[ReportResponse],
    summary="Update report draft",
)
def update_report_draft(
    organization_id: UUID,
    report_id: UUID,
    body: ReportUpdate,
    service: ReportServiceDep,
    _current_user: RequireOrgExecutive,
) -> ApiResponse[ReportResponse]:
    report = service.update_draft(
        organization_id,
        report_id,
        title=body.title,
        summary=body.summary,
    )
    return success_response(
        data=ReportResponse.model_validate(report),
        message="Report draft updated",
    )


@router.post(
    "/{report_id}/publish",
    response_model=ApiResponse[ReportResponse],
    summary="Publish report",
)
def publish_report(
    organization_id: UUID,
    report_id: UUID,
    service: ReportServiceDep,
    current_user: RequireOrgExecutive,
) -> ApiResponse[ReportResponse]:
    report = service.publish_report(
        organization_id,
        report_id,
        initiating_user_id=current_user.id,
    )
    return success_response(
        data=ReportResponse.model_validate(report),
        message="Report published",
    )


@router.delete(
    "/{report_id}",
    response_model=ApiResponse[None],
    summary="Delete report",
)
def delete_report(
    organization_id: UUID,
    report_id: UUID,
    service: ReportServiceDep,
    _current_user: RequireOrgAdmin,
) -> ApiResponse[None]:
    service.delete_report(organization_id, report_id)
    return success_response(data=None, message="Report deleted")
