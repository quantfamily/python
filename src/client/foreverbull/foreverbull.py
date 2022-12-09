import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

from foreverbull_core.models.socket import Request, Response
from foreverbull_core.socket.client import ContextClient, SocketClient, SocketConfig
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter

from foreverbull.models import OHLC, Configuration


class Foreverbull(threading.Thread):
    _worker_routes = {}

    def __init__(self, socket_config: SocketConfig = None, executors: int = 1):
        self.socket_config = socket_config
        self.running = False
        self.logger = logging.getLogger(__name__)
        self._worker_requests = Queue()
        self._worker_responses = Queue()
        self._workers = []
        self.executors = executors
        self._routes = MessageRouter()
        self._routes.add_route(self.stop, "backtest_completed")
        self._routes.add_route(self._configure, "configure", Configuration)
        self._routes.add_route(self._stock_data, "stock_data", OHLC)
        self._request_thread: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
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
        self.logger.info(f"CONFIG: {self.socket_config}")
        socket = SocketClient(self.socket_config)
        while self.running:
            try:
                self.logger.info("Getting context socket")
                context_socket = socket.new_context()
                self.logger.info("Context socket recieved")
                request = context_socket.recv()
                response = self._process_request(request)
                context_socket.send(response)
                context_socket.close()
            except SocketTimeout:
                pass
            except SocketClosed as exc:
                self.logger.exception(exc)
                self.logger.info("main socket closed, exiting")
                return
        self.logger.info("exiting")

    def _process_request(self, request: Request) -> Response:
        try:
            self.logger.debug(f"recieved task: {request.task}")
            return self._routes(request)
        except (SocketTimeout, SocketClosed) as exc:
            self.logger.warning(f"Unable to process context socket: {exc}")
            pass
        except Exception as exc:
            self.logger.error("unknown excetion when processing context socket")
            self.logger.exception(exc)

    def stop(self):
        self.logger.info("Stopping instance")
        self.running = False
        for worker in self._workers:
            worker.stop()
        self._workers = []

    def _configure(self, instance_configuration: Configuration):
        for _ in range(self.executors):
            w = WorkerHandler(instance_configuration, **self._worker_routes)
            self._workers.append(w)
        return

    def _stock_data(self, message: OHLC):
        if not self._workers:
            raise Exception("workers are not initialized")

        for worker in self._workers:
            # TODO: Fix a way to acquire first from pool of workers
            if worker.acquire(blocking=True):
                break

        try:
            worker.process(message)
        except Exception as exc:
            self.logger.error("Error processing to worker")
            self.logger.exception(exc)

        worker.release()
