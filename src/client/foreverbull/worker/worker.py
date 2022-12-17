import logging
import os
from multiprocessing import Event, Process
from threading import Thread

import pynng
from foreverbull.data import Database, DateManager
from foreverbull.models import OHLC, Configuration
from foreverbull.worker.exceptions import WorkerException
from foreverbull_core.models.socket import Request, Response
from foreverbull_core.models.worker import Parameter
from foreverbull_core.socket.exceptions import SocketTimeout


class Worker:
    def __init__(self, survey_address: str, state_address: str, stop_event: Event, **routes):
        self.logger = logging.getLogger(__name__)
        self.logger.debug("setting up worker")
        self._survey_address = survey_address
        self._state_address = state_address
        self._stop_event = stop_event
        self._routes = routes
        self.logger.info("worker configured correctly")
        super(Worker, self).__init__()

    def _setup_parameters(self, *parameters: Parameter):
        for parameter in parameters:
            self.logger.debug("Setting %s to %s", parameter.key, parameter.value)
            self.parameters[parameter.key] = parameter.value

    def _process_ohlc(self, ohlc: OHLC):
        self.logger.debug("Processing OHLC: %s, %s", ohlc.isin, ohlc.time)
        self.date.current = ohlc.time
        try:
            return self._routes["ohlc"](ohlc, self.database)
        except KeyError:
            self.logger.error("No route for OHLC")
            return None

    def configure(self, configuration: Configuration):
        self.configuration = configuration
        self.logger.info("configuring worker")
        if configuration.parameters:
            self._setup_parameters(*configuration.parameters)
        self.date = DateManager(configuration.execution_start_date, configuration.execution_end_date)
        self.database = Database(configuration.execution_id, self.date, configuration.database)
        self.logger.info("worker configured correctly")

    def run(self):
        responder = pynng.Respondent0(dial=self._survey_address)
        responder.send_timeout = 10000
        responder.recv_timeout = 10000
        state = pynng.Pub0(dial=self._state_address)
        state.send(b"ready")
        self.logger.info("starting worker")
        while True:
            try:
                request = Request.load(responder.recv())
                self.logger.info("Received request")
                if request.task == "configure":
                    configuration = Configuration(**request.data)
                    self.configuration = configuration
                    self.configure(configuration)
                    responder.send(Response(task=request.task, error=None).dump())
                elif request.task == "run_backtest":
                    socket = pynng.Rep0(dial=f"tcp://{self.configuration.socket.host}:{self.configuration.socket.port}")
                    socket.recv_timeout = 500
                    socket.send_timeout = 500
                    responder.send(Response(task=request.task, error=None).dump())
                    self.run_backtest(socket)
                elif request.task == "stop":
                    responder.send(Response(task=request.task, error=None).dump())
                    responder.close()
                    state.close()
                    break
                else:
                    self.logger.info("Received unknown task")
                    responder.send(Response(task=request.task, error="Unknown task").dump())
            except pynng.exceptions.Timeout:
                pass
            except Exception as e:
                self.logger.exception(repr(e))
                responder.send(Response(task=request.task, error=repr(e)).dump())
                responder.close()
                state.close()
                raise WorkerException(repr(e))

    def run_backtest(self, socket: pynng.Req0):
        self.database.connect()
        while True:
            try:
                self.logger.info("Getting context socket")
                context_socket = socket.new_context()
                self.logger.info("Getting request")
                request = Request.load(context_socket.recv())
                response = self._process_ohlc(OHLC(**request.data))
                context_socket.send(Response(task=request.task, data=response).dump())
                context_socket.close()
            except (SocketTimeout, pynng.exceptions.Timeout):
                context_socket.close()
            except Exception as e:
                self.logger.exception(repr(e))
                raise WorkerException(repr(e))
            if self._stop_event.is_set():
                break
        socket.close()


class WorkerThread(Worker, Thread):
    pass


class WorkerProcess(Worker, Process):
    pass


class WorkerPool:
    def __init__(self, **routes):
        self.logger = logging.getLogger(__name__)
        self._workers = []
        self._routes = routes
        self._executors = 2
        self._stop_workers_event = Event()
        self._survey_address = "ipc:///tmp/worker_pool.ipc"
        self._state_address = "ipc:///tmp/worker_states.ipc"
        self.survey = pynng.Surveyor0(listen=self._survey_address)
        self.worker_states = pynng.Sub0(listen=self._state_address)
        self.worker_states.subscribe(b"")
        self.worker_states.recv_timeout = 10000
        self.survey.send_timeout = 30000
        self.survey.recv_timeout = 30000

    def setup(self):
        self.logger.info("starting workers")
        for i in range(self._executors):  # Hardcode to 4 workers for now
            self.logger.info("starting worker %s", i)
            if os.getenv("THREADED_EXECUTION"):
                worker = WorkerThread(
                    self._survey_address, self._state_address, self._stop_workers_event, **self._routes
                )
            else:
                worker = WorkerProcess(
                    self._survey_address, self._state_address, self._stop_workers_event, **self._routes
                )
            worker.start()
            self._workers.append(worker)
        responders = 0
        while True:
            try:
                self.worker_states.recv()
                responders += 1
                if responders == self._executors:
                    break
            except pynng.exceptions.Timeout:
                raise WorkerException("Workers did not respond in time")
        self.logger.info("workers started")

    def configure(self, configuration: Configuration):
        self.logger.info("configuring workers")
        self.survey.send(Request(task="configure", data=configuration).dump())
        responders = 0
        while True:
            try:
                self.survey.recv()
                responders += 1
                if responders == self._executors:
                    break
            except pynng.exceptions.Timeout:
                raise WorkerException("Workers did not respond in time")
        self.logger.info("workers configured")

    def run_backtest(self):
        self.logger.info("running backtest")
        self.survey.send(Request(task="run_backtest").dump())
        responders = 0
        while True:
            try:
                self.survey.recv()
                responders += 1
                if responders == self._executors:
                    break
            except pynng.exceptions.Timeout:
                raise WorkerException("Workers did not respond in time")
        self.logger.info("backtest running")

    def stop(self):
        self.logger.info("stopping workers")
        self._stop_workers_event.set()
        self.survey.send(Request(task="stop").dump())
        responders = 0
        while True:
            try:
                self.survey.recv()
                responders += 1
                if responders == self._executors:
                    break
            except pynng.exceptions.Timeout:
                raise WorkerException("Workers did not respond in time")
        self.logger.info("workers stopped")
