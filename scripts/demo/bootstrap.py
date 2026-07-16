#!/usr/bin/env python3
"""Bootstrap demo organization, user, scenarios, and settings for hackathon."""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[2] / "backend"
sys.path.insert(0, str(BACKEND_ROOT))


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file(BACKEND_ROOT / ".env")

from app.business.bootstrap import initialize_business_engines  # noqa: E402
from app.db.models.enums import UserRole  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.repositories import (  # noqa: E402
    OrganizationRepository,
    SettingsRepository,
    SimulationRepository,
    UserRepository,
)
from app.services.exceptions import DuplicateResourceError, InvalidStateError  # noqa: E402
from app.services.organization import OrganizationService  # noqa: E402
from app.services.simulation import SimulationService  # noqa: E402
from app.services.user import UserService  # noqa: E402
from app.settings.service import SettingsService  # noqa: E402

DEMO_ORG_NAME = "مجموعة النخبة القابضة"
DEMO_PLATFORM = "خزينة"
DEMO_EXEC_TITLE = "الرئيس التنفيذي للشؤون المالية"
DEMO_EMAIL = "demo@khazina.sa"
DEMO_PASSWORD = "DemoExec2026!"
DEMO_FULL_NAME = "المستخدم التجريبي التنفيذي"
REPORTING_LABEL = "الربع الثاني 2026"

# Sprint 5: AI-native simulation — no hardcoded preset scenarios.
SCENARIOS: list[dict] = []


def _build_services(session):
    org_repo = OrganizationRepository(session)
    user_repo = UserRepository(session)
    simulation_repo = SimulationRepository(session)
    settings_repo = SettingsRepository(session)
    analysis_repo = __import__(
        "app.repositories", fromlist=["AnalysisRepository"]
    ).AnalysisRepository(session)
    return {
        "org": OrganizationService(session, org_repo),
        "user": UserService(session, user_repo, org_repo),
        "simulation": SimulationService(
            session, simulation_repo, analysis_repo, org_repo
        ),
        "settings": SettingsService(session, settings_repo, org_repo),
        "user_repo": user_repo,
        "org_repo": org_repo,
    }


def main() -> int:
    initialize_business_engines()
    session = SessionLocal()
    try:
        services = _build_services(session)
        org_service = services["org"]
        user_service = services["user"]
        simulation_service = services["simulation"]
        settings_service = services["settings"]
        user_repo = services["user_repo"]

        try:
            org = org_service.get_active_organization()
            print(f"Active organization exists: {org.name} ({org.id})")
        except InvalidStateError:
            org = org_service.create_organization(
                name=DEMO_ORG_NAME,
                platform_name=DEMO_PLATFORM,
                executive_title=DEMO_EXEC_TITLE,
            )
            print(f"Created organization: {org.name} ({org.id})")

        if user_repo.get_by_email(DEMO_EMAIL) is None:
            user_service.create_user(
                org.id,
                full_name=DEMO_FULL_NAME,
                email=DEMO_EMAIL,
                password=DEMO_PASSWORD,
                role=UserRole.EXECUTIVE,
            )
            print(f"Created demo user: {DEMO_EMAIL}")
        else:
            print(f"Demo user already exists: {DEMO_EMAIL}")

        periods = org_service.list_reporting_periods(org.id)
        if not periods:
            period = org_service.create_reporting_period(
                org.id,
                label=REPORTING_LABEL,
                start_date=date(2026, 4, 1),
                end_date=date(2026, 6, 30),
                activate=True,
            )
            print(f"Created reporting period: {period.label}")
        else:
            print(f"Reporting periods present: {len(periods)}")

        existing = simulation_service.list_scenarios(org.id)
        existing_names = {scenario.name for scenario in existing}
        for scenario in SCENARIOS:
            if scenario["name"] in existing_names:
                continue
            created = simulation_service.create_scenario(
                org.id,
                name=scenario["name"],
                description=scenario["description"],
                assumptions=scenario["assumptions"],
            )
            print(f"Created scenario: {created.name} ({created.id})")

        try:
            settings_service.patch_settings(
                org.id,
                {
                    "report_preferences": {
                        "pdf_export_enabled": True,
                        "auto_publish_on_generate": True,
                    }
                },
            )
            print("Settings patched: PDF export enabled")
        except Exception as exc:  # noqa: BLE001
            print(f"Settings patch skipped (defaults apply): {exc}")

        print("\nDemo bootstrap complete.")
        print(f"  Email:    {DEMO_EMAIL}")
        print(f"  Password: {DEMO_PASSWORD}")
        print(f"  Org ID:   {org.id}")
        return 0
    except DuplicateResourceError as exc:
        print(f"Bootstrap skipped: {exc}", file=sys.stderr)
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    raise SystemExit(main())
