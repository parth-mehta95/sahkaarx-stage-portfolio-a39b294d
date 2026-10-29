"""
data_handler.py
Base module defining the abstract DataHandler class.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

# Configure logger
logger = logging.getLogger(__name__)


class DataHandler(ABC):
    """
    Abstract base class for data handling operations.
    
    Provides the foundational interface and shared lifecycle management
    for loading, processing, and handling data across various data sources
    (e.g., databases, CSV/JSON files, APIs).
    """

    def __init__(self, source: str, **kwargs: Any) -> None:
        """
        Initialize the DataHandler instance.

        :param source: Identifier or path for the data source (e.g., db path, URI, file path).
        :param kwargs: Additional configuration options for connection or ingestion.
        """
        self.source: str = source
        self.config: Dict[str, Any] = kwargs
        self.is_connected: bool = False
        self._connection: Optional[Any] = None
        self.metadata: Dict[str, Any] = {}
        logger.info(f"Initialized {self.__class__.__name__} with source: {self.source}")

    @abstractmethod
    def connect(self) -> Any:
        """
        Establish a connection to the data source.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Close any active connections and clean up resources.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def load_data(self, query_or_params: Any, **kwargs: Any) -> Any:
        """
        Load data from the source.
        Must be implemented by subclasses.

        :param query_or_params: Query string, parameters, or specifications for loading data.
        :param kwargs: Additional options for data loading.
        :return: Extracted data in a structured format (e.g., list of dicts, records, DataFrame).
        """
        pass

    def validate_source(self) -> bool:
        """
        Validate whether the source specification is valid and non-empty.

        :return: True if source is valid, False otherwise.
        """
        return bool(self.source and isinstance(self.source, str) and self.source.strip())

    def get_status(self) -> Dict[str, Any]:
        """
        Return the current state and connection metadata of the handler.

        :return: Dictionary containing handler status.
        """
        return {
            "handler_type": self.__class__.__name__,
            "source": self.source,
            "is_connected": self.is_connected,
            "metadata": self.metadata,
        }

    def __enter__(self) -> "DataHandler":
        """
        Context manager entry: auto-connects to the source.
        """
        self.connect()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Context manager exit: auto-disconnects from the source.
        """
        self.disconnect()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(source='{self.source}', connected={self.is_connected})>"

