"""
Pytest-based asynchronous database tests for CRUD operations.

This module defines test cases for verifying the functionality of the database
operations using SQLAlchemy and an async database connection. It includes
fixtures to set up and tear down test environments, as well as tests for
creating, retrieving, updating, and deleting objects in the database.
"""

from collections.abc import Sequence
from datetime import datetime, timedelta
import random
import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.user import UserCRUD
from app.models.user import User
from app.tests.conftest import fake
from app.tests.test_crud_user import user_crud  # noqa

from app.schemas.pools import PoolResponse
import pytest

from app.crud.pool import PoolCRUD, UserPoolCRUD
from app.models.pool import Pool, PoolRiskStatus, PoolStatisticDBView, UserPool


@pytest.fixture
def mock_db_session():
    """Creates a fully mocked async database session that supports async context management."""
    session = AsyncMock()

    session.__aenter__.return_value = session
    session.__aexit__.return_value = None

    session.execute = AsyncMock()
    session.add = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.get = AsyncMock(return_value=None)

    return session


@pytest.fixture
def pool_crud(mock_db_session):
    """Creates an instance of PoolCRUD with a mocked async database session."""
    crud = PoolCRUD(Pool)
    crud.session = MagicMock(return_value=mock_db_session)
    return crud


@pytest.fixture
def user_pool_crud(mock_db_session):
    """Creates an instance of UserPoolCRUD with a mocked async database session."""
    crud = UserPoolCRUD(UserPool)
    crud.session = MagicMock(return_value=mock_db_session)
    return crud


@pytest.mark.asyncio
async def test_create_pool_debug(pool_crud, mock_db_session):
    """Debug test for create_pool to check session calls."""
    token = "BTC"
    risk_status = PoolRiskStatus.LOW

    mock_session_instance = AsyncMock()
    mock_session_instance.add = MagicMock()
    mock_session_instance.commit = AsyncMock()
    mock_session_instance.refresh = AsyncMock()
    mock_session_instance.merge = AsyncMock()

    pool_crud.session = MagicMock(return_value=mock_session_instance)

    result = await pool_crud.create_pool(token, risk_status)

    assert result is not None


@pytest.mark.asyncio
async def test_create_pool(pool_crud, mock_db_session):
    """Test creating a pool."""
    token = "BTC"
    risk_status = PoolRiskStatus.LOW

    pool = Pool(token=token, risk_status=risk_status)

    mock_session_instance = AsyncMock()
    mock_session_instance.commit = AsyncMock()
    mock_session_instance.refresh = AsyncMock()
    mock_session_instance.merge = AsyncMock(return_value=pool)

    mock_db_session.__aenter__.return_value = mock_session_instance
    pool_crud.session = MagicMock(return_value=mock_db_session)

    result = await pool_crud.create_pool(token, risk_status)

    assert result is not None
    assert result.token == token
    assert result.risk_status == risk_status

    mock_session_instance.merge.assert_called_once()
    mock_session_instance.commit.assert_called_once()
    mock_session_instance.refresh.assert_called_once_with(pool)


@pytest.mark.asyncio
async def test_get_all_pools(pool_crud, mock_db_session):
    """Test retrieving all pools."""
    pools = [
        PoolResponse(id=str(uuid.uuid4()), token="BTC", risk_status=PoolRiskStatus.LOW),
        PoolResponse(
            id=str(uuid.uuid4()), token="ETH", risk_status=PoolRiskStatus.HIGH
        ),
    ]
    total = 2

    with patch.object(
        pool_crud, "get_objects", new_callable=AsyncMock
    ) as mock_get_objects:
        with patch.object(
            pool_crud, "get_objects_amounts", new_callable=AsyncMock
        ) as mock_get_amounts:
            mock_get_objects.return_value = pools
            mock_get_amounts.return_value = total

            result = await pool_crud.get_objects(limit=None, offset=None)
            count = await pool_crud.get_objects_amounts()

            assert result == pools
            assert count == total
            mock_get_objects.assert_called_once()
            mock_get_amounts.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_pools_empty(pool_crud, mock_db_session):
    """Test retrieving all pools when there are no pools."""
    pools = []
    total = 0

    with patch.object(
        pool_crud, "get_objects", new_callable=AsyncMock
    ) as mock_get_objects:
        with patch.object(
            pool_crud, "get_objects_amounts", new_callable=AsyncMock
        ) as mock_get_amounts:
            mock_get_objects.return_value = pools
            mock_get_amounts.return_value = total

            result = await pool_crud.get_objects(limit=None, offset=None)
            count = await pool_crud.get_objects_amounts()

            assert result == []
            assert count == 0
            mock_get_objects.assert_called_once()
            mock_get_amounts.assert_called_once()


@pytest.mark.asyncio
async def test_get_all_pools_with_internal_exception(pool_crud, mock_db_session):
    """Test retrieving all pools when there is an internal exception."""
    with patch.object(
        pool_crud, "get_objects", new_callable=AsyncMock
    ) as mock_get_objects:
        mock_get_objects.side_effect = Exception("Internal error")

        with pytest.raises(Exception):
            await pool_crud.get_objects()


@pytest.mark.asyncio
async def test_create_user_pool(user_pool_crud, mock_db_session):
    """Test creating a user pool entry."""
    user_id = uuid.uuid4()
    pool_id = uuid.uuid4()
    amount = Decimal("1000.50")

    mock_db_session.add = AsyncMock()
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    result = await user_pool_crud.create_user_pool(user_id, pool_id, amount)

    assert result.user_id == user_id
    assert result.pool_id == pool_id
    assert result.amount == amount
    mock_db_session.add.assert_called_once_with(result)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_update_user_pool(user_pool_crud, mock_db_session):
    """Test updating an existing user pool."""
    user_pool_id = uuid.uuid4()
    new_amount = Decimal("1500.75")

    existing_user_pool = UserPool(
        user_id=uuid.uuid4(), pool_id=uuid.uuid4(), amount=Decimal("1000")
    )
    existing_user_pool.id = user_pool_id

    mock_db_session.get = AsyncMock(return_value=existing_user_pool)
    mock_db_session.commit = AsyncMock()
    mock_db_session.refresh = AsyncMock()

    result = await user_pool_crud.update_user_pool(user_pool_id, amount=new_amount)

    assert result is not None
    assert result.amount == new_amount
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(result)


@pytest.mark.asyncio
async def test_update_user_pool_not_found(user_pool_crud, mock_db_session):
    """Test updating a user pool that does not exist."""
    user_pool_id = uuid.uuid4()
    mock_db_session.get = AsyncMock(return_value=None)

    result = await user_pool_crud.update_user_pool(user_pool_id, amount=Decimal("2000"))

    assert result is None
    mock_db_session.get.assert_called_once_with(UserPool, user_pool_id)


@pytest.mark.asyncio
async def test_fetch_all_with_amount_delta(pool_crud, mock_db_session):
    """Test fetching all pools with total amount of user pools and calculated delta"""
    expected_res = [
        (
            Pool(id=uuid.uuid4(), token="BTC", risk_status=PoolRiskStatus.LOW),
            Decimal(123),
            Decimal(456),
        ),
        (
            Pool(id=uuid.uuid4(), token="ETH", risk_status=PoolRiskStatus.HIGH),
            Decimal(789),
            Decimal(123456),
        ),
    ]
    mock_res_all = Mock(return_value=expected_res)
    mock_db_session.execute.return_value.all = mock_res_all
    res = await pool_crud.fetch_all_with_amount_delta(timedelta(hours=5))
    assert res == expected_res
    mock_res_all.assert_called_once()
    mock_db_session.execute.assert_awaited_once()


@pytest_asyncio.fixture
async def test_user(user_crud: UserCRUD):
    """
    Fixture to create test user using user_crud as another fixture
    Deletes created user on test teardown
    """
    user = await user_crud.write_to_db(User(wallet_id=str(uuid.uuid4())))
    yield user
    await user_crud.delete_object(user)


@pytest_asyncio.fixture
async def new_mock_pools_with_session(pool_crud: PoolCRUD, test_user: User):
    """
    Fixture to create a set of test pools with associated user pools
    Rollbacks session after on teardown to clear changes
    """
    mock_pools = [
        Pool(
            token=fake.cryptocurrency_code(),
            risk_status=random.choice(list(PoolRiskStatus)),
            user_pools=sorted(
                [
                    UserPool(
                        user_id=test_user.id,
                        amount=Decimal(fake.random_int(1000, 10000)),
                        created_at=datetime.now()
                        - timedelta(
                            hours=random.choice(
                                [0, 23, 47, 71, random.randint(72, 1000)]
                            )
                        ),
                    )
                    for _ in range(10)
                ],
                key=lambda p: p.created_at,
                reverse=True,
            ),
        )
        for _ in range(10)
    ]
    async with pool_crud.session_maker() as session:
        session.add_all(mock_pools)
        await session.flush()
        yield mock_pools, session
        await session.rollback()


def _find_earliest_amount(user_pools: Sequence[UserPool], within_delta_hours: int):
    """
    Finds earliest user pool's amount within supplied amount of hours.
    Assumes that user_pools are sorted by created_at in desc order
    """
    earliest_up = user_pools[0]
    for up in user_pools[1:]:
        if (
            up.created_at >= datetime.now() - timedelta(hours=within_delta_hours)
        ) and up.created_at < earliest_up.created_at:
            earliest_up = up
    return earliest_up.amount


@pytest.mark.asyncio
async def test_pool_statistic_view(
    new_mock_pools_with_session: tuple[Sequence[Pool], AsyncSession],
):
    """Test fetching all from PoolStatisticDBView"""
    mock_pools, session = new_mock_pools_with_session
    res = await session.execute(select(PoolStatisticDBView))
    retrieved_pools: Sequence[PoolStatisticDBView] = res.scalars().all()
    pools_by_id = {pool.id: pool for pool in mock_pools}
    for pool in retrieved_pools:
        expected_pool = pools_by_id[pool.id]
        assert pool.token == expected_pool.token
        latest_amount = expected_pool.user_pools[0].amount
        assert latest_amount - expected_pool.user_pools[-1].amount == pool.volume
        assert (
            latest_amount - _find_earliest_amount(expected_pool.user_pools, 24)
            == pool.volume_24
        )
        assert (
            latest_amount - _find_earliest_amount(expected_pool.user_pools, 48)
            == pool.volume_48
        )
        assert (
            latest_amount - _find_earliest_amount(expected_pool.user_pools, 72)
            == pool.volume_72
        )
