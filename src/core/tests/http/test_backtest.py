import pytest
import requests
import requests_mock
from foreverbull_core.http import RequestError
from foreverbull_core.http.backtest import Backtest
from foreverbull_core.models.backtest import Session


@pytest.fixture(scope="function")
def backtest_session():
    def setup():
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount("http://", adapter)
        backtest = Backtest("127.0.0.1:8080", session=session)
        return backtest, adapter

    return setup


def test_list_backtests(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/backtests", json=[])
    rsp = backtest.list()
    assert rsp == []


def test_list_backtests_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/backtests", json=[], status_code=500)
    with pytest.raises(RequestError, match="get call /backtests gave bad return code: 500"):
        backtest.list()


def test_delete_backtest(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/backtests/backtest_id")
    backtest.delete("backtest_id")


def test_delete_backtest_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/backtests/backtest_id", status_code=500)
    with pytest.raises(RequestError, match="delete call /backtests/backtest_id gave bad return code: 500"):
        backtest.delete("backtest_id")


def test_list_sessions(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/backtests/backtest_id/sessions", json=[])
    assert backtest.list_sessions("backtest_id") == []


def test_list_sessions_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/backtests/backtest_id/sessions", status_code=500)
    with pytest.raises(RequestError, match="get call /backtests/backtest_id/sessions gave bad return code: 500"):
        backtest.list_sessions("backtest_id")


def test_create_session(backtest_session):
    backtest, adapter = backtest_session()
    to_create = Session(backtest_id="backtest_id", worker_count=1)
    created = Session(id="session_id", backtest_id="backtest_id", worker_count=1, run_automaticlly=False)
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/backtests/backtest_id/sessions", json=created.dict())
    assert backtest.create_session("backtest_id", to_create) == created


def test_create_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    to_create = Session(backtest_id="backtest_id", worker_count=1)
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/backtests/backtest_id/sessions", status_code=500)
    with pytest.raises(RequestError, match="post call /backtests/backtest_id/sessions gave bad return code: 500"):
        backtest.create_session("backtest_id", to_create)


def test_get_session(backtest_session):
    backtest, adapter = backtest_session()
    session = Session(id="session_id", backtest_id="backtest_id", worker_count=1, run_automaticlly=False)

    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/backtests/b_id/sessions/s_id", json=session.dict())
    assert backtest.get_session("b_id", "s_id") == session


def test_get_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/backtests/1/sessions/1", status_code=500)
    with pytest.raises(RequestError, match="get call /backtests/1/sessions/1 gave bad return code: 500"):
        backtest.get_session(1, 1)


def test_delete_session(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/backtests/b_id/sessions/s_id")
    assert backtest.delete_session("b_id", "s_id") is None


def test_delete_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/backtests/b_id/sessions/s_id", status_code=500)
    with pytest.raises(RequestError, match="delete call /backtests/b_id/sessions/s_id gave bad return code: 500"):
        backtest.delete_session("b_id", "s_id")


def test_run_session(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/backtests/b_id/sessions/s_id/run")
    assert backtest.run_session("b_id", "s_id") is None


def test_run_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/backtests/b_id/sessions/s_id/run", status_code=500)
    with pytest.raises(RequestError, match="post call /backtests/b_id/sessions/s_id/run gave bad return code: 500"):
        backtest.run_session("b_id", "s_id")


def test_stop_session(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/backtests/b_id/sessions/s_id/stop")
    assert backtest.stop_session("b_id", "s_id") is None


def test_stop_session_negative(backtest_session):
    backtest, adapter = backtest_session()
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/backtests/b_id/sessions/s_id/stop", status_code=500)
    with pytest.raises(RequestError, match="post call /backtests/b_id/sessions/s_id/stop gave bad return code: 500"):
        backtest.stop_session("b_id", "s_id")
