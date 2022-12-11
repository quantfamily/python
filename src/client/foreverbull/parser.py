import argparse
import importlib
import os
import socket

from foreverbull_core.broker import Broker


class ParserError(Exception):
    pass


class Parser:
    def __init__(self) -> None:
        self.algo_file = None
        self.broker = None
        self.backtest_id = None
        self.service_instance = None

    @staticmethod
    def get_broker() -> Broker:
        broker_url = os.environ.get("BROKER_URL", "127.0.0.1:8080")
        local_host = os.environ.get("LOCAL_HOST", socket.gethostbyname(socket.gethostname()))
        return Broker(broker_url, local_host)

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("ALGO_FILE", help="you python- file to run", metavar="[your_file.py]")
        parser.add_argument("--executors", help="Number of Executors", default="1")

    def import_algo_file(self) -> None:
        if not self.algo_file:
            raise ParserError("missing algo file")
        try:
            importlib.import_module(self.algo_file.replace("/", ".").split(".py")[0])
        except ModuleNotFoundError as e:
            raise ParserError(str(e))

    def parse(self, args: argparse.Namespace) -> None:
        self.algo_file = args.ALGO_FILE
        return self.import_algo_file()
