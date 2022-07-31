from foreverbull_core.broker import Broker
from foreverbull_core.http.http import HTTPClient
from foreverbull_core.socket.client import SocketClient


def test_broker():
    broker_host = "my_host.com"
    local_host = "127.0.0.1"
    broker = Broker(broker_host, local_host)
    assert broker._broker_host == broker_host
    assert broker._local_host == local_host
    assert type(broker.http) == HTTPClient
    assert type(broker.socket) == SocketClient
