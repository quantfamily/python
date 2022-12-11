import os
from datetime import datetime
from multiprocessing import Event

import pytest
from foreverbull.models import OHLC
from foreverbull.worker.worker import WorkerPool, WorkerProcess, WorkerThread
from foreverbull_core.models.socket import Request, Response
from pynng import Req0


def plain_ohlc_function(ohlc: OHLC, *args, **kwargs):
    return None

@pytest.mark.skipif(os.getenv("THREADED_EXECUTION"))
def test_worker_process(client_config, server_socket_config):
    event = Event()

    worker = WorkerProcess(client_config, event, ohlc=plain_ohlc_function)
    worker.start()

    server_socket = Req0(listen=f"tcp://{server_socket_config.host}:{server_socket_config.port}")
    server_socket.recv_timeout = 1000
    server_socket.send_timeout = 1000

    context = server_socket.new_context()
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
    request = Request(task="ohlc", data=ohlc)

    context.send(request.dump())
    response = Response.load(context.recv())
    context.close()
    server_socket.close()

    assert response.task == request.task

    event.set()
    worker.join()

def test_worker_thread(client_config, server_socket_config):
    event = Event()

    worker = WorkerThread(client_config, event, ohlc=plain_ohlc_function)
    worker.start()

    server_socket = Req0(listen=f"tcp://{server_socket_config.host}:{server_socket_config.port}")
    server_socket.recv_timeout = 1000
    server_socket.send_timeout = 1000

    context = server_socket.new_context()
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
    request = Request(task="ohlc", data=ohlc)

    context.send(request.dump())
    response = Response.load(context.recv())
    context.close()
    server_socket.close()

    assert response.task == request.task

    event.set()
    worker.join()


def test_worker_pool(client_config, server_socket_config):
    worker_pool = WorkerPool(client_config, ohlc=plain_ohlc_function)
    worker_pool.start()

    server_socket = Req0(listen=f"tcp://{server_socket_config.host}:{server_socket_config.port}")
    server_socket.recv_timeout = 1000
    server_socket.send_timeout = 1000

    for _ in range(16):
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
        context = server_socket.new_context()
        request = Request(task="ohlc", data=ohlc)

        context.send(request.dump())
        response = Response.load(context.recv())
        context.close()

        assert response.task == request.task

    worker_pool.stop()
    server_socket.close()
