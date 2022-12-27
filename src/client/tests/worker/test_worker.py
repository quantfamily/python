import os
from datetime import datetime
from multiprocessing import Event

import pynng
import pytest
from foreverbull.data import Database
from foreverbull.models import OHLC
from foreverbull.worker.worker import Worker, WorkerPool, WorkerProcess, WorkerThread
from foreverbull_core.models.socket import Request, Response
from pandas import DataFrame
from pynng import Req0

from foreverbull_core.models.finance import Order


def plain_ohlc_function(ohlc: OHLC, database: Database):
    assert type(ohlc) == OHLC
    assert type(database) == Database
    df = database.stock_data(ohlc.isin)
    assert type(df) == DataFrame
    assert len(df)
    return Order(isin=ohlc.isin, amount=10)


@pytest.mark.parametrize("workerclass", [WorkerThread, WorkerProcess])
def test_worker(workerclass: Worker, client_config, server_socket_config, spawn_process, loaded_database, instruments):
    if type(workerclass) is WorkerProcess and os.environ.get("THREADED_EXECUTION"):
        pytest.skip("WorkerProcess not supported with THREADED_EXECUTION")
    survey_address = "ipc:///tmp/worker_pool.ipc"
    survey_socket = pynng.Surveyor0(listen=survey_address)
    survey_socket.recv_timeout = 10000
    survey_socket.send_timeout = 10000
    state_address = "ipc:///tmp/worker_pool_state.ipc"
    state_socket = pynng.Sub0(listen=state_address)
    state_socket.recv_timeout = 10000
    state_socket.send_timeout = 10000
    state_socket.subscribe(b"")
    server_socket = Req0(listen=f"tcp://{server_socket_config.host}:{server_socket_config.port}")
    server_socket.recv_timeout = 10000
    server_socket.send_timeout = 10000

    stop_event = Event()

    worker = workerclass(survey_address, state_address, stop_event, ohlc=plain_ohlc_function)
    worker.start()

    state_socket.recv()

    survey_socket.send(Request(task="configure", data=client_config).dump())
    response = Response.load(survey_socket.recv())
    assert response.task == "configure"
    assert response.error is None

    survey_socket.send(Request(task="run_backtest", data=None).dump())
    response = Response.load(survey_socket.recv())
    assert response.task == "run_backtest"
    assert response.error is None

    for isin, _ in instruments.items():
        context = server_socket.new_context()
        ohlc = OHLC(
            isin=isin,
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
        assert response.task == request.task
        assert response.error is None
        assert response.data
        order = Order(**response.data)
        assert order.isin == ohlc.isin

    server_socket.close()

    assert response.task == request.task
    assert response.error is None

    stop_event.set()
    survey_socket.send(Request(task="stop", data=None).dump())
    response = Response.load(survey_socket.recv())
    assert response.task == "stop"
    assert response.error is None

    survey_socket.close()
    state_socket.close()


def test_pool(client_config, server_socket_config, spawn_process, loaded_database):
    server_socket = Req0(listen=f"tcp://{server_socket_config.host}:{server_socket_config.port}")
    server_socket.recv_timeout = 1000
    server_socket.send_timeout = 1000

    pool = WorkerPool(ohlc=plain_ohlc_function)
    pool.setup()
    pool.configure(client_config)

    pool.run_backtest()

    for _ in range(50):
        context = server_socket.new_context()
        ohlc = OHLC(
            isin="US0378331005",
            price=133.7,
            open=133.6,
            close=1337.8,
            high=1337.8,
            low=1337.6,
            volume=9001,
            time=datetime(2021, 10, 1),
        )
        request = Request(task="ohlc", data=ohlc)
        context.send(request.dump())
        response = Response.load(context.recv())
        assert response.error is None
        context.close()
    server_socket.close()

    pool.stop()

    assert response.task == request.task
    assert response.error is None
