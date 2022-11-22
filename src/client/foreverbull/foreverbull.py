import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Queue

from foreverbull_core.models.socket import Request
from foreverbull_core.socket.client import ContextClient, SocketClient
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter

from foreverbull.models import OHLC, Configuration
from foreverbull.worker.worker import WorkerHandler


class Foreverbull(threading.Thread):
    _worker_routes = {}

    def __init__(self, socket: SocketClient = None, executors: int = 1):
        self.socket = socket
        self.running = False
        self.logger = logging.getLogger(__name__)
        self._worker_requests = Queue()
        self._worker_responses = Queue()
        self._workers: list[WorkerHandler] = []
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
        while self.running:
            try:
                context_socket = self.socket.new_context()
                request = context_socket.recv()
                self._request_thread.submit(self._process_request, context_socket, request)
            except SocketTimeout:
                pass
            except SocketClosed as exc:
                self.logger.exception(exc)
                self.logger.info("main socket closed, exiting")
                return
        self.logger.info("exiting")

    def _process_request(self, socket: ContextClient, request: Request):
        try:
            self.logger.debug(f"recieved task: {request.task}")
            response = self._routes(request)
            socket.send(response)
            self.logger.debug(f"reply sent for task: {response.task}")
            socket.close()
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
