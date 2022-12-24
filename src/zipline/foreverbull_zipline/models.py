from datetime import datetime
from typing import List, Optional

from foreverbull_core.models.base import Base
from foreverbull_core.models.socket import SocketConfig


class Database(Base):
    user: str
    password: str
    netloc: str
    port: int
    dbname: str


class Sockets(Base):
    main: SocketConfig
    feed: SocketConfig
    broker: SocketConfig
    running: bool


class IngestConfig(Base):
    name: str
    calendar_name: str
    from_date: str
    to_date: str
    isins: List[str]
    database: Optional[Database]


class EngineConfig(Base):
    bundle: str
    calendar: str
    start_date: str
    end_date: str
    timezone: str = "utc"
    benchmark: str
    isins: List[str]


class Period(Base):
    period_open: datetime
    period_close: datetime
    shorts_count: Optional[int]
    pnl: Optional[float]
    long_value: Optional[float]
    short_value: Optional[int]
    long_exposure: Optional[float]
    starting_exposure: Optional[float]
    short_exposure: Optional[int]
    capital_used: Optional[float]
    gross_leverage: Optional[float]
    net_leverage: Optional[float]
    ending_exposure: Optional[float]
    starting_value: Optional[float]
    ending_value: Optional[float]
    starting_cash: Optional[float]
    ending_cash: Optional[float]
    returns: Optional[float]
    portfolio_value: Optional[float]
    longs_count: Optional[int]
    algo_volatility: Optional[float]
    sharpe: Optional[float]
    alpha: Optional[float]
    beta: Optional[float]
    sortino: Optional[float]
    max_drawdown: Optional[float]
    max_leverage: Optional[float]
    excess_return: Optional[int]
    treasury_period_return: Optional[int]
    benchmark_period_return: Optional[float]
    benchmark_volatility: Optional[float]
    algorithm_period_return: Optional[float]


class Result(Base):
    periods: List[Period]


class OHLC(Base):
    isin: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    time: datetime
