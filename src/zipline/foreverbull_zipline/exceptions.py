class BacktestNotRunning(Exception):
    pass


class BacktestDayNotFinished(Exception):
    pass


class ConfigError(Exception):
    pass


class BrokerError(Exception):
    pass


class EndOfDayError(Exception):
    pass
