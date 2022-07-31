from unittest.mock import create_autospec

import pytest

from foreverbull_core.models.base import Base
from foreverbull_core.models.socket import Request, Response
from foreverbull_core.socket.router import MessageRouter, TaskAlreadyExists


class DemoModel(Base):
    name: str


def demo_function():
    pass


def demo_function_with_model(demo: DemoModel):
    pass


def error_function():
    raise Exception("this does not work")


def test_add_route():
    router = MessageRouter()
    router.add_route(demo_function, "demo")

    assert "demo" in router._routes
    assert demo_function == router._routes["demo"].func


def test_add_route_with_model():
    router = MessageRouter()
    router.add_route(demo_function_with_model, "demo", DemoModel)

    assert "demo" in router._routes
    assert DemoModel == router._routes["demo"].model


def test_add_route_already_exists():
    router = MessageRouter()
    router.add_route(demo_function_with_model, "demo", DemoModel)
    with pytest.raises(TaskAlreadyExists, match="demo already registered"):
        router.add_route(demo_function_with_model, "demo", DemoModel)


def test_call():
    mock_func = create_autospec(demo_function)

    router = MessageRouter()
    router.add_route(mock_func, "demo")

    req = Request(task="demo")
    rsp = router(req)

    mock_func.assert_called_once()
    assert type(rsp) == Response


def test_call_with_model():
    mock_func = create_autospec(demo_function_with_model)

    router = MessageRouter()
    router.add_route(mock_func, "demo", DemoModel)

    data = DemoModel(name="best")
    req = Request(task="demo", data=data)
    rsp = router(req)

    mock_func.assert_called_once()
    mock_func.assert_called_once_with(data)
    assert type(rsp) == Response


def test_call_not_exists():
    router = MessageRouter()

    req = Request(task="demo")
    rsp = router(req)

    assert rsp.error == "task not found"
    assert type(rsp) == Response


def test_call_error_function():
    router = MessageRouter()
    router.add_route(error_function, "do_error")

    req = Request(task="do_error")
    rsp = router(req)
    assert rsp.error is not None
    assert rsp.error == "Exception('this does not work')"
