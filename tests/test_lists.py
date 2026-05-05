"""Tests for lists.py"""

import pytest
from unittest.mock import MagicMock, patch

import msgraphtest.lists as lists_mod


@pytest.fixture()
def env(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_SITE_ID", "site-xyz")
    monkeypatch.setenv("SHAREPOINT_LIST_ID", "list-abc")
    monkeypatch.setenv("AZURE_TENANT_ID", "tenant-id")
    monkeypatch.setenv("AZURE_CLIENT_ID", "client-id")
    monkeypatch.setenv("AZURE_CLIENT_SECRET", "client-secret")


def _mock_client(return_value=None):
    client = MagicMock()
    client.get.return_value = return_value or {}
    client.post.return_value = {"id": "42", "fields": {"Title": "New Item"}}
    client.patch.return_value = {"Title": "Updated Item"}
    return client


def test_get_list_items_returns_value(env):
    items = [{"id": "1", "fields": {"Title": "Item A"}}, {"id": "2", "fields": {"Title": "Item B"}}]
    mock_client = _mock_client(return_value={"value": items})

    with patch.object(lists_mod, "GraphClient", return_value=mock_client):
        result = lists_mod.get_list_items()

    assert result == items
    mock_client.get.assert_called_once()


def test_get_list_items_missing_site_id(monkeypatch):
    monkeypatch.delenv("SHAREPOINT_SITE_ID", raising=False)

    with patch.object(lists_mod, "GraphClient"):
        with pytest.raises(EnvironmentError, match="SHAREPOINT_SITE_ID"):
            lists_mod.get_list_items()


def test_get_list_items_missing_list_id(monkeypatch):
    monkeypatch.setenv("SHAREPOINT_SITE_ID", "site-xyz")
    monkeypatch.delenv("SHAREPOINT_LIST_ID", raising=False)

    with patch.object(lists_mod, "GraphClient"):
        with pytest.raises(EnvironmentError, match="SHAREPOINT_LIST_ID"):
            lists_mod.get_list_items()


def test_create_list_item(env):
    mock_client = _mock_client()

    with patch.object(lists_mod, "GraphClient", return_value=mock_client):
        result = lists_mod.create_list_item({"Title": "New Item", "Status": "Active"})

    mock_client.post.assert_called_once()
    assert result["id"] == "42"


def test_update_list_item(env):
    mock_client = _mock_client()

    with patch.object(lists_mod, "GraphClient", return_value=mock_client):
        result = lists_mod.update_list_item("42", {"Status": "Closed"})

    mock_client.patch.assert_called_once()
    assert result["Title"] == "Updated Item"
