import argparse
import logging
import os
import socket
import time

import foreverbull_core.logger
from foreverbull import Foreverbull
from foreverbull.parser import Parser
from foreverbull_core import cli

_service_input = cli.ServiceInput()
_backtets_input = cli.BacktestInput()
_worker_input = cli.WorkerInput()
client_parser = Parser()

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest="option")

system = subparser.add_parser("service", help="service")
_service_input.add_arguments(system)
backtest = subparser.add_parser("backtest", help="backtest")
_backtets_input.add_arguments(backtest)
worker = subparser.add_parser("worker", help="worker")
_worker_input.add_arguments(worker)
run = subparser.add_parser("run", help="run algo")
client_parser.add_arguments(run)


def run_foreverbull(client_parser: Parser):
    broker = client_parser.get_broker()
    fb = Foreverbull(broker.socket_config)
    client_parser.import_algo_file()
    fb.start()

    while not broker.socket_config.port:
        time.sleep(0.2)

    try:
        broker.http.service.update_instance(
            os.environ.get("SERVICE_NAME"), socket.gethostname(), broker.socket_config, True
        )
    except Exception as e:
        logging.error(f"unable to call backend: {repr(e)}")
        fb.stop()
        return

    try:
        while fb.running:
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Keyboard- Interrupt recieved exiting")

    fb.stop()

    broker.http.service.update_instance(
        os.environ.get("SERVICE_NAME"), socket.gethostname(), broker.socket_config, False
    )


def main():
    foreverbull_core.logger.Logger()
    args = parser.parse_args()
    try:
        if args.option == "run":
            client_parser.parse(args)
            run_foreverbull(client_parser)
        elif args.option == "service":
            _service_input.parse(args)
        elif args.option == "backtest":
            _backtets_input.parse(args)
        elif args.option == "worker":
            _worker_input.parse(args)
        else:
            parser.print_help()
    except Exception as e:
        print(e)
        parser.print_help()


if __name__ == "__main__":
    main()
