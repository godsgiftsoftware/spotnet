"""
Tests for dashboard API endpoints.
"""

import pytest
from http import HTTPStatus
from unittest.mock import AsyncMock, patch

DASHBOARD_URL = "api/dashboard"

@pytest.mark.asyncio
@patch("app.api.dashboard.user_crud.get_objects_amounts", new_callable=AsyncMock)
@patch("app.api.dashboard.margin_position_crud.get_opened_positions_amount", new_callable=AsyncMock)
@patch(
    "app.api.dashboard.margin_position_crud.get_liquidated_positions_amount", new_callable=AsyncMock
)
@patch("app.api.dashboard.order_crud.get_objects_amounts", new_callable=AsyncMock)
def test_get_statistic_success(
    mock_get_orders,
    mock_get_liquidated_positions,
    mock_get_opened_positions, 
    mock_get_users, 
    client
):
    """
    Test successful retrieval of dashboard statistics.
    """
    
    mock_get_users.return_value = 10
    mock_get_opened_positions.return_value = 5
    mock_get_liquidated_positions.return_value = 2
    mock_get_orders.return_value = 15

    response = client.get(f"{DASHBOARD_URL}/statistic")

    assert response.status_code == HTTPStatus.OK
    data = response.json()

    assert data["users"] == 10
    assert data["opened_positions"] == 5
    assert data["liquidated_positions"] == 2
    assert data["opened_orders"] == 15


@pytest.mark.asyncio
@patch("app.api.dashboard.user_crud.get_objects_amounts", new_callable=AsyncMock)
@patch("app.api.dashboard.margin_position_crud.get_opened_positions_amount", new_callable=AsyncMock)
@patch(
    "app.api.dashboard.margin_position_crud.get_liquidated_positions_amount", new_callable=AsyncMock
)
@patch("app.api.dashboard.order_crud.get_objects_amounts", new_callable=AsyncMock)
def test_get_statistic_internal_server_error(
    mock_get_orders,
    mock_get_liquidated_positions,
    mock_get_opened_positions,
    mock_get_users,
    client
):
    """
    Test error handling when fetching dashboard statistics fails.
    """

    mock_get_users.side_effect = Exception("Database error")

    response = client.get(f"{DASHBOARD_URL}/statistic")

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert response.json()["detail"] == "Failed to get statistic."