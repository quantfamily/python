import pandas
from foreverbull.data.data import Database
from foreverbull.data.stock_data import Portfolio


def test_stock_data(loaded_database: Database):
    df = loaded_database.stock_data()
    assert type(df) == pandas.core.frame.DataFrame
    assert len(df)


def test_stock_data_by_isin(loaded_database: Database, instruments: dict):
    for isin, _ in instruments.items():
        df = loaded_database.stock_data(isin=isin)
        assert type(df) == pandas.core.frame.DataFrame
        assert len(df)


def test_portfolio(loaded_database: Database):
    portfolio = loaded_database.portfolio()
    assert type(portfolio) == Portfolio


def test_get_position(loaded_database: Database):
    pass
