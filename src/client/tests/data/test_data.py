from datetime import datetime

import pandas
from foreverbull.data.data import Database, DateManager
from foreverbull.data.stock_data import Portfolio


def test_connect_sqlite():
    db = Database(execution_id="test_execution", date_manager=DateManager(datetime.now(), datetime.now()), db_conf=None)
    db.connect()


def test_connect_postgres(postgres_database):
    db = Database(
        execution_id="test_execution",
        date_manager=DateManager(datetime.now(), datetime.now()),
        db_conf=postgres_database,
    )
    db.connect()


def test_stock_data(postgres_database, loaded_database):
    db = Database(
        execution_id="test_execution",
        date_manager=DateManager(datetime.now(), datetime.now()),
        db_conf=postgres_database,
    )
    db.connect()
    df = db.stock_data()
    assert type(df) == pandas.core.frame.DataFrame


def test_portfolio(db_with_sample_data: Database):
    portfolio = db_with_sample_data.portfolio()
    assert type(portfolio) == Portfolio


def test_get_position(db_with_sample_data: Database):
    pass
