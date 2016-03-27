import logging
import logging.config

# Level for probe errors
from app.parser.outputparser import PARSERS

PROBE = 100

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
            'maxBytes': 500000,
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
    logging.addLevelName(PROBE, 'PROBE')
    for module_name in get_modules():
        # Re-enable loggers with conflicting names
        logging.getLogger(module_name).disabled = False
    logging.captureWarnings(True)
    logging.getLogger('Logger').info("Set up logging")


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
    return (
        ["Main", "Logger", "MainWindow", "LoginDialog", "API", "GSInfoDialog",
         "Parser"] +
        [x.__name__ for x in PARSERS] +
        ["Sender", "Probe", "py.warnings"]
    )
