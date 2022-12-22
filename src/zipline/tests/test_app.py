import time

from foreverbull_core.models.socket import SocketConfig
from foreverbull_zipline.app import Application
from foreverbull_zipline.backtest import Backtest


def test_start_stop():
    socket_config = SocketConfig(host="127.0.0.1", port=6565)
    application = Application(socket_config)
    application.start()
    for _ in range(10):
        if application.running:
            break
        time.sleep(0.1)
    else:
        raise Exception("Application not running")
    application.stop()
    application.join()


def test_route_backtest_status(application: Application):
    status = application._status()
    assert status["running"]


def test_application_test_info_status(application: Application):
    Backtest._config = None
    assert "socket" in application.info()
    assert "feed" in application.info() and "socket" in application.info()["feed"]
    assert "broker" in application.info() and "socket" in application.info()["broker"]
    assert "running" in application.info() and application.info()["running"] is True

    assert application._status()["configured"] is False
    assert application._status()["day_completed"] is False


def test_configured(application, engine_config):
    assert application._status()["configured"] is False
    application.backtest.configure(engine_config)
    assert application._status()["configured"] is True


def test_run_once(application: Application, engine_config, mocker):
    mocker.patch.object(application.feed, "wait_for_new_day")
    application.backtest.configure(engine_config)
    application._run()
    while application.backtest and application.backtest.is_alive():
        time.sleep(0.1)
    application.stop()


def test_run_early_stop(application: Application, engine_config):
    application.backtest.configure(engine_config)
    application._run()
    time.sleep(0.5)
    application.stop()
