import pytest
from foreverbull_core.models.finance import OrderStatus
from foreverbull_zipline.exceptions import BrokerError


@pytest.mark.skip(reason="still dont know how to test this, TODO")
def test_can_trade(running_backtest, broker, asset):
    new_day, finish = running_backtest()
    new_day()
    broker._can_trade(asset)
    finish()


def test_can_trade_unknown_asset(running_backtest, broker, asset):
    new_day, finish = running_backtest()
    new_day()
    asset.symbol = "Ljungskile Pizzeria"
    with pytest.raises(BrokerError, match=".*Symbol 'LJUNGSKILE PIZZERIA' was not found"):
        broker._can_trade(asset)
    finish()


def test_order(running_backtest, broker, order):
    _, finish = running_backtest()
    order = broker._order(order)
    finish()
    assert len(order.id) > 5
    assert order.status == OrderStatus.OPEN


def test_order_unknown_asset(running_backtest, broker, order):
    new_day, finish = running_backtest()
    new_day()
    order.asset.symbol = "Ljungskile Pizzeria"
    with pytest.raises(BrokerError, match=".*Symbol 'LJUNGSKILE PIZZERIA' was not found"):
        broker._order(order)
    finish()


def test_get_order(running_backtest, broker, order):
    new_day, finish = running_backtest()
    new_day()
    broker._order(order)
    new_day()
    new_day()
    order = broker._get_order(order)
    finish()
    assert order.status == OrderStatus.FILLED


def test_get_order_unknown_order_id(running_backtest, broker, order):
    new_day, finish = running_backtest()
    new_day()
    order.id = "asdf"
    with pytest.raises(BrokerError, match="order asdf not found"):
        broker._get_order(order)
    finish()


def test_get_open_orders(running_backtest, broker, order):
    new_day, finish = running_backtest()
    broker._order(order)
    new_day()
    new_day()
    orders = broker._get_open_orders()
    finish()
    assert len(orders) == 1


def test_cancel_order(running_backtest, broker, order):
    order.limit_price = 1
    order.stop_price = 1
    new_day, finish = running_backtest()
    new_day()
    placed_order = broker._order(order)
    assert placed_order.status == OrderStatus.OPEN
    new_day()
    cancelled_order = broker._cancel_order(order)
    finish()
    assert cancelled_order.status == OrderStatus.CANCELLED


def test_cancel_order_unknown_order_id(running_backtest, broker, order):
    new_day, finish = running_backtest()
    new_day()
    order.id = "asdf"
    with pytest.raises(BrokerError, match="order asdf not found"):
        broker._cancel_order(order)
    finish()
