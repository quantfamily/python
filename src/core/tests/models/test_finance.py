from foreverbull_core.models.finance import Instrument, Order, OrderStatus, Portfolio, Position


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
    position = Position(isin="aabbcc123", amount=10, cost_basis=0.1, last_sale_price=15, last_sale_date="2017-01-01")

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
