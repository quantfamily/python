import logging
import threading
import time

from foreverbull_core.models.backtest import Period
from foreverbull_core.models.finance import OHLC, Position
from foreverbull_core.models.socket import Request, SocketConfig
from foreverbull_core.socket.exceptions import SocketClosed
from foreverbull_core.socket.nanomsg import NanomsgSocket
from foreverbull_zipline.exceptions import EndOfDayError

from zipline.api import get_datetime


class Feed:
    def __init__(self, engine, configuration=None):
        self.logger = logging.getLogger(__name__)
        self.engine = engine
        if configuration is None:
            configuration = SocketConfig(socket_type="publisher")
        self.configuration = configuration
        self.socket = NanomsgSocket(configuration)
        self.bardata = None
        self.day_completed = False
        self.timeouts = 10
        self.lock = threading.Event()
        self.lock.set()

    def info(self) -> None:
        return {"socket": self.configuration.dict()}

    def _send_period(self):
        period = Period.from_zipline_backtest(self.engine.trading_algorithm.portfolio, get_datetime())
        req = Request(task="period", data=period.dict())
        self.socket.send(req.dump())

    def _send_positions(self):
        positions = self.engine.trading_algorithm.portfolio.positions.items()
        for _, position in positions:
            pos = Position(
                isin=position.sid.symbol, amount=position.amount, cost_basis=position.cost_basis, period=get_datetime()
            )
            req = Request(task="position", data=pos.dict())
            self.socket.send(req.dump())

    def _send_ohlc(self, asset, data):
        ohlc = OHLC(
            isin=asset.symbol,
            open=data.current(asset, "open"),
            high=data.current(asset, "high"),
            low=data.current(asset, "low"),
            close=data.current(asset, "close"),
            volume=data.current(asset, "volume"),
            time=get_datetime().to_pydatetime(),
        )
        req = Request(task="ohlc", data=ohlc.dict())
        self.socket.send(req.dump())

    def handle_data(self, context, data) -> None:
        if self.lock is None:
            return
        self.logger.debug("running day {}".format(str(get_datetime())))
        self.day_completed = False
        self.lock.clear()
        self.bardata = data
        self._send_period()
        self._send_positions()
        for asset in context.assets:
            try:
                self._send_ohlc(asset, data)
            except SocketClosed as exc:
                self.logger.error(exc, exc_info=True)
                return
        message = Request(task="day_completed")
        try:
            self.socket.send(message.dump())
        except SocketClosed as exc:
            self.logger.error(exc, exc_info=True)
            return
        self.wait_for_new_day()
        self.day_completed = True

    def backtest_completed(self) -> None:
        message = Request(task="backtest_completed")
        self.socket.send(message.dump())

    def wait_for_new_day(self) -> None:
        for _ in range(self.timeouts):
            try:
                if self.lock.wait(0.5):
                    break
            except AttributeError:
                return
        else:
            raise EndOfDayError("timeout when waiting for new day")

    def stop(self) -> None:
        if self.lock:
            self.lock.set()
        self.lock = None
        if self.socket is None:
            return
        message = Request(task="backtest_completed")
        try:
            self.socket.send(message.dump())
            time.sleep(0.5)
            self.socket.close()
            self.socket = None
        except SocketClosed as exc:
            self.logger.error(exc, exc_info=True)
