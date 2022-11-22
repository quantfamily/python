import os
import socket
from argparse import ArgumentParser

import pytest
from _pytest.monkeypatch import MonkeyPatch

from foreverbull.environment import EnvironmentError, EnvironmentParser


def test_get_broker_defaults():
    broker = EnvironmentParser.get_broker()
    assert "127.0.0.1:8080" == broker._broker_host
    assert socket.gethostbyname(socket.gethostname()) == broker._local_host


def test_get_broker_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("BROKER_URL", "foreverbull.com")
    monkeypatch.setenv("LOCAL_HOST", "localhost")
    broker = EnvironmentParser.get_broker()
    assert "foreverbull.com" == broker._broker_host
    assert "localhost" == broker._local_host


def test_get_backtest_id_env(monkeypatch: MonkeyPatch):
    parser = ArgumentParser()
    input_parser = EnvironmentParser()
    input_parser.add_arguments(parser)
    args = parser.parse_args(["file.py"])

    monkeypatch.setenv("BACKTEST_ID", "the-backtest-id")
    backtest_id = EnvironmentParser.get_backtest_id(args)
    assert "the-backtest-id" == backtest_id


def test_get_backtest_id_arg():
    args = ["file.py", "--backtest-id", "the-backtest-id"]
    parser = ArgumentParser()
    input_parser = EnvironmentParser()
    input_parser.add_arguments(parser)
    args = parser.parse_args(args)
    backtest_id = EnvironmentParser.get_backtest_id(args)
    assert "the-backtest-id" == backtest_id


def test_get_service_instance(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("SERVICE_ID", "the_service")
    monkeypatch.setenv("INSTANCE_ID", "the_instance")
    broker = EnvironmentParser.get_broker()
    service_instance = EnvironmentParser.get_service_instance(broker)
    assert "the_instance" == service_instance.id
    assert "the_service" == service_instance.service_id


def test_get_service_instance_missing_env():
    service_instance = EnvironmentParser.get_service_instance(EnvironmentParser.get_broker())
    assert service_instance is None


def test_add_arguments():
    parser = ArgumentParser()
    input_parser = EnvironmentParser()
    input_parser.add_arguments(parser)


def test_parse():
    args = ["The_file.py", "--backtest-id", "b1234"]

    parser = ArgumentParser()
    input_parser = EnvironmentParser()
    input_parser.add_arguments(parser)
    args = parser.parse_args(args)
    input_parser.parse(args)

    assert "The_file.py" == input_parser.algo_file
    assert "b1234" == input_parser.backtest_id


def test_parse_missing_():
    args = ["--backtest-id", "b1234"]

    parser = ArgumentParser()
    input_parser = EnvironmentParser()
    input_parser.add_arguments(parser)
    with pytest.raises(SystemExit) as e:
        args = parser.parse_args(args)

    assert 2 == e.value.code


def test_import_algo_file():
    py_code = """
import foreverbull

fb = foreverbull.Foreverbull()

@fb.on("stock_data")
def hello(*args, **kwargs):
    pass

"""
    input_parser = EnvironmentParser()
    with open("test_file.py", "w") as fw:
        fw.write(py_code)

    input_parser.algo_file = "test_file"
    input_parser.import_algo_file()

    os.remove("test_file.py")


def test_import_algo_file_missing():
    input_parser = EnvironmentParser()
    with pytest.raises(EnvironmentError):
        input_parser.import_algo_file()
