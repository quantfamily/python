import threading
import time

import pytest

from foreverbull_zipline.exceptions import EndOfDayError
from foreverbull_zipline.feed import Feed


def test_start_stop(backtest):
    feed = Feed(backtest)
    feed.stop()


def test_timeout(backtest):
    feed = Feed(backtest)
    feed.lock.clear()

    def set_lock(lock):
        time.sleep(1.0)
        lock.set()

    t1 = threading.Thread(target=set_lock, args=(feed.lock,))
    t1.start()
    feed.wait_for_new_day()


def test_timeout_exception(backtest):
    feed = Feed(backtest)
    feed.lock.clear()
    feed._timeouts = 2
    with pytest.raises(EndOfDayError, match="timeout when waiting for new day"):
        feed.wait_for_new_day()
