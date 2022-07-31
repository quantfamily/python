import json
from threading import Thread

import pytest
from foreverbull import Foreverbull
from foreverbull_core.models.socket import Request, Response, SocketConfig
from foreverbull_core.socket.nanomsg import NanomsgSocket


@pytest.fixture(scope="function")
def sample_data():
    with open("tests/sample_data.json", "r") as fr:
        data = json.load(fr)
    for pair in data:
        pair["req"] = Request(**pair["req"])
        pair["rsp"] = Response(**pair["rsp"])
    return data


def demo(x, y):
    pass


@pytest.fixture(scope="function")
def session():
    Foreverbull._routes["stock_data"] = demo
    backtest = Foreverbull()
    t1 = Thread(target=backtest._on_message)
    local_session = LocalSession(backtest.broker.local_connection()["port"])

    def session():
        t1.start()
        return local_session

    yield session
    t1.join()


class LocalSession:
    def __init__(self, port):
        self.host = "127.0.0.1"
        self.port = port
        self.config = SocketConfig(socket_type="requester", host=self.host, port=self.port, listen=False)
        self.socket = NanomsgSocket(self.config)

    def send(self, message):
        return self.socket.send(message)

    def recv(self):
        return self.socket.recv()
