import time

import pytest
from foreverbull_core.broker import Broker
from foreverbull_zipline.app import Application
from foreverbull_zipline.backtest import Backtest


@pytest.fixture(scope="function")
def application():
    b = Broker("127.0.0.1:8080", "127.0.0.1")
    a = Application(b)
    a.start()
    yield a
    a.stop()
    a.join()


def test_start_stop():
    b = Broker("127.0.0.1:8080", "127.0.0.1")
    a = Application(b)
    a.start()
    a.stop()
    a.join()


def test_route_backtest_status(application):
    status = application._status()
    assert status["running"]


@pytest.mark.skip("Dont know how to handle result yet")
def test_route_backtest_result():
    pass


@pytest.mark.skip("Dont know how to handle result yet")
def test_route_backtest_result_negative():
    pass


def test_application_test_info_status(application):
    Backtest._config = None
    assert "socket" in application.info()
    assert "feed" in application.info() and "socket" in application.info()["feed"]
    assert "broker" in application.info() and "socket" in application.info()["broker"]
    assert "running" in application.info() and application.info()["running"] is True

    assert application._status()["configured"] is False
    assert application._status()["day_completed"] is False


def test_configured(application, backtest_config, yahoo_bundle):
    assert application._status()["configured"] is False
    application.backtest.configure(backtest_config)
    assert application._status()["configured"] is True


def test_run_once(application, backtest_config, mocker):
    mocker.patch.object(application.feed, "wait_for_new_day")
    application.backtest.configure(backtest_config)
    application._run()
    while application.backtest and application.backtest.is_alive():
        time.sleep(0.1)
    application.stop()


def test_run_early_stop(application, backtest_config):
    application.backtest.configure(backtest_config)
    application._run()
    time.sleep(0.5)
    application.stop()
