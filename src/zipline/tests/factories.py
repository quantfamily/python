import yfinance
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from foreverbull_zipline.models import Database, IngestConfig
from tests import OHLC, Base, Instrument


def populate_sql(ic: IngestConfig, db: Database):
    engine = create_engine(f"postgresql://{db.user}:{db.password}@{db.netloc}:{db.port}/{db.dbname}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.query(OHLC).delete()
    session.query(Instrument).delete()
    isin_to_symbol = {"US0378331005": "AAPL", "US88160R1014": "TSLA", "US5949181045": "MSFT"}
    for isin in ic.isins:
        feed = yfinance.Ticker(isin_to_symbol[isin])
        data = feed.history(start=ic.from_date, end=ic.to_date)
        instrument = Instrument(isin=isin)
        session.add(instrument)
        for (idx, row) in data.iterrows():
            ohlc = OHLC(
                isin=isin, open=row.Open, high=row.High, low=row.Low, close=row.Close, volume=row.Volume, time=str(idx)
            )
            session.add(ohlc)
    session.commit()
