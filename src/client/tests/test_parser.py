import socket
from argparse import ArgumentParser

import pytest
from _pytest.monkeypatch import MonkeyPatch
from foreverbull.parser import Parser, ParserError


def test_get_broker_defaults():
    broker = Parser.get_broker()
    assert "127.0.0.1:8080" == broker._broker_host
    assert socket.gethostbyname(socket.gethostname()) == broker._local_host


def test_get_broker_env(monkeypatch: MonkeyPatch):
    monkeypatch.setenv("BROKER_URL", "foreverbull.com")
    monkeypatch.setenv("LOCAL_HOST", "localhost")
    broker = Parser.get_broker()
    assert "foreverbull.com" == broker._broker_host
    assert "localhost" == broker._local_host


def test_add_arguments():
    parser = ArgumentParser()
    input_parser = Parser()
    input_parser.add_arguments(parser)


def test_import_algo_file(algo_file):
    input_parser = Parser()

    input_parser.algo_file = algo_file
    input_parser.import_algo_file()


def test_import_algo_file_missing():
    input_parser = Parser()
    with pytest.raises(ParserError):
        input_parser.import_algo_file()


def test_parse(algo_file):
    args = [algo_file]
    parser = ArgumentParser()
    input_parser = Parser()
    input_parser.add_arguments(parser)
    args = parser.parse_args(args)
    input_parser.parse(args)

    assert algo_file == input_parser.algo_file


def test_parse_missing():
    args = []

    parser = ArgumentParser()
    input_parser = Parser()
    input_parser.add_arguments(parser)
    with pytest.raises(SystemExit) as e:
        args = parser.parse_args(args)

    assert 2 == e.value.code
