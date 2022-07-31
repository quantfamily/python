from datetime import datetime

from foreverbull_core.models.finance import Asset, EndOfDay, Order, OrderStatus, Portfolio, Position, Price


def test_asset():
    a = Asset(sid=123, symbol="AAPL", asset_name="Apple", exchange="QUANDL")

    data = a.dump()
    loaded = Asset.load(data)
    assert a == loaded


def test_price():
    price = Price(
        date=datetime.now(),
        last_traded=datetime.now(),
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
    )

    data = price.dump()
    loaded = Price.load(data)
    assert price == loaded


def test_end_of_day():
    a = Asset(sid=123, symbol="AAPL", asset_name="Apple", exchange="QUANDL")
    eod = EndOfDay(
        asset=a,
        date=datetime.now(),
        last_traded=datetime.now(),
        price=133.7,
        open=133.6,
        close=1337.8,
        high=1337.8,
        low=1337.6,
        volume=9001,
    )

    data = eod.dump()
    loaded = EndOfDay.load(data)
    assert eod == loaded


def test_order():
    a = Asset(sid=123, symbol="AAPL", asset_name="Apple", exchange="QUANDL")
    order_status = OrderStatus(value=1)
    order = Order(
        id="order_id",
        asset=a,
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
    a = Asset(sid=123, symbol="AAPL", asset_name="Apple", exchange="QUANDL")
    position = Position(asset=a, amount=10, cost_basis=0.1, last_sale_price=15, last_sale_date="2017-01-01")

    data = position.dump()
    loaded = Position.load(data)
    assert position == loaded


def test_portfolio():
    portfolio = Portfolio(
        cash_flow=133.7,
        starting_cash=1000,
        portfolio_value=1543.0,
        pnl=13.4,
        returns=600,
        cash=0,
        positions=[],
        start_date="2017-01-01",
        current_date="2018-01-01",
        positions_value=1543.0,
        positions_exposure=0,
    )

    data = portfolio.dump()
    loaded = Portfolio.load(data)
    assert portfolio == loaded
