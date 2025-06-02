"""
Tests for Google OAuth authentication flow and token handling.
Validates access token response, secure cookie storage for refresh tokens,
and automatic user creation functionality.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_google_auth_returns_access_token():
    """
    Test that the Google auth endpoint returns an access token in the response body.
    This is the primary requirement of the task.
    """
    with patch("app.api.auth.google_auth") as mock_google_auth, patch(
        "app.api.auth.user_crud"
    ) as mock_user_crud:

        mock_user_data = MagicMock()
        mock_user_data.email = "test@example.com"
        mock_google_auth.get_user = AsyncMock(return_value=mock_user_data)

        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user_crud.get_object_by_field = AsyncMock(return_value=mock_user)

        response = client.get("/api/auth/google?code=test_code")

        assert response.status_code == status.HTTP_200_OK
        json_response = response.json()

        assert "access_token" in json_response
        assert isinstance(json_response["access_token"], str)
        assert len(json_response["access_token"]) > 0

        assert json_response["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_google_auth_sets_refresh_token_cookie():
    """
    Test that the Google auth endpoint sets a refresh token in a secure HTTP cookie.
    """
    with patch("app.api.auth.google_auth") as mock_google_auth, patch(
        "app.api.auth.user_crud"
    ) as mock_user_crud:

        mock_user_data = MagicMock()
        mock_user_data.email = "test@example.com"
        mock_google_auth.get_user = AsyncMock(return_value=mock_user_data)

        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user_crud.get_object_by_field = AsyncMock(return_value=mock_user)

        response = client.get("/api/auth/google?code=test_code")

        assert "refresh_token" in response.cookies

        cookie_header = response.headers.get("set-cookie", "")
        assert "refresh_token=" in cookie_header
        assert "HttpOnly" in cookie_header
        assert "Secure" in cookie_header
        assert "Path=/" in cookie_header


@pytest.mark.asyncio
async def test_google_auth_with_nonexistent_user():
    """
    Test that a new user is created if one doesn't exist.
    """
    with patch("app.api.auth.google_auth") as mock_google_auth, patch(
        "app.api.auth.user_crud"
    ) as mock_user_crud:

        mock_user_data = MagicMock()
        mock_user_data.email = "new@example.com"
        mock_google_auth.get_user = AsyncMock(return_value=mock_user_data)

        mock_user_crud.get_object_by_field = AsyncMock(return_value=None)

        created_user = MagicMock()
        created_user.id = "some-uuid"
        created_user.email = None
        mock_user_crud.create_user = AsyncMock(return_value=created_user)

        updated_user = MagicMock()
        updated_user.email = "new@example.com"
        mock_user_crud.update_user = AsyncMock(return_value=updated_user)

        response = client.get("/api/auth/google?code=test_code")

        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()

        expected_wallet_id = f"{mock_user_data.email}_wallet"
        mock_user_crud.create_user.assert_called_once_with(wallet_id=expected_wallet_id)

        mock_user_crud.update_user.assert_called_once_with(
            created_user.id, email=mock_user_data.email
        )
