# log_settings.py

logger_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "std_format": {
            "format": "%(asctime)s - %(levelname)s | %(message)-60s | %(name)s  %(lineno)s",
            "datefmt" : "%y/%b/%Y %H:%M:%S"
        }
    },
    "root": {
        "level": "DEBUG",
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "std_format",
        },
    },
    "loggers": {
        "inventory_generator": {
            "level": "DEBUG",
            "handlers": ["console"],
        },
        "cleanup": {
            "level": "DEBUG",
            "handlers": ["console"],
        }
    },
}