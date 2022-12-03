import os
from datetime import date
from typing import Iterator

import pynng
import pytest
import yfinance
from foreverbull.environment import EnvironmentParser
from foreverbull.foreverbull import Foreverbull
from foreverbull.models import Configuration
from foreverbull_core.broker import Broker
from foreverbull_core.models.socket import Request, Response
from foreverbull_zipline.app import Application
from foreverbull_zipline.models import Database, EngineConfig, IngestConfig
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


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
    isin_to_symbol = {"US0378331005": "AAPL", "US88160R1014": "TSLA", "US5949181045": "MSFT"}
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


class Backtest:
    def __init__(self, application_socket: pynng.Req0) -> None:
        self.application_socket = application_socket
        req = Request(task="info")
        data = req.dump()
        application_socket.send(data)
        rsp_data = application_socket.recv()
        rsp = Response.load(rsp_data)

        req = rsp.data["socket"]
        self.request_socket = pynng.Req0(dial=f"tcp://{req['host']}:{req['port']}")
        self.request_socket.recv_timeout = 5000
        self.request_socket.send_timeout = 5000

        feed = rsp.data["feed"]["socket"]
        self.feed_socket = pynng.Sub0(dial=f"tcp://{feed['host']}:{feed['port']}")
        self.feed_socket.subscribe(b"")
        self.feed_socket.recv_timeout = 5000

    def ingest(self, config: IngestConfig) -> None:
        req = Request(task="ingest", data=config)
        self.request_socket.send(req.dump())
        rsp_data = self.request_socket.recv()
        rsp = Response.load(rsp_data)
        assert rsp.error is None

    def configure(self, backtest_config: EngineConfig) -> None:
        req = Request(task="configure", data=backtest_config)
        self.request_socket.send(req.dump())
        rsp_data = self.request_socket.recv()
        rsp = Response.load(rsp_data)
        assert rsp.error is None

    def run(self) -> Iterator[Request]:
        req = Request(task="run")
        self.request_socket.send(req.dump())
        rsp_data = self.request_socket.recv()
        rsp = Response.load(rsp_data)
        assert rsp.error is None
        while True:
            data = self.feed_socket.recv()
            msg = Request.load(data)
            if msg.task == "day_completed":
                req = Request(task="continue")
                self.request_socket.send(req.dump())
                rsp_data = self.request_socket.recv()
                rsp = Response.load(rsp_data)
                assert rsp.error is None
            if msg.task == "backtest_completed":
                break
            yield msg


def on_message(data, dataframe, *args, **kwargs):
    print("GOT MESSAGE", data, dataframe)
    return


class Client:
    def __init__(self, foreverbull: Foreverbull, socket: pynng.Req0) -> None:
        self.foreverbull = foreverbull
        self.socket = socket

    def configure(self, config: Configuration) -> None:
        req = Request(task="configure", data=config)

        context_socket = self.socket.new_context()
        context_socket.send(req.dump())
        rsp_data = context_socket.recv()
        rsp = Response.load(rsp_data)
        assert rsp.task == "configure"
        assert rsp.error is None

    def process(self, ohlc: OHLC) -> None:
        req = Request(task="stock_data", data=ohlc)
        context_socket = self.socket.new_context()
        context_socket.send(req.dump())
        rsp_data = context_socket.recv()
        rsp = Response.load(rsp_data)
        assert rsp.task == "stock_data"
        assert rsp.error is None


@pytest.fixture
def backtest():
    foreverbull_broker = Broker("127.0.0.1:8080", "127.0.0.1")
    application = Application(foreverbull_broker)
    application.start()
    socket = pynng.Req0(dial=f"{application.broker.socket.url()}")
    socket.recv_timeout = 5000
    socket.send_timeout = 5000
    b = Backtest(socket)
    yield b
    application.stop()
    application.join()


@pytest.fixture
def client():
    input_parser = EnvironmentParser()
    input_parser.algo_file = None
    input_parser.broker = input_parser.get_broker()
    input_parser.service_instance = input_parser.get_service_instance(input_parser.broker)
    fb = Foreverbull(input_parser.broker.socket, 1)
    fb._worker_routes["stock_data"] = on_message
    fb.start()

    host = input_parser.broker.socket_config.host
    port = input_parser.broker.socket_config.port
    socket = pynng.Req0(dial=f"tcp://{host}:{port}")
    socket.recv_timeout = 5000
    socket.send_timeout = 5000
    yield Client(fb, socket)

    fb.stop()
    fb.join()


def test_backtest_client_connection(backtest: Backtest, client: Client):
    netloc = os.environ.get("POSTGRES_NETLOC", "127.0.0.1")
    database_config = Database(user="postgres", password="foreverbull", netloc=netloc, port=5433, dbname="postgres")
    ingest_config = IngestConfig(
        name="foreverbull",
        calendar_name="NYSE",
        from_date="2020-01-01",
        to_date="2020-12-31",
        isins=["US0378331005", "US88160R1014", "US5949181045"],
        database=database_config,
    )
    populate_sql(ingest_config, database_config)
    backtest.ingest(ingest_config)

    backtest_config = EngineConfig(
        bundle="foreverbull",
        calendar="XFRA",
        start_date="2020-01-07",
        end_date="2020-02-01",
        benchmark="US0378331005",  # Apple
        isins=["US0378331005", "US88160R1014"],  # Apple, Tesla
    )
    backtest.configure(backtest_config)

    worker_config = Configuration(
        execution_id="123",
        execution_start_date=date(2020, 1, 7),
        execution_end_date=date(2020, 2, 1),
        parameters=[],
        database=database_config,
    )
    client.configure(worker_config)

    for message in backtest.run():
        # print("message: ", message)
        if message.task == "stock_data":
            try:
                client.process(message.data)
            except Exception as exc:
                print("ERROR", exc)
                return
