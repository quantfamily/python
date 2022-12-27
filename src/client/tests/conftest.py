import os
from datetime import datetime
from multiprocessing import get_start_method, set_start_method

import pytest
import yfinance
from foreverbull.data.data import Database, DateManager
from foreverbull.data.stock_data import OHLC, Base, Portfolio, Position
from foreverbull.models import Configuration
from foreverbull.worker import WorkerPool
from foreverbull_core.models.socket import SocketConfig
from foreverbull_core.models.worker import Database as DatabaseConfig
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope="session")
def spawn_process():
    method = get_start_method()
    if method != "spawn":
        set_start_method("spawn", force=True)


@pytest.fixture
def worker_pool():
    wp = WorkerPool()
    wp.setup()
    yield wp
    wp.stop()


@pytest.fixture
def server_socket_config():
    return SocketConfig(host="127.0.0.1", port=5656, listen=True)


@pytest.fixture
def client_socket_config():
    return SocketConfig(host="127.0.0.1", port=5656, listen=False)


@pytest.fixture
def client_config(client_socket_config, database_config):
    return Configuration(
        execution_id="test",
        execution_start_date=datetime(2020, 1, 1),
        execution_end_date=datetime(2021, 12, 31),
        database=database_config,
        parameters=None,
        socket=client_socket_config,
    )


@pytest.fixture
def algo_file():
    py_code = """
import foreverbull

fb = foreverbull.Foreverbull()

@fb.on("ohlc")
def hello(*args, **kwargs):
    pass
    """
    with open("test_file.py", "w") as fw:
        fw.write(py_code)
    yield "test_file"
    os.remove("test_file.py")


@pytest.fixture(scope="session")
def date_manager():
    start = datetime(2020, 1, 1)
    end = datetime(2021, 12, 31)
    date = DateManager(start, end)
    date.current = end
    return date


@pytest.fixture(scope="session")
def instruments():
    return {"US0378331005": "AAPL", "US88160R1014": "TSLA", "US5949181045": "MSFT"}


@pytest.fixture(scope="session")
def database_config():
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "foreverbull")
    netloc = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5433")
    dbname = os.environ.get("POSTGRES_DB", "postgres")
    return DatabaseConfig(
        netloc=netloc,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
    )


@pytest.fixture(scope="session")
def loaded_database(date_manager, instruments):
    start = "2020-01-01"
    end = "2021-12-31"

    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "foreverbull")
    netloc = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5433")
    dbname = os.environ.get("POSTGRES_DB", "postgres")
    engine = create_engine(f"postgresql://{user}:{password}@{netloc}:{port}/{dbname}")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(OHLC).delete()

    for isin, symbol in instruments.items():
        ticker = yfinance.Ticker(symbol)
        history = ticker.history(start=start, end=end)
        for time, row in history.iterrows():
            ohlc = OHLC(
                isin=isin,
                time=time,
                high=row["High"],
                low=row["Low"],
                open=row["Open"],
                close=row["Close"],
                volume=row["Volume"],
            )
            session.add(ohlc)
    session.commit()
    portfolio = Portfolio(
        execution_id="test_execution",
        cash_flow=123.2,
        starting_cash=1000,
        portfolio_value=2134.2,
        pnl=32.2,
        returns=22.2,
        timestamp=datetime(2021, 12, 31),
        positions_value=222.4,
        positions_exposure=100.0,
    )
    session.add(portfolio)
    session.commit()
    session.refresh(portfolio)
    position = Position(
        portfolio_id=portfolio.id,
        isin="US0378331005",
        amount=100,
        cost_basis=100,
        last_sale_date=datetime(2021, 12, 31),
    )
    session.add(position)
    session.commit()
    return Database(
        execution_id="test_execution",
        date_manager=date_manager,
        db_conf=DatabaseConfig(
            user=user,
            password=password,
            netloc=netloc,
            port=port,
            dbname=dbname,
        ),
    )
