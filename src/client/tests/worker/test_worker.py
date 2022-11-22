from datetime import datetime
from multiprocessing import Queue

from foreverbull_core.models.finance import Order
from foreverbull_core.models.worker import Parameter

from foreverbull.models import OHLC, Configuration
from foreverbull.worker.worker import Worker, WorkerHandler


def just_return_order_amount_10(*_):
    return Order(amount=10)


def test_setup_parameters_is_None():
    req = Queue()
    rsp = Queue()
    worker_conf = Configuration(
        execution_id=123, execution_start_date=datetime.now(), execution_end_date=datetime.now()
    )
    worker = Worker(req, rsp, worker_conf)

    assert len(worker.parameters) == 0


def test_setup_parameters():
    req = Queue()
    rsp = Queue()
    param1 = Parameter(key="key1", value=22, default=11)
    worker_conf = Configuration(
        execution_id=123, execution_start_date=datetime.now(), execution_end_date=datetime.now(), parameters=[param1]
    )
    worker = Worker(req, rsp, worker_conf)

    assert len(worker.parameters) == 1


def test_worker_process_request():
    order_to_return = Order(amount=1337)

    def on_update(ohlc, _):
        assert type(ohlc) == OHLC
        return order_to_return

    worker_conf = Configuration(
        execution_id=123, execution_start_date=datetime.now(), execution_end_date=datetime.now()
    )
    worker = Worker(None, None, worker_conf, **{"stock_data": on_update})

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

    assert worker._process_request(ohlc) == order_to_return


def test_worker_process_start_stop():
    queue = Queue()
    worker_conf = Configuration(
        execution_id=123, execution_start_date=datetime.now(), execution_end_date=datetime.now()
    )
    worker = Worker(queue, 123, worker_conf)
    worker.start()
    queue.put(None)
    worker.join()


def test_worker_handler_lock():
    worker_conf = Configuration(
        execution_id=123, execution_start_date=datetime.now(), execution_end_date=datetime.now()
    )
    wh = WorkerHandler(worker_conf)

    # Check if locked after init, acquire and make sure its locked
    assert wh.locked() is False
    assert wh.acquire() is True
    assert wh.locked() is True

    # second acquire should not work
    assert wh.acquire() is False

    # release and check its not locked anymore
    wh.release()
    assert wh.locked() is False
    wh.stop()


def test_worker_handler():
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
    response = Order(amount=10)

    worker_conf = Configuration(
        execution_id=123, execution_start_date=datetime.now(), execution_end_date=datetime.now()
    )
    wh = WorkerHandler(worker_conf, stock_data=just_return_order_amount_10)

    assert wh.locked() is False
    wh.acquire(False, -1)

    result = wh.process(ohlc)

    wh.release()
    wh.stop()

    assert result == response
