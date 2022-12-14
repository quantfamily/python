import logging
import os
from multiprocessing import Event, Process, set_start_method
from threading import Thread

from foreverbull.data import Database, DateManager
from foreverbull.models import OHLC, Configuration
from foreverbull.worker.exceptions import WorkerException
from foreverbull_core.models.socket import Response
from foreverbull_core.models.worker import Parameter
from foreverbull_core.socket.client import SocketClient
from foreverbull_core.socket.exceptions import SocketTimeout

set_start_method("spawn")

class Worker:
    def __init__(self, configuration: Configuration, stop_event: Event, **routes):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("setting up worker")
        self._routes = routes
        self.execution_id = configuration.execution_id
        self.date: DateManager = DateManager(configuration.execution_start_date, configuration.execution_end_date)
        self.logger.debug("setting up database connection")
        self.database: Database = Database(
            execution_id=configuration.execution_id, date_manager=self.date, db_conf=configuration.database
        )
        self.parameters = {}
        if configuration.parameters:
            self.logger.debug("setting up parameters")
            self._setup_parameters(*configuration.parameters)
        self.configuration = configuration
        self.stop_event = stop_event
        self.logger.info("worker configured correctly")
        super(Worker, self).__init__()

    def _setup_parameters(self, *parameters: Parameter):
        for parameter in parameters:
            self.logger.debug("Setting %s to %s", parameter.key, parameter.value)
            self.parameters[parameter.key] = parameter.value

    def _process_request(self, ohlc: OHLC):
        self.logger.debug("sending request to worker")
        self.date.current = ohlc.time
        try:
            return self._routes["ohlc"](ohlc, self.database, **self.parameters)
        except KeyError:
            self.logger.info(ohlc)
            return None

    def run(self):
        self.logger.info(f"starting worker, {self.configuration.socket}")
        socket = SocketClient(self.configuration.socket)
        self.database.connect()
        while True:
            try:
                self.logger.info("Getting context socket")
                context_socket = socket.new_context()
                self.logger.info("Getting request")
                request = context_socket.recv()
                response = self._process_request(OHLC(**request.data))
                context_socket.send(Response(task=request.task, data=response))
                context_socket.close()
            except SocketTimeout:
                pass
            except Exception as e:
                self.logger.exception(repr(e))
                raise WorkerException(repr(e))
            if self.stop_event.is_set():
                self.logger.info("stopping worker")
                context_socket.close()
                socket.close()
                break


class WorkerThread(Worker, Thread):
    pass


class WorkerProcess(Worker, Process):
    pass


class WorkerPool:
    def __init__(self, configuration: Configuration, **routes):
        self.logger = logging.getLogger(__name__)
        self._workers = []
        self._configuration = configuration
        self._routes = routes
        self._worker_stop_event = Event()

    def start(self):
        self.logger.info("starting workers")
        self.logger.info(f"connecting to: {self._configuration.socket.host}:{self._configuration.socket.port}")
        for i in range(4):  # Hardcode to 4 workers for now
            self.logger.info("starting worker %s", i)
            if os.getenv("THREADED_EXECUTION"):
                worker = WorkerThread(self._configuration, self._worker_stop_event, **self._routes)
            else:
                worker = WorkerProcess(self._configuration, self._worker_stop_event, **self._routes)
            worker.start()
            self._workers.append(worker)

    def stop(self):
        self.logger.info("stopping workers")
        self._worker_stop_event.set()
        for worker in self._workers:
            worker.join()
