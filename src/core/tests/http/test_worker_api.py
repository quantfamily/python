import pytest
import requests
import requests_mock

from foreverbull_core.http import RequestError
from foreverbull_core.http.worker import Worker
from foreverbull_core.models import worker


@pytest.fixture(scope="function")
def worker_session():
    def setup():
        session = requests.Session()
        adapter = requests_mock.Adapter()
        session.mount("http://", adapter)
        worker = Worker("127.0.0.1:8080", session=session)
        return worker, adapter

    return setup


def test_list_workers(worker_session):
    worker, adapter = worker_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/workers", json=[])
    assert worker.list() == []


def test_list_workers_populated(worker_session):
    worker_api, adapter = worker_session()
    worker_list = [worker.Config(id="worker_id", name="super_worker").dict()]
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/workers", json=worker_list)
    assert worker_api.list() == worker_list


def test_create_worker(worker_session):
    worker_api, adapter = worker_session()
    to_create = worker.Config(service_id="service_id", name="demoWorker")
    created = worker.Config(id="worker_id", service_id="service_id", name="demoWorker")
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/workers", json=created.dict())
    assert worker_api.create(to_create) == created


def test_create_worker_negative(worker_session):
    worker_api, adapter = worker_session()
    to_create = worker.Config(service_id="service_id", name="demoWorker")
    adapter.register_uri("POST", "http://127.0.0.1:8080/api/v1/workers", status_code=409)
    with pytest.raises(RequestError, match="post call /workers gave bad return code: 409"):
        worker_api.create(to_create)


def test_get_worker(worker_session):
    worker_api, adapter = worker_session()
    to_get = worker.Config(id="worker_id", service_id="service_id", name="demoWorker")
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/workers/worker_id", json=to_get.dict())
    assert worker_api.get("worker_id") == to_get


def test_get_worker_negative(worker_session):
    worker_api, adapter = worker_session()
    adapter.register_uri("GET", "http://127.0.0.1:8080/api/v1/workers/worker_id", status_code=404)
    with pytest.raises(RequestError, match="get call /workers/worker_id gave bad return code: 404"):
        worker_api.get("worker_id")


def test_update_worker(worker_session):
    worker_api, adapter = worker_session()
    updated = worker.Config(id="worker_id", service_id="service_id", name="demoWorker")
    adapter.register_uri("PUT", "http://127.0.0.1:8080/api/v1/workers/worker_id", json=updated.dict())
    assert worker_api.update("worker_id", updated) == updated


def test_update_worker_negative(worker_session):
    worker_api, adapter = worker_session()
    updated = worker.Config(id="worker_id", service_id="service_id", name="demoWorker")
    adapter.register_uri("PUT", "http://127.0.0.1:8080/api/v1/workers/worker_id", status_code=409)
    with pytest.raises(RequestError, match="put call /workers/worker_id gave bad return code: 409"):
        worker_api.update("worker_id", updated)


def test_delete_worker(worker_session):
    worker_api, adapter = worker_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/workers/worker_id")
    assert worker_api.delete("worker_id") is None


def test_delete_worker_negative(worker_session):
    worker_api, adapter = worker_session()
    adapter.register_uri("DELETE", "http://127.0.0.1:8080/api/v1/workers/worker_id", status_code=404)
    with pytest.raises(RequestError, match="delete call /workers/worker_id gave bad return code: 404"):
        worker_api.delete("worker_id")
