import pynng
import pytest
from foreverbull_core.models.finance import Order, Portfolio
from foreverbull_core.models.socket import Request, Response
from foreverbull_zipline.app import Application


@pytest.fixture(scope="function")
def application_socket(application: Application):
    socket = pynng.Req0(dial=f"tcp://{application.socket_config.host}:{application.socket_config.port}")
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


def test_simple_run(backtest, foreverbull_bundle, engine_config):
    main = request_socket(backtest["socket"])
    feed = feed_socket(backtest["feed"]["socket"])

    rsp = configure(main, engine_config)
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


def test_ingest(backtest, ingest_config, foreverbull_bundle):
    main = request_socket(backtest["socket"])

    req = Request(task="ingest", data=ingest_config)
    main.send(req.dump())
    rsp_data = main.recv()
    rsp = Response.load(rsp_data)

    assert rsp.error is None


def test_order_and_result(backtest, foreverbull_bundle, engine_config):
    main = request_socket(backtest["socket"])
    feed = feed_socket(backtest["feed"]["socket"])
    broker = request_socket(backtest["broker"]["socket"])
    rsp = configure(main, engine_config)
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

    order = Order(isin=engine_config.isins[0], amount=10)
    req = Request(task="order", data=order)
    broker.send(req.dump())
    rsp_data = broker.recv()
    rsp = Response.load(rsp_data)
    assert rsp.error is None
    order_data = rsp.data

    while True:  # Just to jump one day
        msg = new_feed_data(feed)
        if msg.task == "portfolio":
            portfolio = Portfolio(**msg.data)
            assert len(portfolio.positions) == 0
        if msg.task == "day_completed":
            rsp = day_completed(main)
            assert rsp.error is None
            break
        if msg.task == "backtest_completed":
            break

    while True:  # Just to jump one day
        msg = new_feed_data(feed)
        if msg.task == "portfolio":
            portfolio = Portfolio(**msg.data)
            assert len(portfolio.positions) == 1
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
