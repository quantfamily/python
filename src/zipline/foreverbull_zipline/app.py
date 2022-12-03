import logging
import os
import threading
from datetime import datetime

from foreverbull_core.broker import Broker
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.router import MessageRouter

from foreverbull_zipline.backtest import Backtest
from foreverbull_zipline.broker import Broker as StockBroker
from foreverbull_zipline.exceptions import BacktestNotRunning
from foreverbull_zipline.feed import Feed
from foreverbull_zipline.models import EngineConfig, IngestConfig, Period, Result


class ApplicationError(Exception):
    pass


class Application(threading.Thread):
    def __init__(self, broker: Broker):
        self.logger = logging.getLogger(__name__)
        self.id = os.environ.get("SERVICE_ID", None)
        self.broker: Broker = broker
        self.running = False
        self.online = False
        self._router = MessageRouter()
        self._router.add_route(self.info, "info")
        self._router.add_route(self._ingest, "ingest", IngestConfig)
        self._router.add_route(self._configure, "configure", EngineConfig)
        self._router.add_route(self._run, "run")
        self._router.add_route(self._continue, "continue")
        self._router.add_route(self._status, "status")
        self._router.add_route(self._stop, "stop")
        self._router.add_route(self._result, "result")
        self._stop_lock = threading.Lock()
        self.backtest: Backtest = Backtest()
        self.feed: Feed = Feed(self.backtest)
        self.stock_broker: StockBroker = StockBroker(self.backtest, self.feed)
        threading.Thread.__init__(self)

    def _ingest(self, config: IngestConfig):
        self.backtest.ingest(config)

    def _configure(self, config: EngineConfig):
        self.backtest.configure(config)

    def _run(self):
        self.logger.info("running backtest")
        self.backtest.set_callbacks(self.feed.handle_data, self.feed.backtest_completed)
        self.stock_broker.start()
        self.backtest.start()
        return {"status": "ok"}

    def _continue(self) -> None:
        if not self.running:
            raise BacktestNotRunning("backtest is not running")
        self.feed.lock.set()  # TODO: Maybe change this variable name?

    def info(self) -> dict:
        return {
            "socket": self.broker.socket.config.dict(),
            "feed": {"socket": self.feed.configuration.dict()},
            "broker": {"socket": self.stock_broker.configuration.dict()},
            "running": self.running,
        }

    def _status(self) -> dict:
        return {
            "running": self.running,
            "configured": self.backtest.configured,
            "day_completed": self.feed.day_completed,
        }

    def _stop(self) -> None:
        self._stop_lock.acquire()
        if self.backtest and self.backtest.is_alive():
            self.backtest.stop()
            # self.backtest.join()
            self.backtest = None
        if self.stock_broker and self.stock_broker.is_alive():
            self.stock_broker.stop()
            self.stock_broker.join()
            self.stock_broker = None
        if self.running:
            self.feed.stop()
        self._stop_lock.release()
        self.running = False

    def run(self) -> None:
        self.running = True
        while self.running:
            self.logger.debug("waiting for socket.recv()..")
            try:
                message = self.broker.socket.recv()
                self.logger.info(f"recieved task: {message.task}")
                rsp = self._router(message)
                self.logger.info(f"sending response for task: {message.task}")
                self.broker.socket.send(rsp)
            except SocketTimeout:
                self.logger.debug("timeout")
                pass
            except SocketClosed:
                return
            except Exception as e:
                self.logger.warning(f"Unknown Exception when running: {repr(e)}")

    def stop(self):
        self.broker.socket.close()
        return self._stop()

    def _result(self) -> dict:
        result = Result(periods=[])
        for period in self.backtest.result:
            period["period_open"] = datetime.fromtimestamp(period["period_open"] / 1000)
            period["period_close"] = datetime.fromtimestamp(period["period_close"] / 1000)
            period_result = Period(**period)
            result.periods.append(period_result)
        return result.dict()
