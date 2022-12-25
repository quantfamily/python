from datetime import datetime
from enum import IntEnum
from typing import List, Optional

from foreverbull_core.models.base import Base


class Instrument(Base):
    isin: str
    symbol: str
    exchange: str
    name: str


class OrderStatus(IntEnum):
    OPEN = 0
    FILLED = 1
    CANCELLED = 2
    REJECTED = 3
    HELD = 4


class Order(Base):
    id: Optional[str]
    isin: Optional[str]
    amount: Optional[int]
    filled: Optional[int]
    commission: Optional[int]
    limit_price: Optional[int]
    stop_price: Optional[int]
    current_date: Optional[str]
    created_date: Optional[str]
    status: Optional[OrderStatus]

    @classmethod
    def from_zipline(cls, order):
        return cls(
            id=order.id,
            isin=order.sid.symbol,
            amount=order.amount,
            filled=order.filled,
            commission=order.commission,
            limit_price=order.limit,
            stop_price=order.stop,
            current_date=order.dt.isoformat(),
            created_date=order.created.isoformat(),
            status=order.status,
        )


class Position(Base):
    isin: str
    amount: int
    cost_basis: float
    last_sale_price: float
    last_sale_date: str


class Portfolio(Base):
    cash_flow: float
    starting_cash: int
    portfolio_value: float
    pnl: float
    returns: float
    cash: float
    positions: List[Position]
    start_date: str
    current_date: str
    positions_value: float
    positions_exposure: float

    @classmethod
    def from_zipline_backtest(cls, backtest, current_date: datetime):
        positions = []
        for _, pos in backtest.positions.items():
            position = Position(
                isin=pos.sid.symbol,
                amount=pos.amount,
                cost_basis=pos.cost_basis,
                last_sale_price=pos.last_sale_price,
                last_sale_date=pos.last_sale_date.isoformat(),
            )
            positions.append(position)
        portfolio = Portfolio(
            cash_flow=backtest.cash_flow,
            starting_cash=backtest.starting_cash,
            portfolio_value=backtest.portfolio_value,
            pnl=backtest.pnl,
            returns=backtest.returns,
            cash=backtest.cash,
            positions=positions,
            start_date=backtest.start_date.isoformat(),
            current_date=current_date.isoformat(),
            positions_value=backtest.positions_value,
            positions_exposure=backtest.positions_exposure,
        )
        return portfolio
