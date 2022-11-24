import pynng
import pytest
from foreverbull_core.broker import Broker
from foreverbull_core.models.finance import Asset, Order
from foreverbull_core.models.socket import Request, Response

from foreverbull_zipline.app import Application
from foreverbull_zipline.models import EngineConfig, IngestConfig
from tests.conftest import foreverbull_bundle, yahoo_bundle
from tests.factories import populate_sql


@pytest.fixture(scope="function")
def application():
    b = Broker("127.0.0.1:8080", "127.0.0.1")
    a = Application(b)
    a.start()
    yield a
    a.stop()
    a.join()


@pytest.fixture(scope="function")
def application_socket(application):
    socket = pynng.Req0(dial=f"{application.broker.socket.url()}")
    socket.recv_timeout = 5000
    socket.send_timeout = 5000
    return socket


@pytest.fixture(scope="function")
def backtest(application_socket):
    req = Request(task="info")
    data = req.dump()
    application_socket.send(data)
    rsp_data = application_socket.recv()
    rsp = Response.load(rsp_data)
    return rsp.data


def request_socket(socket_info):
    socket = pynng.Req0(dial=f"tcp://{socket_info['host']}:{socket_info['port']}")
    socket.recv_timeout = 5000
    socket.send_timeout = 5000
    return socket


def feed_socket(socket_info):
    socket = pynng.Sub0(dial=f"tcp://{socket_info['host']}:{socket_info['port']}")
    socket.subscribe(b"")
    socket.recv_timeout = 5000
    return socket


def configure(main_socket, backtest_config):
    req = Request(task="configure", data=backtest_config)
    main_socket.send(req.dump())
    rsp_data = main_socket.recv()
    return Response.load(rsp_data)


def run_backtest(main_socket):
    req = Request(task="run")
    main_socket.send(req.dump())
    rsp_data = main_socket.recv()
    return Response.load(rsp_data)


def new_feed_data(feed_socket):
    msg_data = feed_socket.recv()
    msg = Request.load(msg_data)
    return msg


def day_completed(main_socket):
    req = Request(task="continue")
    main_socket.send(req.dump())
    rsp_data = main_socket.recv()
    return Response.load(rsp_data)


@pytest.mark.parametrize(
    "bundle,config",
    [
        (
            yahoo_bundle,
            EngineConfig(
                bundle="yahoo",
                calendar="NYSE",
                start_date="2020-01-07",
                end_date="2020-02-01",
                benchmark="AAPL",
                isins=["AAPL", "TSLA"],
            ),
        ),
        (
            "foreverbull_bundle",
            EngineConfig(
                bundle="foreverbull",
                calendar="XFRA",
                start_date="2020-01-07",
                end_date="2020-02-01",
                benchmark="US0378331005",  # Apple
                isins=["US0378331005", "US88160R1014"],  # Apple, Tesla
            ),
        ),
    ],
)
def test_simple_run(backtest, bundle, config):
    main = request_socket(backtest["socket"])
    feed = feed_socket(backtest["feed"]["socket"])

    rsp = configure(main, config)
    assert rsp.error is None

    rsp = run_backtest(main)
    assert rsp.error is None

    while True:
        msg = new_feed_data(feed)
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
        if msg.task == "backtest_completed":
            break


@pytest.mark.parametrize(
    "fill_database,config",
    [
        (
            False,
            IngestConfig(
                name="yahoo",
                calendar_name="NYSE",
                from_date="2020-01-01",
                to_date="2020-12-31",
                isins=["AAPL", "TSLA", "MSFT"],
            ),
        ),
        (
            True,
            IngestConfig(
                name="foreverbull",
                calendar_name="NYSE",
                from_date="2020-01-01",
                to_date="2020-12-31",
                isins=["US0378331005", "US88160R1014", "US5949181045"],
            ),
        ),
    ],
)
def test_ingest(backtest, fill_database, config: IngestConfig, database_config):
    if fill_database:
        populate_sql(config, database_config)
        config.database = database_config
    main = request_socket(backtest["socket"])

    req = Request(task="ingest", data=config)
    main.send(req.dump())
    rsp_data = main.recv()
    rsp = Response.load(rsp_data)

    assert rsp.error is None


@pytest.mark.parametrize(
    "bundle,config",
    [
        (
            yahoo_bundle,
            EngineConfig(
                bundle="yahoo",
                calendar="NYSE",
                start_date="2020-01-07",
                end_date="2020-02-01",
                benchmark="AAPL",
                isins=["AAPL", "TSLA"],
            ),
        ),
        (
            foreverbull_bundle,
            EngineConfig(
                bundle="foreverbull",
                calendar="XFRA",
                start_date="2020-01-07",
                end_date="2020-02-01",
                benchmark="US0378331005",  # Apple
                isins=["US0378331005", "US88160R1014"],  # Apple, Tesla
            ),
        ),
    ],
)
def test_order_and_result(backtest, bundle, config):
    main = request_socket(backtest["socket"])
    feed = feed_socket(backtest["feed"]["socket"])
    broker = request_socket(backtest["broker"]["socket"])
    rsp = configure(main, config)
    assert rsp.error is None

    rsp = run_backtest(main)
    assert rsp.error is None

    while True:  # Just to jump one day
        msg = new_feed_data(feed)
        if msg.task == "portfolio":
            continue
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
            break
        if msg.task == "backtest_completed":
            break

    order = Order(asset=Asset(symbol=config.isins[0], exchange="QUANDL"), amount=10)
    req = Request(task="order", data=order)
    broker.send(req.dump())
    rsp_data = broker.recv()
    rsp = Response.load(rsp_data)
    assert rsp.error is None
    order_data = rsp.data

    while True:  # Just to jump one day
        msg = new_feed_data(feed)
        if msg.task == "portfolio":
            pass
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
            break
        if msg.task == "backtest_completed":
            break

    while True:  # Just to jump one day
        msg = new_feed_data(feed)
        if msg.task == "portfolio":
            pass
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
            break
        if msg.task == "backtest_completed":
            break

    order = Order.load(order_data)
    req = Request(task="get_order", data=order)
    broker.send(req.dump())
    rsp_data = broker.recv()
    rsp = Response.load(rsp_data)
    assert rsp.error is None

    while True:
        msg = new_feed_data(feed)
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
        if msg.task == "backtest_completed":
            break

    req = Request(task="result")
    main.send(req.dump())
    rsp_data = main.recv()
    rsp = Response.load(rsp_data)
    assert rsp.error is None
