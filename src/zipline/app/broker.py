import logging
import threading

import zipline
from foreverbull_core.models.finance import Asset, Order
from foreverbull_core.models.socket import Request, SocketConfig
from foreverbull_core.socket.exceptions import SocketClosed, SocketTimeout
from foreverbull_core.socket.nanomsg import NanomsgSocket
from foreverbull_core.socket.router import MessageRouter

from app.backtest import Backtest
from app.feed import Feed

from .exceptions import BrokerError


class Broker(threading.Thread):
    def __init__(self, backtest: Backtest, feed: Feed, configuration=None):
        self.backtest = backtest
        self.feed = feed
        self.logger = logging.getLogger(__name__)
        if configuration is None:
            configuration = SocketConfig(socket_type="replier", recv_timeout=200000)
        self.configuration = configuration
        self.socket = NanomsgSocket(configuration)
        self.router = MessageRouter()
        self.router.add_route(self._can_trade, "can_trade", Asset)
        self.router.add_route(self._order, "order", Order)
        self.router.add_route(self._get_order, "get_order", Order)
        self.router.add_route(self._get_open_orders, "get_open_orders")
        self.router.add_route(self._cancel_order, "cancel_order", Order)
        super(Broker, self).__init__()

    def info(self) -> dict:
        return {"socket": self.configuration.dict()}

    def run(self) -> None:
        while True:
            try:
                req_data = self.socket.recv()
                req = Request.load(req_data)
                rsp = self.router(req)
                self.socket.send(rsp.dump())
            except SocketTimeout:
                pass
            except SocketClosed:
                return

    def _can_trade(self, asset: Asset) -> bool:
        try:
            equity = self.backtest.trading_algorithm.symbol(asset.symbol)
        except zipline.errors.SymbolNotFound as e:
            raise BrokerError(repr(e))
        if self.feed.bardata.can_trade(equity):
            return True
        raise BrokerError(f"Asset {asset.symbol} is not tradeable")

    def _order(self, order: Order) -> dict:
        self.logger.info(f"order: {order}")
        try:
            equity = self.backtest.trading_algorithm.symbol(order.asset.symbol)
        except zipline.errors.SymbolNotFound as e:
            raise BrokerError(repr(e))
        order.id = self.backtest.trading_algorithm.order(
            asset=equity, amount=order.amount, limit_price=order.limit_price, stop_price=order.stop_price
        )
        event = self.backtest.trading_algorithm.get_order(order.id)
        order.update(event)
        self.logger.info(f"Order done: {order}")
        return order

    def _get_order(self, order: Order) -> dict:
        self.logger.info(f"Get Order {order}")
        event = self.backtest.trading_algorithm.get_order(order.id)
        if event is None:
            raise BrokerError(f"order {order.id} not found")
        order.update(event)
        self.logger.info(f"Get Order updated: {order}")
        return order

    def _get_open_orders(self) -> dict:
        response = {"orders": []}
        for _, open_orders in self.backtest.trading_algorithm.get_open_orders().items():
            for order in open_orders:
                response["orders"].append(Order.create(order))
        return response

    def _cancel_order(self, order: Order) -> dict:
        self.backtest.trading_algorithm.cancel_order(order.id)
        event = self.backtest.trading_algorithm.get_order(order.id)
        if event is None:
            raise BrokerError(f"order {order.id} not found")
        order.update(event)
        return order

    def stop(self) -> None:
        self.socket.close()
