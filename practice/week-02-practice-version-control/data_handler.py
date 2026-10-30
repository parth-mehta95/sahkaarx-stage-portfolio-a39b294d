"""
data_handler.py
Abstract Base Class defining the standard interface and lifecycle for Data Handlers.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, Optional

# Module-level logger
logger = logging.getLogger("DataHandler")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class DataHandlerError(Exception):
    """Base exception for all DataHandler operations."""
    pass


class DataConnectionError(DataHandlerError):
    """Raised when establishing or terminating a data connection fails."""
    pass


class DataValidationError(DataHandlerError):
    """Raised when data or schema validation fails."""
    pass


class DataExecutionError(DataHandlerError):
    """Raised when executing queries or data operations fails."""
    pass


class DataHandler(ABC):
    """
    Abstract Base Class for data handlers.

    Enforces a consistent Object-Oriented contract across diverse storage backends
    (SQL databases, CSV/Parquet files, object stores, and APIs).

    Provides:
    - Connection lifecycle methods (`connect`, `disconnect`).
    - Core abstract I/O methods (`read`, `write`).
    - Python Context Manager protocol (`__enter__`, `__exit__`).
    - Source validation and metadata tracking.
    """

    def __init__(self, source: Optional[str] = None, **kwargs: Any) -> None:
        """
        Initialize the DataHandler base class.

        :param source: Connection string, file path, or resource URI.
        :param kwargs: Additional configuration options.
        """
        self.source: Optional[str] = source
        self.config: Dict[str, Any] = kwargs
        self.is_connected: bool = False
        self.metadata: Dict[str, Any] = {}
        self.status: str = "INITIALIZED"
        logger.info(f"Initialized {self.__class__.__name__} with source='{self.source}'.")

    # Context Manager Protocol
    def __enter__(self) -> "DataHandler":
        """Enter runtime context and automatically connect."""
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """Exit runtime context and safely disconnect."""
        self.disconnect()
        # Do not suppress exceptions
        return False

    @abstractmethod
    def connect(self) -> Any:
        """
        Establish a connection or open access to the data source.

        :return: Backend connection or client handle.
        :raises DataConnectionError: If connection cannot be established.
        """
        raise NotImplementedError("Subclasses must implement the 'connect' method.")

    @abstractmethod
    def disconnect(self) -> None:
        """
        Safely terminate the connection and release resources.
        """
        raise NotImplementedError("Subclasses must implement the 'disconnect' method.")

    @abstractmethod
    def read(self, *args: Any, **kwargs: Any) -> Any:
        """
        Read or retrieve data from the configured source.

        :return: Loaded dataset (e.g., list of records, DataFrame, or stream).
        :raises DataExecutionError: If data retrieval fails.
        """
        raise NotImplementedError("Subclasses must implement the 'read' method.")

    @abstractmethod
    def write(self, data: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Write, load, or persist data to the destination.

        :param data: Data payload to persist.
        :return: Execution summary or row count.
        :raises DataExecutionError: If write operation fails.
        """
        raise NotImplementedError("Subclasses must implement the 'write' method.")

    def validate_source(self) -> bool:
        """
        Validate whether the configured source is specified and non-empty.

        :return: True if valid, False otherwise.
        """
        return bool(self.source and str(self.source).strip())

    def get_metadata(self) -> Dict[str, Any]:
        """
        Retrieve operational metadata for the handler.

        :return: Metadata dictionary.
        """
        return {
            "handler_class": self.__class__.__name__,
            "source": self.source,
            "is_connected": self.is_connected,
            "status": self.status,
            **self.metadata,
        }

