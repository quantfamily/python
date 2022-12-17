import os
from datetime import date

import pytest
from foreverbull.models import Configuration
from foreverbull_core.models.socket import SocketConfig

from foreverbull.worker import WorkerPool

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
