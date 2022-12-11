import os
import warnings
from typing import List

import numpy as np
import pandas as pd
from foreverbull_zipline.models import Database
from pandas import read_sql_query
from sqlalchemy import create_engine

from zipline.data.bundles import ingest, register
from zipline.utils.cli import maybe_show_progress

warnings.filterwarnings("ignore")


class DatabaseEngine:
    def __init__(self, db_config: Database):
        self._db_config = db_config
        self._engine = create_engine(self._get_db_url())

    def _get_db_url(self) -> str:
        return f"postgresql://{self._db_config.user}:{self._db_config.password}@{self._db_config.netloc}:{self._db_config.port}/{self._db_config.dbname}"  # noqa

    def get_data(self, isin, from_date, to_date):
        query = f"""SELECT open, high, low, close, volume, time FROM ohlc
        INNER JOIN instrument ON instrument.isin = ohlc.isin
        WHERE instrument.isin='{isin}' AND time BETWEEN '{from_date}' AND '{to_date}'
        ORDER BY time asc"""
        return read_sql_query(query, self._engine)


class SQLIngester:
    def __init__(self, isins: List[str], from_date: str, to_date: str, engine: DatabaseEngine, **kwargs):
        self.isins = isins
        self.from_date = from_date
        self.to_date = to_date
        self._engine = engine

    def create_metadata(self) -> pd.DataFrame:
        return pd.DataFrame(
            np.empty(
                len(self.isins),
                dtype=[
                    ("start_date", "datetime64[ns]"),
                    ("end_date", "datetime64[ns]"),
                    ("auto_close_date", "datetime64[ns]"),
                    ("symbol", "object"),
                    ("exchange", "object"),
                ],
            )
        )

    def get_stock_data(self, isins: str) -> pd.DataFrame:
        data = self._engine.get_data(isins, self.from_date, self.to_date)
        data["time"] = pd.to_datetime(data["time"])
        data.rename(columns={"time": "Date"}, inplace=True, copy=False)
        data.set_index("Date", inplace=True)
        return data

    def writer(self, show_progress: bool) -> iter(int, pd.DataFrame):
        with maybe_show_progress(self.isins, show_progress, label="Ingesting from SQL") as it:
            for index, isin in enumerate(it):
                data = self.get_stock_data(isin)
                data.dropna(
                    inplace=True
                )  # Yahoo can sometimes add duplicate rows on same date, one which is full or NaN
                start_date = data.index[0]
                end_date = data.index[-1]
                autoclose_date = end_date + pd.Timedelta(days=1)
                self._df_metadata.iloc[index] = start_date, end_date, autoclose_date, isin, "NASDAQ"
                yield index, data

    def __call__(
        self,
        environ,
        asset_db_writer,
        minute_bar_writer,
        daily_bar_writer,
        adjustment_writer,
        calendar,
        start_session,
        end_session,
        cache,
        show_progress,
        output_dir,
    ):
        self._df_metadata = self.create_metadata()
        daily_bar_writer.write(self.writer(show_progress), show_progress=show_progress)
        asset_db_writer.write(equities=self._df_metadata)
        adjustment_writer.write()


if __name__ == "__main__":
    symbols = [sym.strip() for sym in os.environ.get("SYMBOLS").split(",")]
    register(
        "foreverbull",
        SQLIngester(symbols, os.environ.get("FROM_DATE"), os.environ.get("TO_DATE")),
        calendar_name="XFRA",
    )
    ingest("foreverbull", os.environ, pd.Timestamp.utcnow(), [], True)
