# (C) Datadog, Inc. 2010-2016
# All rights reserved
# Licensed under Simplified BSD License (see LICENSE)

# stdlib
from functools import wraps
from logging import LogRecord
import re

# project
import config

def log_exceptions(logger):
    """
    A decorator that catches any exceptions thrown by the decorated function and
    logs them along with a traceback.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception:
                logger.exception(
                    u"Uncaught exception while running {0}".format(func.__name__)
                )
                raise
            return result
        return wrapper
    return decorator

class DisableLoggerInit():
    '''
    Context manager to disable the logging initialization.
    Just a basic monkey-patch of the logging intialization routine.
    Useful when importing elements from modules that may init the
    logger at the global level.
    '''
    def __enter__(self):
        self._original = config.initialize_logging
        config.initialize_logging = lambda x: None
    def __exit__(self, exc_type, exc_val, exc_tb):
        config.initialize_logging = self._original

class RedactedLogRecord(LogRecord, object):
    """
    Custom LogRecord that obfuscates API key logging.
    """
    API_KEY_PATTERN = re.compile('api_key=*\w+(\w{5})')
    API_KEY_REPLACEMENT = r'api_key=*************************\1'

    def getMessage(self):
        message = super(RedactedLogRecord, self).getMessage()

        return re.sub(self.API_KEY_PATTERN, self.API_KEY_REPLACEMENT, message)
