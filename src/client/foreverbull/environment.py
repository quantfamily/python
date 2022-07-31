import argparse
import importlib
import os
import socket

from foreverbull_core.broker import Broker
from foreverbull_core.models.service import Instance as ServiceInstance


class EnvironmentError(Exception):
    pass


class EnvironmentParser:
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

    @staticmethod
    def get_backtest_id(args: argparse.Namespace) -> str:
        backtest_id = os.environ.get("BACKTEST_ID")
        if args.backtest_id:
            backtest_id = args.backtest_id
        return backtest_id

    @staticmethod
    def get_service_instance(broker: Broker) -> ServiceInstance:
        service_id = os.environ.get("SERVICE_ID")
        instance_id = os.environ.get("INSTANCE_ID")
        if service_id is None or instance_id is None:
            return None
        host = os.environ.get("LOCAL_HOST", socket.gethostbyname(socket.gethostname()))
        return ServiceInstance(id=instance_id, service_id=service_id, host=host, port=broker.socket_config.port)

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("ALGO_FILE", help="you python- file to run", metavar="[your_file.py]")
        parser.add_argument("--executors", help="Number of Executors", default="1")
        parser.add_argument("--backtest-id", help="id of backtest")

    def parse(self, args: argparse.Namespace) -> None:
        self.algo_file = args.ALGO_FILE
        self.executors = int(args.executors)
        self.broker = EnvironmentParser.get_broker()
        self.backtest_id = EnvironmentParser.get_backtest_id(args)
        self.service_instance = EnvironmentParser.get_service_instance(self.broker)
        return

    def import_algo_file(self) -> None:
        if not self.algo_file:
            raise EnvironmentError("missing algo file")
        try:
            importlib.import_module(self.algo_file.replace("/", ".").split(".py")[0])
        except ModuleNotFoundError as e:
            raise EnvironmentError(str(e))
