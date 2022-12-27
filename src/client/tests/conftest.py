import os
from datetime import date, datetime
from multiprocessing import get_start_method, set_start_method

import pytest
import yfinance
from foreverbull.data.data import DateManager
from foreverbull.data.stock_data import OHLC, Base
from foreverbull.models import Configuration
from foreverbull.worker import WorkerPool
from foreverbull_core.models.socket import SocketConfig
from foreverbull_core.models.worker import Database
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
def client_config(client_socket_config):
    return Configuration(
        execution_id="test",
        execution_start_date=date.today(),
        execution_end_date=date.today(),
        database=None,
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
def postgres_database():
    user = os.environ.get("POSTGRES_USER", "postgres")
    password = os.environ.get("POSTGRES_PASSWORD", "foreverbull")
    netloc = os.environ.get("POSTGRES_HOST", "localhost")
    port = os.environ.get("POSTGRES_PORT", "5433")
    dbname = os.environ.get("POSTGRES_DB", "postgres")
    return Database(user=user, password=password, netloc=netloc, port=port, dbname=dbname)


@pytest.fixture(scope="session")
def loaded_database(postgres_database: Database):
    instruments = {"US0378331005": "AAPL", "US88160R1014": "TSLA", "US5949181045": "MSFT"}
    start = "2020-01-01"
    end = "2021-12-31"

    db = postgres_database
    engine = create_engine(f"postgresql://{db.user}:{db.password}@{db.netloc}:{db.port}/{db.dbname}")
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
    return instruments


@pytest.fixture
def date_manager():
    start = datetime(2020, 1, 1)
    end = datetime(2021, 12, 31)
    date = DateManager(start, end)
    date.current = end
    return date
