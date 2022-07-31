from datetime import datetime
from typing import List, Optional

from foreverbull_core.models.base import Base
from foreverbull_core.models.socket import SocketConfig
from pydantic import validator


class Database(Base):
    """_summary_

    Args:
        user (str): str
        password (str): str
        netloc (str): str
        port (int): int
        dbname (str): str

    Returns:
        Database: database
    """

    user: str
    password: str
    netloc: str
    port: int
    dbname: str


class Sockets(Base):
    """_summary_

    Args:
        main (SocketConfig): Configuration for the backtest engine main socket
        feed (SocketConfig): Configuration for the backtest engine feed socket
        broker (SocketConfig): Configuration for the backtest engine broker socket
        running (bool): If the engine is running or not

    Returns:
        Sockets: Pydantic Sockets object
    """

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
    """_summary_

    Args:
        start_date (str): From when the backtest engine shall start feeding data
        end_date (str): To when the backtest engine shall stop feeding data, and end.
        timezone (str): Which timezone the backtest engine should simulate as
        benchmark (str): Index or asset that should be benchmark for performance
        isins (List[str]): Number of asset symbols that should be included in the simulation

    Returns:
        EngineConfig:
    """

    bundle: str
    calendar: str
    start_date: str
    end_date: str
    timezone: str = "utc"
    benchmark: str
    isins: List[str]


class Period(Base):
    """_summary_

    Args:
        period_open (str): str
        period_close (str): str
        shorts_count (int): Optional[int]
        pnl (float, optional): Optional[float]
        long_value (float, optional): Optional[float]
        short_value (int): Optional[int]
        long_exposure (float, optional): Optional[float]
        starting_exposure (float, optional): Optional[float]
        short_exposure (int): Optional[int]
        capital_used (float, optional): Optional[float]
        gross_leverage (float, optional): Optional[float]
        net_leverage (float, optional): Optional[float]
        ending_exposure (float, optional): Optional[float]
        starting_value (float, optional): Optional[float]
        ending_value (float, optional): Optional[float]
        starting_cash (float, optional): Optional[float]
        ending_cash (float, optional): Optional[float]
        returns (float, optional): Optional[float]
        portfolio_value (float, optional): Optional[float]
        longs_count (int): Optional[int]
        algo_volatility (float, optional): Optional[float]
        sharpe (float, optional): Optional[float]
        alpha (float, optional): Optional[float]
        beta (float, optional): Optional[float]
        sortino (float, optional): Optional[float]
        max_drawdown (float, optional): Optional[float]
        max_leverage (float, optional): Optional[float]
        excess_return (int): Optional[int]
        treasury_period_return (int): Optional[int]
        trading_days (int): Optional[int]
        benchmark_period_return (float, optional): Optional[float]
        benchmark_volatility (float, optional): Optional[float]
        algorithm_period_return (float, optional): Optional[float]

    Returns:
        Period: _description_
    """

    period_open: str
    period_close: str
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
    trading_days: Optional[int]
    benchmark_period_return: Optional[float]
    benchmark_volatility: Optional[float]
    algorithm_period_return: Optional[float]

    @validator("period_open", pre=True)
    def period_open_to_isodate(cls, v):
        if type(v) is datetime:
            return v.isoformat()
        return v

    @validator("period_close", pre=True)
    def period_close_to_isodate(cls, v):
        if type(v) is datetime:
            return v.isoformat()
        return v


class Result(Base):
    """_summary_

    Args:
        periods (List[Period]): _description_

    Returns:
        Result:
    """

    periods: List[Period]


class OHLC(Base):
    isin: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    time: datetime
