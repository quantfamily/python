import argparse
import logging
import os
import socket
import time

import foreverbull_core.logger
from foreverbull import Foreverbull
from foreverbull.environment import EnvironmentParser
from foreverbull_core import cli
from foreverbull_core.broker import Broker
from foreverbull_core.models.backtest import Session
from foreverbull_core.models.service import RawConnection

_service_input = cli.ServiceInput()
_backtets_input = cli.BacktestInput()
_worker_input = cli.WorkerInput()
_env = EnvironmentParser()

parser = argparse.ArgumentParser()
subparser = parser.add_subparsers(dest="option")

system = subparser.add_parser("service", help="service")
_service_input.add_arguments(system)
backtest = subparser.add_parser("backtest", help="backtest")
_backtets_input.add_arguments(backtest)
worker = subparser.add_parser("worker", help="worker")
_worker_input.add_arguments(worker)
run = subparser.add_parser("run", help="run algo")
_env.add_arguments(run)


def sleep_till_keyboard_interrupt(fb: Foreverbull):
    print("IS RUNNING: ", fb.running)
    try:
        while fb.running:
            print("sleeping")
            time.sleep(0.5)
    except KeyboardInterrupt:
        logging.info("Keyboard- Interrupt recieved exiting")


def run_foreverbull(env: EnvironmentParser):
    fb = Foreverbull(env.broker.socket, env.executors)
    env.import_algo_file()
    fb.start()

    try:
        if True:
            env.broker.http.service.update_instance(
                os.environ.get("SERVICE_NAME"), socket.gethostname(), env.broker.socket_config, True
            )
        elif input.backtest_id:
            session = Session(backtest_id=env.backtest_id, worker_count=0, run_automaticlly=False)
            conn = RawConnection(host=env.broker._local_host, port=_env.broker.socket.config.port)
            session = env.broker.http.backtest.create_session(env.backtest_id, session=session)
            env.broker.http.backtest.setup_session(session.backtest_id, session.id)
            env.broker.http.backtest.configure_session(session.backtest_id, session.id, conn)
            env.broker.http.backtest.run_session(session.backtest_id, session.id)
    except Exception as e:
        logging.error(f"unable to call backend: {repr(e)}")
        fb.stop()
        return

    sleep_till_keyboard_interrupt(fb)
    fb.stop()

    if True:
        env.broker.http.service.update_instance(
            os.environ.get("SERVICE_NAME"), socket.gethostname(), env.broker.socket_config, False
        )
    else:
        _env.broker.http.backtest.stop_session(session.backtest_id, session.id)


def get_broker(args: argparse.Namespace) -> Broker:
    if args.broker_url:
        broker_url = args.broker_url
    else:
        broker_url = os.environ.get("BROKER_URL", "127.0.0.1:8080")
    if args.local_host:
        local_host = args.local_host
    else:
        local_host = os.environ.get("LOCAL_HOST", socket.gethostbyname(socket.gethostname()))

    return Broker(broker_url, local_host)


def main():
    foreverbull_core.logger.Logger()
    args = parser.parse_args()
    try:
        if args.option == "run":
            _env.parse(args)
            run_foreverbull(_env)
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
