from datetime import datetime

import pandas

from foreverbull.data.data import Database, DateManager
from foreverbull.data.stock_data import Instrument, Portfolio, Position


def test_connect():
    db = Database(execution_id="test_execution", date_manager=DateManager(datetime.now(), datetime.now()), db_conf=None)
    db.connect()


def test_stock_data():
    db = Database(execution_id="test_execution", date_manager=DateManager(datetime.now(), datetime.now()), db_conf=None)
    db.connect()
    df = db.stock_data()
    assert type(df) == pandas.core.frame.DataFrame


def test_portfolio(db_with_sample_data: Database):
    portfolio = db_with_sample_data.portfolio()
    assert type(portfolio) == Portfolio


def test_get_position(db_with_sample_data: Database, sample_instrument: Instrument):
    model = Instrument(isin="abc123")
    position = db_with_sample_data.get_position(model)

    assert type(position) == Position
