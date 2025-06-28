"""
Testing module for auth admin user middleware (app.main.auth_admin_user).
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import status

from app.services.auth.base import create_access_token
from app.models.admin import Admin
from app.crud.admin import admin_crud
from app.tests.api.test_admin_api import (
    mock_get_all_admin,
    mock_get_admin_by_email,
    test_admin_object,
    make_admin_obj,
)

API_ADMIN_URL = "/api/admin"
ADMIN_ROUTE_TO_TEST = "/all"


def test_auth_admin_user_middleware_not_guarded_url(client):
    """
    Test that not guarded URL works without admin user authentication.
    """
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK


def test_auth_admin_user_middleware_guarded_url_missing_authorization_header(client):
    """
    Test that guarded URL return UNAUTHORIZED status code when missing authorization header.
    """
    response = client.get(API_ADMIN_URL + ADMIN_ROUTE_TO_TEST)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing authorization header." == response.json().get("detail")


@pytest.mark.parametrize(
    "auth_header_content, expected_error_message",
    [
        ("", "Missing authorization header."),
        ("gibberish", "Invalid authorization header format."),
        ("gibberish gibberish_token", "Invalid authentication scheme."),
        ("Bearer gibberish_token", "Authentication error."),
    ],
)
def test_auth_admin_user_middleware_guarded_url_invalid_authorization_header(
    client, auth_header_content, expected_error_message
):
    """
    Test that guarded URL return UNAUTHORIZED status code when authorization header is invalid
     with(different scenarios).
    """
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": auth_header_content},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert expected_error_message == response.json().get("detail")


@patch("app.crud.admin.admin_crud.get_by_email", new_callable=AsyncMock)
@patch("app.crud.base.DBConnector.get_objects", new_callable=AsyncMock)
def test_auth_admin_user_middleware_guarded_url_valid_authorization_header(
    mock_get_all_admin, mock_get_admin_by_email, client
):
    """
    Test that middleware works properly when valid authorization header is provided.
    """
    test_token = create_access_token(test_admin_object.get("email"))
    mock_get_admin_by_email.return_value = make_admin_obj(test_admin_object)
    mock_get_all_admin.return_value = [make_admin_obj(test_admin_object)]
    
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == status.HTTP_200_OK


@patch("app.crud.admin.admin_crud.get_by_email", new_callable=AsyncMock)
def test_auth_admin_user_middleware_user_not_found(mock_get_admin_by_email, client):
    """
    Test that middleware returns authentication error when user is not found in database.
    """
    test_token = create_access_token("nonexistent@test.com")
    mock_get_admin_by_email.return_value = None
    
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication error." == response.json().get("detail")


def test_auth_admin_user_middleware_expired_token(client):
    """
    Test that middleware returns authentication error when token is expired.
    """
    import jwt
    from datetime import datetime, timedelta, timezone
    from app.core.config import settings
    
    # Create an expired token
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)  # Expired 1 minute ago
    to_encode = {"sub": test_admin_object.get("email"), "exp": expire}
    expired_token = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication error." == response.json().get("detail")


def test_auth_admin_user_middleware_malformed_token(client):
    """
    Test that middleware returns authentication error when token is malformed.
    """
    malformed_token = "invalid.jwt.token"
    
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": f"Bearer {malformed_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication error." == response.json().get("detail")


@patch("app.crud.admin.admin_crud.get_by_email", new_callable=AsyncMock)
def test_auth_admin_user_middleware_database_error(mock_get_admin_by_email, client):
    """
    Test that middleware handles database errors gracefully.
    """
    test_token = create_access_token(test_admin_object.get("email"))
    mock_get_admin_by_email.side_effect = Exception("Database connection error")
    
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": f"Bearer {test_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication error." == response.json().get("detail")


def test_auth_admin_user_middleware_case_insensitive_bearer(client):
    """
    Test that middleware works with case-insensitive Bearer scheme.
    """
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": "bearer some_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Authentication error." == response.json().get("detail")


@patch("app.crud.admin.admin_crud.get_by_email", new_callable=AsyncMock)
@patch("app.crud.base.DBConnector.get_objects", new_callable=AsyncMock)
def test_auth_admin_user_middleware_sets_request_state(
    mock_get_all_admin, mock_get_admin_by_email, client
):
    """
    Test that middleware properly sets the admin_user in request state.
    """
    test_token = create_access_token(test_admin_object.get("email"))
    mock_admin = make_admin_obj(test_admin_object)
    mock_get_admin_by_email.return_value = mock_admin
    mock_get_all_admin.return_value = [mock_admin]
    
    response = client.get(
        API_ADMIN_URL + ADMIN_ROUTE_TO_TEST,
        headers={"Authorization": f"Bearer {test_token}"},
    )
    
    # The middleware should successfully authenticate and the endpoint should work
    assert response.status_code == status.HTTP_200_OK
    # Verify that get_by_email was called with the correct email
    mock_get_admin_by_email.assert_called_once_with(test_admin_object.get("email"))


def test_auth_admin_user_middleware_multiple_paths_covered(client):
    """
    Test that middleware only affects /api/admin paths and not other admin-related paths.
    """
    # Test that /api/admin paths are protected
    response = client.get("/api/admin/all")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test that non-admin paths are not affected
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "test_path",
    [
        "/api/admin",
        "/api/admin/",
        "/api/admin/all",
        "/api/admin/123e4567-e89b-12d3-a456-426614174000",
        "/api/admin/add",
    ],
)
def test_auth_admin_user_middleware_covers_all_admin_paths(client, test_path):
    """
    Test that middleware protects all admin API paths.
    """
    response = client.get(test_path)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing authorization header." == response.json().get("detail")
