from datetime import datetime
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from foreverbull.environment import EnvironmentError, EnvironmentParser
from foreverbull.foreverbull import Foreverbull
from foreverbull.models import Configuration


def test_on():
    route = Foreverbull.on("stock_data")
    route("hello")
    assert "stock_data" in Foreverbull._worker_routes
    assert Foreverbull._worker_routes["stock_data"] == "hello"


def test_setup_worker():
    pyfile = """
from foreverbull import Foreverbull

@Foreverbull.on("magic_data")
def magic_func(*args):
    pass
    """

    demo_file = Path("demo.py")
    with open(demo_file.name, "w") as fw:
        fw.write(pyfile)
    input = EnvironmentParser()
    input.algo_file = demo_file.name
    input.import_algo_file()

    assert "magic_data" in Foreverbull._worker_routes
    demo_file.unlink()
    Foreverbull._worker_routes = {}


def test_setup_worker_negative():
    input_parser = EnvironmentParser()

    with pytest.raises(EnvironmentError):
        input_parser.import_algo_file()

    with pytest.raises(EnvironmentError):
        input_parser.algo_file = "non_file.py"
        input_parser.import_algo_file()


def test_configure_and_completed():
    configuration = Configuration(
        execution_id="123", execution_start_date=datetime.now(), execution_end_date=datetime.now(), parameters=[]
    )
    fb = Foreverbull()
    Foreverbull._worker_routes = {}
    fb.executors = 2
    fb._configure(configuration)
    assert len(fb._workers) == 2
    fb.stop()
    assert len(fb._workers) == 0


def test_start_stop(mocker: MockerFixture):
    input = EnvironmentParser()
    broker = input.get_broker()
    fb = Foreverbull(broker.socket, 1)

    fb.start()
    fb.stop()
    fb.join()
