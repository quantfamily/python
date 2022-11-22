import pytest
from foreverbull_core.http.backtest import Backtest
from foreverbull_core.http.service import Service
from foreverbull_core.models.backtest import Session
from foreverbull_core.models.service import Instance
from pytest_mock import MockerFixture

from foreverbull import __main__
from foreverbull.environment import EnvironmentError, EnvironmentParser


def test_run_foreverbull_as_instance(mocker: MockerFixture):
    __main__._run_input = EnvironmentParser()
    import_algo_file = mocker.patch.object(__main__._run_input, "import_algo_file")
    update_instance = mocker.patch.object(Service, "update_instance", return_value=True)
    sleep = mocker.patch.object(__main__, "sleep_till_keyboard_interrupt", return_value=True)

    service_instance = Instance(id="123", service_id="456", host="abc.com", port=1337)
    __main__._run_input.service_instance = service_instance
    __main__._run_input.broker = __main__._run_input.get_broker()
    __main__._run_input.executors = 0

    __main__.run_foreverbull(__main__._run_input)

    import_algo_file.assert_called_once()
    assert update_instance.call_count == 2
    sleep.assert_called_once()


@pytest.mark.skip(reason="not enabled")
def test_run_foreverbull_instanceless(mocker: MockerFixture):
    __main__._run_input = EnvironmentParser()
    session = Session(id="123", backtest_id="456")

    import_algo_file = mocker.patch.object(__main__._run_input, "import_algo_file")
    create_session = mocker.patch.object(Backtest, "create_session", return_value=session)
    setup_session = mocker.patch.object(Backtest, "setup_session", return_value=True)
    configure_session = mocker.patch.object(Backtest, "configure_session", return_value=True)
    run_session = mocker.patch.object(Backtest, "run_session", return_value=True)
    stop_session = mocker.patch.object(Backtest, "stop_session", return_value=True)
    sleep = mocker.patch.object(__main__, "sleep_till_keyboard_interrupt", return_value=True)

    __main__._run_input.backtest_id = "backtest_id"
    __main__._run_input.broker = __main__._run_input.get_broker()
    __main__._run_input.executors = 0

    __main__.run_foreverbull(__main__._run_input)

    import_algo_file.assert_called_once()
    create_session.assert_called_once()
    setup_session.assert_called_once()
    configure_session.assert_called_once()
    run_session.assert_called_once()
    stop_session.assert_called_once()
    sleep.assert_called_once()


@pytest.mark.skip(reason="not enabled")
def test_run_foreverbull_inputerror(mocker: MockerFixture):
    __main__._run_input = EnvironmentParser()
    import_algo_file = mocker.patch.object(__main__._run_input, "import_algo_file")

    __main__._run_input.broker = __main__._run_input.get_broker()
    __main__._run_input.executors = 0

    with pytest.raises(EnvironmentError, match="neither service_instance or backtest-id defined"):
        __main__.run_foreverbull(__main__._run_input)

    import_algo_file.assert_called_once()
