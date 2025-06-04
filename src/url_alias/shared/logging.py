import logging
import sys
from typing import Optional


class LogConfig:
    """Centralized logging configuration"""

    @staticmethod
    def setup_logging(
        level: str = "INFO", format_string: Optional[str] = None, service_name: Optional[str] = None
    ) -> None:
        """Setup logging configuration for the application"""

        if format_string is None:
            if service_name:
                format_string = f"%(asctime)s - {service_name} - %(name)s - %(levelname)s - %(message)s"
            else:
                format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        log_level = getattr(logging, level.upper(), logging.INFO)

        logging.basicConfig(
            level=log_level, format=format_string, datefmt="%Y-%m-%d %H:%M:%S", stream=sys.stdout, force=True
        )

        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name"""
    return logging.getLogger(name)


def get_service_logger(service_name: str) -> logging.Logger:
    """Get a logger for a specific service"""
    return logging.getLogger(f"url_alias.{service_name}")


LogConfig.setup_logging(service_name="url-alias")
