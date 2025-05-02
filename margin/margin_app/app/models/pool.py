"""
This module contains the Pool and UserPool models.
"""

from datetime import timedelta
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
    def _get_amount_delta_stmt(
        cls, label: str | None = None, within_hours: int | None = None
    ):
        stmt = sa.func.coalesce(
            sa.func.first_value(UserPool.amount)
            .over(partition_by=UserPool.pool_id, order_by=UserPool.created_at.desc())
            .label("latest_amount")
            - sa.func.first_value(UserPool.amount)
            .over(
                partition_by=UserPool.pool_id,
                order_by=UserPool.created_at.asc(),
                range_=(
                    RangeInterval(timedelta(hours=within_hours))
                    if within_hours
                    else None,
                    None,
                ),
            )
            .label("earliest_amount"),
            0,
        )
        if label:
            stmt = stmt.label(label)
        return stmt

    @classmethod
    def build(cls):
        """Public method to build final query"""
        volumes_subq = aliased(
            sa.select(
                UserPool.pool_id,
                cls._get_amount_delta_stmt("volume"),
                cls._get_amount_delta_stmt("volume_24", 24),
                cls._get_amount_delta_stmt("volume_48", 48),
                cls._get_amount_delta_stmt("volume_72", 72),
            )
            .distinct(UserPool.pool_id)
            .order_by(UserPool.pool_id, UserPool.created_at.desc())
            .subquery()
        )
        return (
            sa.select(
                Pool.id,
                Pool.token,
                volumes_subq.c.volume,
                volumes_subq.c.volume_24,
                volumes_subq.c.volume_48,
                volumes_subq.c.volume_72,
            )
            .select_from(Pool)
            .outerjoin(volumes_subq, volumes_subq.c.pool_id == Pool.id)
        )


class PoolStatisticDBView(Base):
    """Orm model for view. Manually creates underlying Table object as database view"""

    __table__ = create_view(
        "pool_statistic_view",
        Base.metadata,
        _PoolStatisticViewQueryBuilder.build(),
    )
