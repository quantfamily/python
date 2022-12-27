from foreverbull.data.stock_data import Base, Portfolio, Position
from foreverbull_core.models.worker import Database as DatabaseConfiguration
from pandas import read_sql_query, DataFrame
from sqlalchemy import create_engine, desc
from sqlalchemy.orm.session import sessionmaker


class DateManager:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.current = None


class Database:
    def __init__(self, execution_id: str, date_manager: DateManager, db_conf: DatabaseConfiguration = None):
        self.db_conf = db_conf
        if db_conf is None:
            self.uri = "sqlite:///:memory:"
        else:
            self.uri = (
                f"postgresql://{db_conf.user}:{db_conf.password}@{db_conf.netloc}:{db_conf.port}/{db_conf.dbname}"
            )
        self.execution_id = execution_id
        self.date_manager = date_manager

    def connect(self) -> None:
        self.engine = create_engine(self.uri)
        if self.db_conf is None:
            Base.metadata.create_all(self.engine)
        self.session_maker = sessionmaker(self.engine)

    def stock_data(self, isin: str = None) -> DataFrame:
        if isin:
            query = f"""Select isin, time, high, low, open, close, volume
                        FROM ohlc WHERE time BETWEEN '{self.date_manager.start}' 
                        AND '{self.date_manager.current}' AND isin='{isin}'"""
        else:
            query = f"""Select isin, time, high, low, open, close, volume
                        FROM ohlc WHERE time BETWEEN '{self.date_manager.start}' 
                        AND '{self.date_manager.current}'"""
        return read_sql_query(query, self.engine)

    def portfolio(self) -> Portfolio:
        with self.session_maker() as db_session:
            q = db_session.query(Portfolio).filter_by(execution_id=self.execution_id)
            portfolio = q.order_by(desc(Portfolio.current_date)).first()
        return portfolio

    def get_position(self, isin: str) -> Position:
        portfolio = self.portfolio()

        with self.session_maker() as db_session:
            query = db_session.query(Position).join(Portfolio).join(Instrument)
            query = query.filter(Portfolio.id == portfolio.id)
            query = query.filter(isin == Position.isin)
            position = query.first()

        return position
