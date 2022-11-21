import logging
import logging.config


class Logger:
    def __init__(self):
        self.default_config = {
            "version": 1,
            "formatters": {"simple": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "simple",
                    "stream": "ext://sys.stdout",
                }
            },
            "loggers": {"base": {"level": "DEBUG", "handlers": ["console"], "propagate": False}},
            "root": {"level": "DEBUG", "handlers": ["console"]},
        }
        logging.config.dictConfig(self.default_config)
