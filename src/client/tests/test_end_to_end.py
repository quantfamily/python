from datetime import date, datetime

import pytest
from foreverbull_core.models.socket import Request, SocketConfig, SocketType
from foreverbull_core.models.worker import Parameter
from foreverbull_core.socket.client import SocketClient

from foreverbull.environment import EnvironmentParser
from foreverbull.foreverbull import Foreverbull
from foreverbull.models import OHLC, Configuration


def on_message(data, dataframe, ma_high, ma_low):
    return


def test_simple_simulation_without_socket():
    input_parser = EnvironmentParser()
    input_parser.algo_file = None
    input_parser.broker = input_parser.get_broker()
    input_parser.service_instance = input_parser.get_service_instance(input_parser.broker)
    fb = Foreverbull(input_parser.broker.socket, 1)
    fb._worker_routes["stock_data"] = on_message

    fb.start()

    # configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    configuration = Configuration(
        execution_id="123",
        execution_start_date=date.today(),
        execution_end_date=date.today(),
        parameters=[param1, param2],
    )
    req = Request(task="configure", data=configuration)
    rsp = fb._routes(req)
    assert rsp.error is None
    # stock_data
    ohlc = OHLC(
        isin="ISIN11223344",
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
        time=datetime.now(),
    )
    for _ in range(10):
        req = Request(task="stock_data", data=ohlc)
        rsp = fb._routes(req)
        assert rsp.error is None
    # teardown
    fb.stop()
    fb.join()


@pytest.fixture
def get_requester():
    def inner(host: str, port: int) -> SocketClient:
        socket = SocketClient(
            SocketConfig(host=host, port=port, listen=False, dial=True, socket_type=SocketType.REQUESTER)
        )
        return socket

    return inner


def test_simulation_with_socket(get_requester):
    input_parser = EnvironmentParser()
    input_parser.algo_file = None
    input_parser.broker = input_parser.get_broker()
    input_parser.service_instance = input_parser.get_service_instance(input_parser.broker)
    fb = Foreverbull(input_parser.broker.socket, 1)
    fb._worker_routes["stock_data"] = on_message

    fb.start()

    socket = get_requester(input_parser.broker.socket_config.host, input_parser.broker.socket_config.port)

    # configure
    param1 = Parameter(key="ma_high", value=64, default=30)
    param2 = Parameter(key="ma_low", value=16, default=90)
    configuration = Configuration(
        execution_id="123",
        execution_start_date=date.today(),
        execution_end_date=date.today(),
        parameters=[param1, param2],
    )
    req = Request(task="configure", data=configuration)

    context_socket = socket.new_context()
    context_socket.send(req)
    rsp = context_socket.recv()
    assert rsp.task == "configure"

    # stock_data
    ohlc = OHLC(
        isin="ISIN11223344",
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
        time=datetime.now(),
    )
    for _ in range(10):
        req = Request(task="stock_data", data=ohlc)
        context_socket = socket.new_context()
        context_socket.send(req)
        rsp = context_socket.recv()
        assert rsp.task == "stock_data"
    # taredown
    fb.stop()
    fb.join()
