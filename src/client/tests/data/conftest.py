from datetime import datetime

import pytest
from sqlalchemy.orm import sessionmaker

from foreverbull.data.data import Database, DateManager
from foreverbull.data.stock_data import OHLC, Instrument, Portfolio, Position

date = datetime(2016, 1, 4, 21)


@pytest.fixture()
def sample_instrument():
    return Instrument(isin="abc123", name="BERLINER KEBAP")


@pytest.fixture()
def sample_stock_data(sample_instrument):
    return OHLC(isin=sample_instrument.isin)


@pytest.fixture()
def sample_portfolio():
    return Portfolio(
        execution_id="test_execution",
        cash_flow=123.2,
        starting_cash=1000,
        portfolio_value=2134.2,
        pnl=32.2,
        returns=22.2,
        start_date=date,
        current_date=date,
        positions_value=222.4,
        positions_exposure=100.0,
    )


@pytest.fixture()
def sample_position(sample_instrument):
    return Position(isin=sample_instrument.isin, amount=10, cost_basis=12.2, last_sale_price=77.4, last_sale_date=date)


@pytest.fixture()
def db():
    db = Database(execution_id="test_execution", date_manager=DateManager(datetime.now(), datetime.now()), db_conf=None)
    db.connect()
    return db


@pytest.fixture()
def db_with_sample_data(db, sample_instrument, sample_stock_data, sample_portfolio, sample_position):
    Session = sessionmaker(db.engine)

    with Session() as db_session:
        db_session.add(sample_instrument)
        db_session.add(sample_stock_data)
        db_session.add(sample_portfolio)
        db_session.commit()
        db_session.refresh(sample_portfolio)

    with Session() as db_session:
        sample_position.portfolio_id = sample_portfolio.id
        db_session.add(sample_position)
        db_session.commit()

    return db
