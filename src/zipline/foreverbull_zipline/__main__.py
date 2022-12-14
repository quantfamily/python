import argparse
import logging
import os
import signal
import socket
import time

import foreverbull_core.logger
from foreverbull_core.broker import Broker
from foreverbull_zipline.app import Application

log = logging.getLogger()

parser = argparse.ArgumentParser(prog="zipline-foreverbull")
parser.add_argument("--broker-url", help="URL of broker")
parser.add_argument("--local-host", help="Local Address")
parser.add_argument("--service-id", help="Service ID")
parser.add_argument("--instance-id", help="Instance ID")


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


def run_application(application: Application):
    application.start()
    try:
        while application.running:
            time.sleep(1)
    except KeyboardInterrupt:
        application.stop()
    application.join()


if __name__ == "__main__":
    foreverbull_core.logger.Logger()
    args = parser.parse_args()
    broker = get_broker(args)
    application = Application(broker.socket_config)
    broker.http.service.update_instance(
        os.environ.get("SERVICE_NAME"), socket.gethostname(), broker.socket_config, True
    )
    signal.signal(signal.SIGTERM, application.stop)
    log.info("starting application")
    run_application(application)
    log.info("ending application")
    broker.http.service.update_instance(
        os.environ.get("SERVICE_NAME"), socket.gethostname(), broker.socket_config, False
    )
