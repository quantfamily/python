from threading import Thread

import pynng
from foreverbull_core.models.socket import Request, Response, SocketConfig, SocketType
from foreverbull_core.socket.client import ContextClient, SocketClient


def test_socket_client():
    client = SocketClient(SocketConfig(host="127.0.0.1"))
    req_socket = pynng.Req0(dial=client.url())

    req = Request(task="demo")
    req_socket.send(req.dump())
    client_recieved = client.recv()

    rsp = Response(task="demo")
    client.send(rsp)
    req_socket_recieved = req_socket.recv()

    assert type(client_recieved) == Request
    assert type(req_socket_recieved) == bytes
    assert client.close() is None


def test_context_client():
    rep_client = SocketClient(
        SocketConfig(host="127.0.0.1", port=1337, listen=True, dial=False, socket_type=SocketType.REPLIER)
    )
    req_client = SocketClient(
        SocketConfig(host="127.0.0.1", port=1337, listen=False, dial=True, socket_type=SocketType.REQUESTER)
    )

    rep_context = rep_client.new_context()
    req_context = req_client.new_context()

    req_context.send(Request(task="demo"))

    request = rep_context.recv()
    assert request.task == "demo"

    rep_context.send(Response(task="works"))

    response = req_context.recv()
    assert response.task == "works"

    rep_context.close()
    req_context.close()
    req_client.close()
    rep_client.close()


def test_context_client_in_thread():
    context_replier = SocketClient(
        SocketConfig(host="127.0.0.1", port=1337, listen=True, dial=False, socket_type=SocketType.REPLIER)
    )
    context_requester = SocketClient(
        SocketConfig(host="127.0.0.1", port=1337, listen=False, dial=True, socket_type=SocketType.REQUESTER)
    )

    def listen_on_context(context_socket: ContextClient, return_string: str):
        context_socket.recv()
        context_socket.send((Response(task=return_string)))

    rep1 = context_replier.new_context()
    t1 = Thread(
        target=listen_on_context,
        args=(
            rep1,
            "from first",
        ),
    )
    t1.start()

    rep2 = context_replier.new_context()
    t2 = Thread(
        target=listen_on_context,
        args=(
            rep2,
            "from second",
        ),
    )
    t2.start()

    rep3 = context_replier.new_context()
    t3 = Thread(
        target=listen_on_context,
        args=(
            rep3,
            "from third",
        ),
    )
    t3.start()

    req1 = context_requester.new_context()
    req2 = context_requester.new_context()
    req3 = context_requester.new_context()

    req1.send(Request(task="one"))
    req2.send(Request(task="two"))
    req3.send(Request(task="three"))

    from_first = req1.recv()
    from_second = req2.recv()
    from_third = req3.recv()

    req1.close()
    req2.close()
    req3.close()
    rep1.close()
    rep2.close()
    rep3.close()
    context_requester.close()
    context_replier.close()

    t1.join()
    t2.join()
    t3.join()

    assert from_first.task == "from first"
    assert from_second.task == "from second"
    assert from_third.task == "from third"
