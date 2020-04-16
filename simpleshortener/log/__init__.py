__all__ = ["LoggerSetup"]

import logging
from typing import Union, List

VERBOSITY_LEVELS = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG
}

class LoggerSetup:
    def __init__(self,loggers: List[str], log_level: Union[int, str], log_level_modules: Union[int, str] = logging.ERROR):
        if isinstance(log_level, str):
            log_level = VERBOSITY_LEVELS[log_level]

        if isinstance(log_level_modules, str):
            modules_log_level = VERBOSITY_LEVELS[log_level_modules]

        # Set format for the log
        logging.basicConfig(format="%(levelname)s|%(name)s|%(message)s", level=log_level_modules)

        for l in loggers:
            logging.getLogger(l).setLevel(log_level)
