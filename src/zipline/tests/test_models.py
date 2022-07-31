from foreverbull_core.models.socket import SocketConfig, SocketType

from app.models import EngineConfig, Period, Result, Sockets


def test_info():
    main = SocketConfig(socket_type=SocketType.REQUESTER)
    feed = SocketConfig(socket_type=SocketType.PUBLISHER)
    broker = SocketConfig(socket_type=SocketType.REQUESTER)
    info = Sockets(main=main, feed=feed, broker=broker, running=True)

    dumped = info.dump()
    loaded = Sockets.load(dumped)
    assert info == loaded


def test_config():
    config = EngineConfig(
        bundle="bundle",
        calendar="calendar",
        start_date="2017-01-01",
        end_date="2018-01-01",
        timezone="utc",
        benchmark="AAPL",
        isins=["TSLA", "AAPL"],
    )

    dumped = config.dump()
    loaded = EngineConfig.load(dumped)
    assert config == loaded


def test_result():
    period = Period(
        period_open=1483626660000,
        period_close=1483650000000,
        shorts_count=0,
        pnl=-0.59305,
        long_value=1166.1,
        short_value=0,
        long_exposure=1166.1,
        starting_exposure=0.0,
        short_exposure=0,
        capital_used=-1166.69305,
        gross_leverage=0.0116610692,
        net_leverage=0.0116610692,
        ending_exposure=1166.1,
        starting_value=0.0,
        ending_value=1166.1,
        starting_cash=100000.0,
        ending_cash=98833.30695,
        returns=-0.0000059305,
        portfolio_value=99999.40695,
        longs_count=1,
        algo_volatility=0.0000543539,
        sharpe=-9.1651513899,
        alpha=-0.0000144607,
        beta=-0.0008449102,
        sortino=-9.1651513899,
        max_drawdown=-0.0000059305,
        max_leverage=0.0116610692,
        excess_return=0,
        treasury_period_return=0,
        trading_days=3,
        benchmark_period_return=0.006820929,
        benchmark_volatility=0.0498830578,
        algorithm_period_return=-0.0000059305,
    )
    result = Result(periods=[period])
    dumped = result.dump()
    loaded = Result.load(dumped)
    assert loaded == result
