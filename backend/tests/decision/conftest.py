"""Shared fixtures for waste decision tests."""

from __future__ import annotations

import pytest

from app.business.bootstrap import initialize_business_engines


@pytest.fixture
def business_engines_initialized() -> None:
    initialize_business_engines()


def sample_waste_payload(*, include_second_sheet: bool = False) -> dict:
    sheet = {
        "name": "WasteData",
        "columns": ["category", "amount", "total_spend"],
        "rows": [
            {
                "row_number": 2,
                "values": {
                    "category": "overlapping_contracts",
                    "amount": "745000",
                    "total_spend": "50000000",
                },
            },
            {
                "row_number": 3,
                "values": {
                    "category": "operations",
                    "amount": "520000",
                    "total_spend": "50000000",
                },
            },
            {
                "row_number": 4,
                "values": {
                    "category": "finance",
                    "amount": "1075000",
                    "total_spend": "50000000",
                },
            },
        ],
    }
    sheets = [sheet]
    if include_second_sheet:
        sheets.append(
            {
                "name": "OtherWaste",
                "columns": ["category", "amount", "total_spend"],
                "rows": [
                    {
                        "row_number": 2,
                        "values": {
                            "category": "travel",
                            "amount": "100",
                            "total_spend": "10000",
                        },
                    }
                ],
            }
        )
    return {"source_file_name": "Procurement_Q2.xlsx", "sheets": sheets}
