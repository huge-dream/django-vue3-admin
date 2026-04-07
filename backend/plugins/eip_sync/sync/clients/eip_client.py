from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from django.conf import settings


class EipClient:
    """HTTP client for PIS -> EIP outbound calls (placeholder for future use)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        self.base_url = (base_url or getattr(settings, "EIP_BASE_URL", "") or "").rstrip("/")
        self.api_key = api_key or getattr(settings, "EIP_API_KEY", "") or ""
        self.timeout = timeout
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update(
                {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                }
            )

    def post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"Status": "fail", "Message": str(e)}

    def get(self, endpoint: str, params: Dict[str, Any] | None = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params or {}, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"Status": "fail", "Message": str(e)}
