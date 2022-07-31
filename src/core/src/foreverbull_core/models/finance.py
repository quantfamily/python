from datetime import datetime
from enum import IntEnum
from typing import List, Optional

from pydantic import validator

from foreverbull_core.models.base import Base


class Asset(Base):
    """Contains the information about a specific asset.
    Symbol is required.
    Given a correct symbol the backend shall be able to determinate the rest.

    Args:
        sid (int, optional): Stock Identified, usually some sort of number.
        symbol (str): Symbol of the asset, eg AAPL for Apple Inc.
        asset_name (str, optional): The full name of the Company or Asset.
        exchange (str, optional): Symbol of the Exchange where the Asset is traded.
        exchange_full (str, optional): Full name of the Exchange where the Asset is traded.
        country_code (str, optional): Country Code where the Exchange is operated.

    Returns:
        Asset: Object contining the information about an Asset
    """

    sid: Optional[int]
    symbol: str
    asset_name: Optional[str]
    exchange: str
    exchange_full: Optional[str]
    country_code: Optional[str]

    @classmethod
    def create(cls, asset):
        """_summary_

        Args:
            asset (Zipline Asset): Import and gerate a Pydantic object from a Zipline Asset.

        Returns:
            Asset: Pydantic Asset object
        """
        return cls(
            sid=asset.sid,
            symbol=asset.symbol,
            asset_name=asset.asset_name,
            exchange=asset.exchange,
            exchange_full=asset.exchange_full,
            country_code=asset.country_code,
        )


class Price(Base):
    """Price shows the current price of an Asset.
    During simulations and backtesting the date information refers to the date and time during that simulation.

    Args:
        date (datetime): Current date of the price object.
        last_traded(datetime): Date of when the Asset was last traded.
        price (float): Current spot price of the Asset.
        open (float): What is was during opening, for a simulation of Daily, hourly or so.
        close (close): What is was during closing, for a simulation of Daily, hourly or so.
        high (high): Highest point for a simulation during a period.
        low (low): Lower point for a simulation during a period.
        volume (volume): Total sum of stocks that has been traded during a time.

    Returns:
        Price: Pydantic Price object
    """

    date: datetime
    last_traded: datetime
    price: float
    open: float
    close: float
    high: float
    low: float
    volume: int

    @validator("date", pre=True)
    def date_to_isodate(cls, v):
        """Converts datetime to a string of isodate format."""
        if type(v) is datetime:
            return v.isoformat()
        return v

    @validator("last_traded", pre=True)
    def last_traded_to_isodate(cls, v):
        """Converts datetime to a string of isodate format."""
        if type(v) is datetime:
            return v.isoformat()
        return v


class EndOfDay(Price):
    """Daily period price.
    TODO: Change name to also use same object for Hourly and Weekly times?

    Args:
        asset (Asset): Asset object to identify which asset the price is about.
        date (datetime): Current date of the price object.
        last_traded(datetime): Date of when the Asset was last traded.
        price (float): Current spot price of the Asset.
        open (float): What is was during opening, for a simulation of Daily, hourly or so.
        close (close): What is was during closing, for a simulation of Daily, hourly or so.
        high (high): Highest point for a simulation during a period.
        low (low): Lower point for a simulation during a period.
        volume (volume): Total sum of stocks that has been traded during a time.

    Returns:
        EndOfDay: Pydantic object containing period pricing
    """

    asset: Asset


class OrderStatus(IntEnum):
    OPEN = 0
    FILLED = 1
    CANCELLED = 2
    REJECTED = 3
    HELD = 4


class Order(Base):
    """Information about an Order, not everything is needed when requesting a Order.
    However the backend will fill in all the meta- data and such once its accepted.

    OrderStatus is used to get details about the processing

    Args:
        id (str, optional): Order ID, will be set after the order is accepted in the backend.
        asset (Asset, optional): Asset object to know which asset the order is placed for.
        amount (int, optional): Number of assets that the order contains. Negative int for selling.
        filled (int, optional): How many of the amount that is filled, ie has been accepted and proceed.
        commission (int, optional): Total commission taken by the stock broker.
        limit_price (int, optional): Limit price of the Order
        stop_price (int, optional): Stop price of the Order
        current_date (datetime, optional): Current date and time were this information was taken from.
        created_date (datetime, optional): Created date of the order.
        status (OrderStatus, optional): Status of the order, filled, open rejected etc.

    Returns:
        Order: Pydantic object containing order
    """

    id: Optional[str]
    asset: Optional[Asset]
    amount: Optional[int]
    filled: Optional[int]
    commission: Optional[int]
    limit_price: Optional[int]
    stop_price: Optional[int]
    current_date: Optional[str]
    created_date: Optional[str]
    status: Optional[OrderStatus]

    def update(self, event):
        """Updates the information in the Asset object

        Args:
            event (Zipline Order Object): Object coming from Zipline simulation
        """
        asset = Asset(
            sid=event.sid.sid,
            symbol=event.sid.symbol,
            asset_name=event.sid.asset_name,
            exchange=event.sid.exchange,
            exchange_full=event.sid.exchange_full,
            country_code=event.sid.country_code,
        )
        self.asset = asset
        self.amount = event.amount
        self.filled = event.filled
        self.commission = event.commission
        self.limit_price = event.limit
        self.stop_price = event.stop
        self.current_date = event.dt.isoformat()
        self.created_date = event.created.isoformat()
        self.status = event.status

    @classmethod
    def create(cls, order):
        """Create a pydantic object from a zipline order object

        Args:
            order (Zipline Order Object): Object coming from Zipline simulation

        Returns:
            Order: Pydantic order object
        """
        asset = Asset(
            sid=order.sid.sid,
            symbol=order.sid.symbol,
            asset_name=order.sid.asset_name,
            exchange=order.sid.exchange,
            exchange_full=order.sid.exchange_full,
            country_code=order.sid.country_code,
        )
        return cls(
            id=order.id,
            asset=asset,
            amount=order.amount,
            filled=order.filled,
            commission=order.commission,
            limit_price=order.limit,
            stop_price=order.stop,
            current_date=order.dt.isoformat(),
            created_date=order.created.isoformat(),
            status=order.status,
        )


class Position(Base):
    """Information about a current Position of an Asset

    Args:
        asset (Asset): Asset of where we have a position
        amount (int): Amount that we have in the Asset
        cost_basis (float): Cost basis of the Asset position
        last_sale_price (float): Price of which the asset was traded last
        last_sale_date (datetime): Date of which the asset was traded last

    Returns:
        Position:
    """

    asset: Asset
    amount: int
    cost_basis: float
    last_sale_price: float
    last_sale_date: str


class Portfolio(Base):
    """TODO: Documentation on this

    Args:
        cash_flow (float): Cash Flow
        starting_cash (int): Starting Cash
        portfolio_value (float): Portfolio Value
        pnl (float): float
        returns (float): float
        cash (float): float
        positions (List[Position]): List[Position]
        start_date (datetime): str
        current_date (datetime): str
        positions_value (float): float
        positions_exposure (float): float

    Returns:
        Portfolio: _description_
    """

    cash_flow: float
    starting_cash: int
    portfolio_value: float
    pnl: float
    returns: float
    cash: float
    positions: List[Position]
    start_date: str
    current_date: str
    positions_value: float
    positions_exposure: float

    @classmethod
    def from_backtest(cls, backtest, current_date: datetime):
        """TODO: Docs

        Args:
            backtest (object): _description_
            current_date (datetime): _description_

        Returns:
            Portfolio: _description_
        """
        positions = []
        for _, pos in backtest.positions.items():
            asset = Asset(
                sid=pos.asset.sid,
                symbol=pos.asset.symbol,
                asset_name=pos.asset.asset_name,
                exchange=pos.asset.exchange,
                exchange_full=pos.asset.exchange_full,
                country_code=pos.asset.country_code,
            )
            position = Position(
                asset=asset,
                amount=pos.amount,
                cost_basis=pos.cost_basis,
                last_sale_price=pos.last_sale_price,
                last_sale_date=pos.last_sale_date.isoformat(),
            )
            positions.append(position)
        portfolio = Portfolio(
            cash_flow=backtest.cash_flow,
            starting_cash=backtest.starting_cash,
            portfolio_value=backtest.portfolio_value,
            pnl=backtest.pnl,
            returns=backtest.returns,
            cash=backtest.cash,
            positions=positions,
            start_date=backtest.start_date.isoformat(),
            current_date=current_date.isoformat(),
            positions_value=backtest.positions_value,
            positions_exposure=backtest.positions_exposure,
        )
        return portfolio
