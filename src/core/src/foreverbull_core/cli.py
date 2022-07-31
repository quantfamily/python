import argparse
import json
from typing import List

from foreverbull_core.http.backtest import Backtest
from foreverbull_core.http.service import Service
from foreverbull_core.http.worker import Worker
from foreverbull_core.models import backtest, service, worker


class CLI:
    def __init__(self, argparser: argparse.ArgumentParser = None):
        if argparser is None:
            argparser = argparse.ArgumentParser()
        self.argparser = argparser

    def add_parsers(self):
        self.argparser.add_argument("--broker", default="http://127.0.0.1:8080/")
        core = self.argparser.add_subparsers(dest="core_option")
        service_arg = core.add_parser("service", help="create, list or delete  Services")
        self.service = ServiceInput()
        self.service.add_arguments(service_arg)
        backtest_arg = core.add_parser("backtest", help="create, list or delete backtest")
        self.backtest = BacktestInput()
        self.backtest.add_arguments(backtest_arg)
        worker_arg = core.add_parser("worker", help="create, list or delete workers")
        self.worker = WorkerInput()
        self.worker.add_arguments(worker_arg)

    def parse(self, args: argparse.Namespace):
        if args.core_option == "service":
            self.service.parse(args)
        if args.core_option == "backtest":
            self.backtest.parse(args)
        if args.core_option == "worker":
            self.worker.parse(args)


class ServiceInput:
    def __init__(self) -> None:
        pass

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--broker-url", help="url of foreverbull broker", default="127.0.0.1:8080")
        subparser = parser.add_subparsers(dest="system_option", help="system options")
        create = subparser.add_parser("create", help="Create a new Service")
        create.add_argument("--name", required=True, help="Name of Service")
        create.add_argument("--image", required=True, help="Image-name (docker image)")
        create.add_argument("--type", required=True, choices=["backtest", "worker"])
        subparser.add_parser("list", help="List stored services")
        delete = subparser.add_parser("delete", help="Delete a Service")
        delete.add_argument("--id", required=True, help="Service-ID of service")

    def parse(self, args: argparse.Namespace):
        if args.system_option == "create":
            self._create_service(args)
        if args.system_option == "list":
            self._list_services(args)
        if args.system_option == "delete":
            self._delete_service(args)

    def _create_service(self, args: argparse.Namespace):
        api = Service(args.broker_url)
        model = service.Service(name=args.name, image=args.image, type=args.type)
        print(api.create(model))

    def _list_services(self, args: argparse.Namespace):
        api = Service(args.broker_url)
        for stored_service in api.list():
            print(stored_service)

    def _delete_service(self, args: argparse.Namespace):
        api = Service(args.broker_url)
        print(api.delete(args.id))


class BacktestInput:
    def __init__(self) -> None:
        pass

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--broker-url", help="url of foreverbull broker", default="127.0.0.1:8080")
        subparser = parser.add_subparsers(dest="backtest_option", help="backtest options")
        subparser.add_parser("list", help="list stored backtests")
        create = subparser.add_parser("create", help="create backtest")
        create.add_argument("--service-id", help="id of backtest- service", required=True)
        create.add_argument("--name", help="name of backtest", required=True)
        create.add_argument("--config", help="config of backtest(expects json filename)", required=True)
        delete = subparser.add_parser("delete", help="delete backtest")
        delete.add_argument("--id", help="id of backtest", required=True)

    def parse(self, args: argparse.Namespace) -> None:
        if args.backtest_option == "list":
            self._list_backtests(args)
        if args.backtest_option == "create":
            self._create_backtest(args)
        if args.backtest_option == "delete":
            self._delete_backtest(args)

    def _list_backtests(self, args: argparse.Namespace) -> None:
        api = Backtest(args.broker_url)
        for stored_backtest in api.list():
            print(stored_backtest)

    def _create_backtest(self, args: argparse.Namespace) -> None:
        api = Backtest(args.broker_url)
        config = None
        with open(args.config, "r") as fr:
            config = json.loads(fr.read())
        model = backtest.Config(service_id=args.service_id, name=args.name, config=config)
        print(api.create(model))

    def _delete_backtest(self, args: argparse.Namespace) -> None:
        api = Backtest(args.broker_url)
        print(api.delete(args.id))


class WorkerInput:
    def __init__(self) -> None:
        pass

    def add_arguments(self, parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--broker-url", help="url of foreverbull broker", default="http://127.0.0.1:8080")
        subparser = parser.add_subparsers(dest="worker_option", help="Worker Options")
        subparser.add_parser("list", help="list workers")
        create = subparser.add_parser("create", help="create worker")
        create.add_argument("--service-id", help="service id of the worker", required=True)
        create.add_argument("--name", help="name of the worker", required=True)
        create.add_argument("--parameters", nargs="+", help="parameters in format [key=value key=value key=value]")
        delete = subparser.add_parser("delete", help="delete worker")
        delete.add_argument("--id", required=True)

    def parse(self, args: argparse.Namespace) -> None:
        if args.worker_option == "list":
            self._list_workers(args)
        if args.worker_option == "create":
            self._create_worker(args)
        if args.worker_option == "delete":
            self._delete_worker(args)

    def _list_workers(self, args: argparse.ArgumentParser) -> None:
        api = Worker(args.broker_url)
        for stored_worker in api.list():
            print(stored_worker)

    def _parse_worker_parameters(self, string_parameters: List[str]) -> dict:
        params = []
        for param in string_parameters:
            key, default = param.split("=")
            params.append(worker.Parameter(key=key, default=int(default)))
        return params

    def _create_worker(self, args: argparse.ArgumentParser) -> None:
        api = Worker(args.broker_url)
        parameters = []
        if args.parameters:
            parameters = self._parse_worker_parameters(args.parameters)
        model = worker.Config(service_id=args.service_id, name=args.name, parameters=parameters)
        print(api.create(model))

    def _delete_worker(self, args: argparse.ArgumentParser) -> None:
        api = Worker(args.broker_url)
        print(api.delete(args.id))
