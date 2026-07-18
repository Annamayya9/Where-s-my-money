from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

import requests


class SplitwiseClient:
    BASE_URL = "https://secure.splitwise.com/api/v3.0"

    def __init__(self, access_token: str) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }
        )

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.session.get(f"{self.BASE_URL}{path}", params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_current_user_id(self) -> int:
        payload = self._get("/get_current_user")
        return int(payload["user"]["id"])

    def get_expenses_for_date_range(
        self,
        start_date: date,
        end_date_exclusive: date,
        page_size: int = 100,
    ) -> list[dict[str, Any]]:
        expenses: list[dict[str, Any]] = []
        offset = 0

        while True:
            payload = self._get(
                "/get_expenses",
                params={
                    "dated_after": start_date.isoformat(),
                    "dated_before": end_date_exclusive.isoformat(),
                    "limit": page_size,
                    "offset": offset,
                },
            )

            page = payload.get("expenses", [])
            expenses.extend(page)

            if len(page) < page_size:
                break

            offset += page_size

        return expenses


def as_decimal(value: Any) -> Decimal:
    if value is None or value == "":
        return Decimal("0")
    return Decimal(str(value))
