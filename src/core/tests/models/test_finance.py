from datetime import datetime

from foreverbull_core.models.finance import Instrument, Order, OrderStatus, Position


def test_instrument():
    i = Instrument(isin="AABBCC123", symbol="AAPL", name="Apple", exchange="QUANDL")

    data = i.dump()
    loaded = Instrument.load(data)
    assert i == loaded


def test_order():
    order_status = OrderStatus(value=1)
    order = Order(
        id="order_id",
        isin="aabbcc123",
        amount=10,
        filled=10,
        commission=0,
        limit_price=133.7,
        current_date="2017-01-01",
        created_date="2017-01-01",
        status=order_status,
    )

    data = order.dump()
    loaded = Order.load(data)
    assert order == loaded


def test_position():
    position = Position(isin="aabbcc123", amount=10, cost_basis=0.1, period=datetime.now())

    data = position.dump()
    loaded = Position.load(data)
    assert position == loaded
