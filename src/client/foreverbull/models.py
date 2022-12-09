from datetime import date, datetime
from typing import List, Optional

from foreverbull_core.models.base import Base
from foreverbull_core.models.socket import SocketConfig
from foreverbull_core.models.worker import Database, Parameter


class Configuration(Base):
    """_summary_
    Args:
        database (Database, optional): Optional[Database]
        parameters (List[Parameter], optional): Optional[List[Parameter]]
    Returns:
        Instance: instance
    """

    execution_id: str
    execution_start_date: date
    execution_end_date: date
    database: Optional[Database]
    parameters: Optional[List[Parameter]]
    socket: SocketConfig


class OHLC(Base):
    isin: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    time: datetime
