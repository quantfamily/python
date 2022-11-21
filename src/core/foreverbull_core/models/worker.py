from typing import List, NamedTuple, Optional

from foreverbull_core.models.base import Base


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


class Parameter(Base):
    """_summary_

    Args:
        key (str): str
        value (value, optional): Optional[int]
        default (int): int

    Returns:
        Parameter: parameter
    """

    key: str
    value: Optional[int]
    default: int


class Instance(Base):
    """_summary_

    Args:
        session_id (str): str
        database (Database, optional): Optional[Database]
        parameters (List[Parameter], optional): Optional[List[Parameter]]

    Returns:
        Instance: instance
    """

    session_id: str
    database: Optional[Database]
    parameters: Optional[List[Parameter]]


class Config(Base):
    """_summary_

    Args:
        id (str, optional): Optional[str]
        service_id (str, optional): Optional[str]
        name (str): str
        parameters (List[Parameter], optional): Optional[List[Parameter]]

    Returns:
        Config: config
    """

    id: Optional[str]
    service_id: Optional[str]
    name: str
    parameters: Optional[List[Parameter]]


class Run(NamedTuple):
    """_summary_

    Args:
        broker_url (str): str = ""
        local_host (str): str = ""

    Returns:
        Run: run
    """

    broker_url: str = ""
    local_host: str = ""


class BacktestRun(Run):
    """_summary_

    Args:
        service_id (str): str = ""
        instance_id (str): str =

    Returns:
        BacktestRun:
    """

    service_id: str = ""
    instance_id: str = ""


class TestRun(NamedTuple):
    """_summary_

    Args:
        NamedTuple (_type_): _description_
    """

    broker_url: str = ""
    local_host: str = ""
    backtest_id: str = ""
