from datetime import datetime

import pytest
from foreverbull.foreverbull import Foreverbull
from foreverbull.models import Configuration
from foreverbull_core.models.socket import Request, Response, SocketConfig
from pynng import Req0


@pytest.fixture
def client_socket_config():
    return SocketConfig(host="127.0.0.1", port=5656, listen=True)


@pytest.fixture
def server_socket():
    return Req0(listen="tcp://127.0.0.1:5757")


@pytest.fixture
def configuration():
    return Configuration(
        execution_id="test",
        execution_start_date=datetime.now(),
        execution_end_date=datetime.now(),
        database=None,
        parameters=None,
        socket=SocketConfig(host="127.0.0.1", port=5757, listen=False, recv_timeout=200, send_timeout=200),
    )


def test_configure_and_stop(client_socket_config, configuration, worker_pool):
    fb = Foreverbull(client_socket_config, worker_pool)

    fb.start()
    fb.configure(configuration)
    fb.stop()
    fb.join()


def test_configure_and_stop_over_socket(client_socket_config, worker_pool, configuration):
    fb = Foreverbull(client_socket_config, worker_pool)
    fb.start()

    socket = Req0(dial=f"tcp://{client_socket_config.host}:{client_socket_config.port}")
    socket.recv_timeout = 5000
    socket.send_timeout = 5000

    context = socket.new_context()
    context.send(Request(task="configure", data=configuration).dump())
    response = Response.load(context.recv())
    context.close()
    assert response.task == "configure"
    assert response.error is None

    context = socket.new_context()
    context.send(Request(task="stop").dump())
    response = Response.load(context.recv())
    context.close()
    assert response.task == "stop"
    assert response.error is None

    fb.join()
