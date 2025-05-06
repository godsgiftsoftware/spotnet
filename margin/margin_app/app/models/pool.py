"""
This module contains the Pool and UserPool models.
"""

from datetime import UTC, datetime, timedelta
import uuid
from decimal import Decimal
from enum import Enum
from typing import List

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, aliased, mapped_column, relationship

from app.db.extensions import RangeInterval
from app.db.extensions import create_view

from .base import Base, BaseModel


class PoolRiskStatus(Enum):
    """PoolRiskStatus Enum"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Pool(BaseModel):
    """
    Represents a pool in the application.
    """

    __tablename__ = "pool"

    token: Mapped[str] = mapped_column(sa.String, nullable=False)
    risk_status: Mapped[PoolRiskStatus] = mapped_column(
        sa.Enum(
            PoolRiskStatus,
            name="pool_risk_status",
            values_callable=lambda obj: [e.value for e in obj],
        )
    )
    user_pools: Mapped[List["UserPool"]] = relationship(back_populates="pool")

    def __repr__(self) -> str:
        """
        Returns a string representation of the Pool object.
        """
        return f"<Pool(id={self.id}, token={self.token})>"


class UserPool(BaseModel):
    """
    Represents a user's participation in a pool.
    This acts as an association table between users and pools,
    and stores additional information about the user's participation.
    """

    __tablename__ = "user_pool"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("user.id"), nullable=False
    )
    pool_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), sa.ForeignKey("pool.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(nullable=False)
    pool: Mapped["Pool"] = relationship(back_populates="user_pools", lazy="selectin")

    def __repr__(self) -> str:
        """
        Returns a string representation of the UserPool object.
        """
        return (
            f"<UserPool(id={self.id}, user_id={self.user_id}, pool_id={self.pool_id}, "
            f"token={self.pool.token}, amount={self.amount})>"
        )


class _PoolStatisticViewQueryBuilder:
    """
    Class used to create query for PoolStatisticDBView by decomposing statement
    into smaller pieces and collecting together in build function
    """

    @classmethod
    def _get_earliest_amount_stmt(cls, for_interval: RangeInterval | None = None):
        return sa.func.first_value(UserPool.amount).over(
            partition_by=UserPool.pool_id,
            order_by=UserPool.created_at.asc(),
            range_=(for_interval, None),
        )

    @classmethod
    def _get_first_amount_stmt(cls, *, within_hours: int):
        stmt = sa.func.coalesce(
            sa.Grouping(
                sa.func.array_agg(UserPool.amount)
                .filter(
                    UserPool.created_at
                    >= datetime.now(UTC) - timedelta(hours=within_hours)
                )
                .over(
                    partition_by=UserPool.pool_id,
                    order_by=UserPool.created_at,
                    range_=(None, None),
                )
            )[1],  # in postgres array indices start from 1
            0,
        )
        return stmt

    @classmethod
    def build(cls):
        """Public method to build final query"""
        volumes_subq = aliased(
            sa.select(
                UserPool.pool_id,
                UserPool.created_at,
                UserPool.amount,
                sa.func.first_value(UserPool.amount)
                .over(
                    partition_by=UserPool.pool_id,
                    order_by=UserPool.created_at.desc(),
                )
                .label("latest_amount"),
                sa.func.first_value(UserPool.amount)
                .over(
                    partition_by=UserPool.pool_id,
                    order_by=UserPool.created_at.asc(),
                )
                .label("oldest_amount"),
                cls._get_first_amount_stmt(within_hours=24).label("amount_24"),
                cls._get_first_amount_stmt(within_hours=48).label("amount_48"),
                cls._get_first_amount_stmt(within_hours=72).label("amount_72"),
            ).subquery()
        )
        return (
            sa.select(
                Pool.id,
                Pool.token,
                (volumes_subq.c.latest_amount - volumes_subq.c.oldest_amount).label(
                    "volume"
                ),
                (volumes_subq.c.latest_amount - volumes_subq.c.amount_24).label(
                    "volume_24"
                ),
                (volumes_subq.c.latest_amount - volumes_subq.c.amount_48).label(
                    "volume_48"
                ),
                (volumes_subq.c.latest_amount - volumes_subq.c.amount_72).label(
                    "volume_72"
                ),
            )
            .distinct(volumes_subq.c.pool_id)
            .select_from(Pool)
            .outerjoin(volumes_subq, volumes_subq.c.pool_id == Pool.id)
            .order_by(volumes_subq.c.pool_id, volumes_subq.c.created_at.desc())
        )


class PoolStatisticDBView(Base):
    """Orm model for view. Manually creates underlying Table object as database view"""

    __table__ = create_view(
        "pool_statistic_view",
        Base.metadata,
        _PoolStatisticViewQueryBuilder.build(),
    )
