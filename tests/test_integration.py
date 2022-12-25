import os
from datetime import date
from typing import Iterator

import pynng
import pytest
import yfinance
from foreverbull.foreverbull import Foreverbull
from foreverbull.models import Configuration
from foreverbull.worker import WorkerPool
from foreverbull_core.broker import Broker
from foreverbull_core.models.socket import Request, Response, SocketConfig
from foreverbull_zipline.app import Application
from foreverbull_zipline.models import Database, EngineConfig, IngestConfig
from pynng import Rep0, Req0, Sub0
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

from multiprocessing import get_start_method, set_start_method


@pytest.fixture(scope="session")
def spawn_process():
    method = get_start_method()
    if method != "spawn":
        set_start_method("spawn", force=True)


class Instrument(Base):
    __tablename__ = "instrument"
    isin = Column(String(), primary_key=True)


class OHLC(Base):
    __tablename__ = "ohlc"
    id = Column(Integer, primary_key=True)
    isin = Column(String(), ForeignKey("instrument.isin"))
    open = Column(Integer())
    high = Column(Integer())
    low = Column(Integer())
    close = Column(Integer())
    volume = Column(Integer())
    time = Column(String())


def populate_sql(ic: IngestConfig, db: Database):
    engine = create_engine(f"postgresql://{db.user}:{db.password}@{db.netloc}:{db.port}/{db.dbname}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(OHLC).delete()
    session.query(Instrument).delete()
    isin_to_symbol = {"US0378331005": "AAPL", "US88160R1014": "TSLA", "US5949181045": "MSFT", "US02079K1079": "GOOG", "US0231351067": "AMZN", "US30303M1027": "META"}
    for isin in ic.isins:
        feed = yfinance.Ticker(isin_to_symbol[isin])
        data = feed.history(start=ic.from_date, end=ic.to_date)
        instrument = Instrument(isin=isin)
        session.add(instrument)
        for (idx, row) in data.iterrows():
            ohlc = OHLC(
                isin=isin, open=row.Open, high=row.High, low=row.Low, close=row.Close, volume=row.Volume, time=str(idx)
            )
            session.add(ohlc)
            session.add(instrument)
    session.commit()


def on_ohlc(*args, **kwargs):
    pass


def test_simple_execution(spawn_process):
    # Setup
    worker_pool = WorkerPool()
    worker_pool.setup()

    client_socket = SocketConfig(host="127.0.0.1", port=6565)
    client = Foreverbull(client_socket, worker_pool)
    client._worker_routes["ohlc"] = on_ohlc
    client.start()
    client_socket = Req0(dial=f"tcp://{client_socket.host}:{client_socket.port}")
    client_socket.send_timeout = 10000
    client_socket.recv_timeout = 10000

    client_server_socket_config = SocketConfig(host="127.0.0.1", port=6566, listen=False)
    client_server_socket = Req0(listen=f"tcp://{client_server_socket_config.host}:{client_server_socket_config.port}")
    client_server_socket.send_timeout = 10000
    client_server_socket.recv_timeout = 10000

    backtest_socket = SocketConfig(host="127.0.0.1", port=5656)
    backtest = Application(backtest_socket)
    backtest.start()
    backtest_socket = Req0(dial=f"tcp://{backtest_socket.host}:{backtest_socket.port}")
    backtest_socket.send_timeout = 10000
    backtest_socket.recv_timeout = 10000
    backtest_socket.send(Request(task="info").dump())
    response = Response.load(backtest_socket.recv())
    assert response.error is None

    backtest_info = response.data
    backtest_main_socket = Req0(dial=f"tcp://{backtest_info['socket']['host']}:{backtest_info['socket']['port']}")
    backtest_main_socket.send_timeout = 10000
    backtest_main_socket.recv_timeout = 10000
    backtest_feed_socket = Sub0(
        dial=f"tcp://{backtest_info['feed']['socket']['host']}:{backtest_info['feed']['socket']['port']}"
    )
    backtest_feed_socket.recv_timeout = 10000
    backtest_feed_socket.subscribe(b"")

    # Ingest backtest data
    netloc = os.environ.get("POSTGRES_NETLOC", "127.0.0.1")
    database_config = Database(user="postgres", password="foreverbull", netloc=netloc, port=5433, dbname="postgres")
    ingest_config = IngestConfig(
        name="foreverbull",
        calendar_name="NYSE",
        from_date="2019-01-01",
        to_date="2021-12-31",
        isins=["US0378331005", "US88160R1014", "US5949181045", "US02079K1079", "US0231351067", "US30303M1027"],
        database=database_config,
    )
    populate_sql(ingest_config, database_config)

    backtest_main_socket.send(Request(task="ingest", data=ingest_config).dump())
    response = Response.load(backtest_main_socket.recv())
    assert response.error is None

    # Configure Backtest
    engine_config = EngineConfig(
        name="foreverbull",
        bundle="foreverbull",
        calendar="XFRA",
        start_date="2019-01-07",
        end_date="2021-12-31",
        benchmark="US0378331005",  # Apple
        isins=["US0378331005", "US88160R1014", "US5949181045", "US02079K1079", "US0231351067", "US30303M1027"],
    )
    backtest_main_socket.send(Request(task="configure", data=engine_config).dump())
    response = Response.load(backtest_main_socket.recv())
    assert response.error is None

    # Configure Worker
    worker_config = Configuration(
        execution_id="test",
        execution_start_date=date.today(),
        execution_end_date=date.today(),
        database=None,
        parameters=None,
        socket=client_server_socket_config,
    )
    client_socket.send(Request(task="configure", data=worker_config).dump())
    response = Response.load(client_socket.recv())
    assert response.error is None

    # Run Backtest
    backtest_main_socket.send(Request(task="run").dump())
    response = Response.load(backtest_main_socket.recv())
    assert response.error is None

    client_socket.send(Request(task="run_backtest").dump())
    response = Response.load(client_socket.recv())
    assert response.error is None

    while True:
        message = Request.load(backtest_feed_socket.recv())
        if message.task == "day_completed":
            backtest_main_socket.send(Request(task="continue").dump())
            response = Response.load(backtest_main_socket.recv())
            assert response.error is None
        elif message.task == "ohlc":
            client_server_socket.send(Request(task="ohlc", data=message.data).dump())
            response = Response.load(client_server_socket.recv())
            assert response.error is None
        elif message.task == "backtest_completed":
            break
    # Stop

    client_socket.send(Request(task="stop").dump())
    response = Response.load(client_socket.recv())
    assert response.error is None
    client.join()
    client_socket.close()
    client_server_socket.close()

    backtest_socket.send(Request(task="stop").dump())
    response = Response.load(backtest_socket.recv())
    assert response.error is None
    backtest_socket.close()
    backtest_main_socket.close()
    backtest_feed_socket.close()
    backtest.join()
