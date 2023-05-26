import functools
import logging
import time
from logging import Logger

DEFAULT_LEVEL = 'INFO'
DEFAULT_FORMAT = '[%(levelname)s] %(asctime)s - %(module)s - %(filename)s : %(message)s'


def logging_setup(level=DEFAULT_LEVEL, log_format=DEFAULT_FORMAT) -> Logger:
    """
    Set up the logging configuration and create a Logger object.

    :param level: The logging level to set (default: 'INFO').
    :type level: str
    :param log_format: The logging format (default: '[%(levelname)s] %(asctime)s - %(module)s - %(filename)s : %(message)s').
    :type log_format: str
    :return: The Logger object.
    :rtype: logging.Logger
    """
    log_formatter = logging.Formatter(log_format)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    consoler_handler = logging.StreamHandler()
    consoler_handler.setFormatter(log_formatter)
    root_logger.addHandler(consoler_handler)

    return root_logger


def log_process_time(func):
    """
    Decorator function to log the start and completion of a process, including execution time.

    Usage:
    @log_process
    def my_function(self, *args, **kwargs):
        ...

    :param func: The function to be decorated.
    :type func: function
    :return: The decorated function.
    :rtype: function
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        logger = self.log if hasattr(self, 'log') else logging.getLogger()
        logger.info(f"Starting {func.__name__}()")
        start_time = time.time()
        result = func(self, *args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"Process {func.__name__}() done. Execution time: {execution_time:.2f} seconds")
        return result

    return wrapper
