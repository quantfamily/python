import logging
import threading

from foreverbull.models import Configuration
from foreverbull.worker import WorkerPool
from foreverbull_core.socket.client import SocketClient, SocketConfig
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter


class Foreverbull(threading.Thread):
    _worker_routes = {}

    def __init__(self, socket_config: SocketConfig = None, worker_pool: WorkerPool = None):
        self.socket_config = socket_config
        self.running = False
        self._worker_pool: WorkerPool = worker_pool
        self.logger = logging.getLogger(__name__)
        self._routes = MessageRouter()
        self._routes.add_route(self.stop, "stop")
        self._routes.add_route(self.configure, "configure", Configuration)
        self._routes.add_route(self.run_backtest, "run_backtest")
        threading.Thread.__init__(self)

    @staticmethod
    def on(msg_type):
        def decorator(t):
            Foreverbull._worker_routes[msg_type] = t
            return t

        return decorator

    def run(self):
        self.running = True
        self.logger.info("Starting instance")
        socket = SocketClient(self.socket_config)
        context_socket = None
        self.logger.info("Listening on {}:{}".format(self.socket_config.host, self.socket_config.port))
        while self.running:
            try:
                self.logger.info("Getting context socket")
                context_socket = socket.new_context()
                self.logger.info("Context socket recieved")
                request = context_socket.recv()
                response = self._routes(request)
                context_socket.send(response)
                context_socket.close()
            except SocketTimeout:
                context_socket.close()
            except SocketClosed as exc:
                self.logger.exception(exc)
                self.logger.info("main socket closed, exiting")
        socket.close()
        self.logger.info("exiting")

    def configure(self, configuration: Configuration) -> None:
        self.logger.info("Configuring instance")
        self._worker_pool.configure(configuration)
        return None

    def run_backtest(self):
        self.logger.info("Running backtest")
        self._worker_pool.run_backtest()

    def stop(self):
        self.logger.info("Stopping instance")
        if self._worker_pool:
            self._worker_pool.stop()
        self.running = False
