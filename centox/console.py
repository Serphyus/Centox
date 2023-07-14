import logging


class Logger(logging.Formatter):
    FORMATS = {
        logging.INFO:     "\x1b[38m[*]\x1b[0m %(message)s",
        logging.DEBUG:    "\x1b[34m[+]\x1b[0m %(message)s",
        logging.WARNING:  "\x1b[33m[!]\x1b[0m %(message)s",
        logging.ERROR:    "\x1b[31m[-]\x1b[0m %(message)s",
        logging.CRITICAL: "\x1b[31m;1[-]\x1b[0m %(message)s",
    }

    
    def format(self, record):
        formatter = logging.Formatter(
            fmt=self.FORMATS.get(record.levelno),
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        return formatter.format(record)

    
    @classmethod
    def init(cls, log_level: int) -> None:
        handler = logging.StreamHandler()
        handler.setFormatter(cls())

        logging.basicConfig(
            level=log_level,
            handlers=[handler]
        )