import logging
import logging.config

config = {
    'version': 1,
    'formatters': {
        'precise': {
            'format': '%(asctime)s | %(name)-12s | %(levelname)-8s | '
                      '%(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'precise',
            'level': 'ERROR',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'precise',
            'filename': 'receiver.log',
            'maxBytes': 50000,
            'backupCount': 5
        },
        'memory': {
            'class': 'logging.handlers.MemoryHandler',
            'capacity': 0  # for flush() at each log record
        }
    },
    'root': {
        'level': logging.DEBUG,
        'handlers': ['console', 'file', 'memory']
    }
}


def set_up_logging():
    """Configure the logging module."""
    logging.config.dictConfig(config)
    logging.getLogger('api').disabled = False
    logging.captureWarnings(True)
    logging.getLogger('logger').info("Set up logging")


def get_memory_handler():
    """Get MemoryHandler for root logger.

    This is used to connect the logging module to log table view in
    Main Window.

    :rtype: logging.handlers.MemoryHandler
    """
    return logging.root.handlers[2]


def get_modules():
    """Get known modules that logs messages.

    :return: list of modules
    """
    return ["main", "logger", "mainwindow", "logindialog", "gsinfodialog",
            "py.warnings"]
