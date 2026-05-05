"""
graph_client.py — Thin wrapper around the Microsoft Graph REST API.

Provides a GraphClient class that handles authentication and makes
authenticated HTTP requests to the Graph API endpoint.
"""

from __future__ import annotations

import requests

from msgraphtest.auth import get_access_token

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphClient:
    """Minimal Microsoft Graph API client (client credentials)."""

    def __init__(self) -> None:
        self._token: str = get_access_token()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            }
        )

    def get(self, path: str, **kwargs) -> dict:
        url = f"{GRAPH_BASE_URL}{path}"
        response = self._session.get(url, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, json: dict, **kwargs) -> dict:
        url = f"{GRAPH_BASE_URL}{path}"
        response = self._session.post(url, json=json, **kwargs)
        response.raise_for_status()
        return response.json()

    def patch(self, path: str, json: dict, **kwargs) -> dict:
        url = f"{GRAPH_BASE_URL}{path}"
        response = self._session.patch(url, json=json, **kwargs)
        response.raise_for_status()
        return response.json()

    def put_bytes(self, path: str, data: bytes, content_type: str = "application/octet-stream", **kwargs) -> dict:
        url = f"{GRAPH_BASE_URL}{path}"
        headers = {"Content-Type": content_type}
        response = self._session.put(url, data=data, headers=headers, **kwargs)
        response.raise_for_status()
        return response.json()

    def get_raw(self, path: str, **kwargs) -> bytes:
        url = f"{GRAPH_BASE_URL}{path}"
        response = self._session.get(url, **kwargs)
        response.raise_for_status()
        return response.content
