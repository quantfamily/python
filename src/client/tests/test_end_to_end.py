from argparse import ArgumentParser
from datetime import datetime

import pytest
from foreverbull.foreverbull import Foreverbull
from foreverbull.models import OHLC
from foreverbull.parser import Parser
from foreverbull_core.models.socket import Request, Response
from pynng import Req0


@pytest.mark.skip(reason="test")
def test_simple_simulation(algo_file, client_config, server_socket_config):
    args = [algo_file]
    parser = ArgumentParser()
    input_parser = Parser()
    input_parser.add_arguments(parser)
    args = parser.parse_args(args)
    input_parser.parse(args)

    server_socket = Req0(listen=f"tcp://{server_socket_config.host}:{server_socket_config.port}")
    server_socket.recv_timeout = 100000
    server_socket.send_timeout = 100000

    fb = Foreverbull(input_parser.get_broker().socket_config)
    fb.start()

    request_socket = Req0(
        dial=f"tcp://{input_parser.get_broker().socket_config.host}:{input_parser.get_broker().socket_config.port}"
    )
    request_socket.recv_timeout = 100000
    request_socket.send_timeout = 100000

    request_context = request_socket.new_context()
    request_context.send(Request(task="configure", data=client_config).dump())
    response = Response.load(request_context.recv())
    request_context.close()
    assert response.task == "configure"
    assert response.error is None

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
        server_context = server_socket.new_context()
        server_context.send(Request(task="ohlc", data=ohlc).dump())
        response = Response.load(server_context.recv())
        server_context.close()
        assert response.task == "ohlc"
        assert response.error is None

    request_context = request_socket.new_context()
    request_context.send(Request(task="stop").dump())
    response = Response.load(request_context.recv())
    request_context.close()
    assert response.task == "stop"
    assert response.error is None

    fb.join()

    request_socket.close()
    server_socket.close()
