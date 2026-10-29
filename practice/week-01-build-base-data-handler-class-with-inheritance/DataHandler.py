"""
DataHandler Module

This module provides a reusable Object-Oriented Programming (OOP) foundation
for consistent data handling across various input and output formats such as
CSV files and database sources.

Classes:
    - DataHandler: Base abstract/parent class defining the interface for data operations.
    - CSVDataHandler: Child class specialized for handling CSV file input and output.
    - DatabaseDataHandler: Child class providing structure for database operations.
"""

from abc import ABC, abstractmethod
import csv
import os
from typing import Any, Dict, List, Optional, Union


class DataHandler(ABC):
    """
    Abstract base class for data handlers.

    Provides a standard blueprint for reading from and writing to
    different data sources (e.g., CSV, SQL databases, JSON, APIs).

    Attributes:
        data_source (str): Identifier or path for the data source.
        data (Optional[Any]): In-memory representation of loaded data.
    """

    def __init__(self, data_source: Optional[str] = None) -> None:
        """
        Initialize the DataHandler base class.

        Args:
            data_source (Optional[str]): Path, connection string, or identifier
                                         of the data source.
        """
        self.data_source = data_source
        self.data: Optional[Any] = None

    @abstractmethod
    def read(self, *args, **kwargs) -> Any:
        """
        Read data from the configured data source.

        Subclasses must implement this method according to their specific source.

        Returns:
            Any: The loaded data.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the 'read' method.")

    @abstractmethod
    def write(self, data: Optional[Any] = None, *args, **kwargs) -> Any:
        """
        Write data to the destination.

        Subclasses must implement this method according to their specific destination.

        Args:
            data (Optional[Any]): The data to write. If None, uses self.data.

        Raises:
            NotImplementedError: If not implemented in a subclass.
        """
        raise NotImplementedError("Subclasses must implement the 'write' method.")

    def get_data(self) -> Optional[Any]:
        """
        Return the currently loaded data.

        Returns:
            Optional[Any]: The data currently held in memory.
        """
        return self.data


class CSVDataHandler(DataHandler):
    """
    Child class inheriting from DataHandler for CSV-specific data processing.

    Handles reading from and writing to CSV files with configurable delimiter
    and encoding settings.

    Attributes:
        file_path (str): File path to the CSV file.
        delimiter (str): Delimiter character used in the CSV.
        encoding (str): Encoding format for reading/writing files.
        data (List[Dict[str, Any]]): List of row dictionaries representing CSV data.
    """

    def __init__(
        self,
        file_path: Optional[str] = None,
        delimiter: str = ",",
        encoding: str = "utf-8",
    ) -> None:
        """
        Initialize the CSVDataHandler.

        Args:
            file_path (Optional[str]): Path to the target CSV file.
            delimiter (str): Column delimiter character. Defaults to ','.
            encoding (str): Text encoding. Defaults to 'utf-8'.
        """
        super().__init__(data_source=file_path)
        self.delimiter = delimiter
        self.encoding = encoding
        self.data: List[Dict[str, Any]] = []

    @property
    def file_path(self) -> Optional[str]:
        """Get the current CSV file path."""
        return self.data_source

    @file_path.setter
    def file_path(self, path: str) -> None:
        """Set the CSV file path."""
        self.data_source = path

    def read(self, file_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Read tabular data from a CSV file into a list of dictionaries.

        Args:
            file_path (Optional[str]): Path to the CSV file. If provided, updates
                                      the handler's target file path.

        Returns:
            List[Dict[str, Any]]: Parsed rows with column headers as keys.

        Raises:
            ValueError: If no file path is specified.
            FileNotFoundError: If the CSV file does not exist.
        """
        target_path = file_path or self.file_path
        if not target_path:
            raise ValueError("CSV file path must be provided to read data.")

        if not os.path.exists(target_path):
            raise FileNotFoundError(f"CSV file not found: {target_path}")

        records: List[Dict[str, Any]] = []
        with open(target_path, mode="r", encoding=self.encoding, newline="") as csvfile:
            reader = csv.DictReader(csvfile, delimiter=self.delimiter)
            for row in reader:
                records.append(dict(row))

        self.data = records
        self.data_source = target_path
        return self.data

    def write(
        self,
        data: Optional[Union[List[Dict[str, Any]], List[List[Any]]]] = None,
        output_path: Optional[str] = None,
        fieldnames: Optional[List[str]] = None,
    ) -> str:
        """
        Write tabular data to a CSV file.

        Supports writing a list of dictionaries (standard) or a list of rows.

        Args:
            data (Optional[Union[List[Dict[str, Any]], List[List[Any]]]]):
                Data to be written. If omitted, uses self.data.
            output_path (Optional[str]): Destination file path. If omitted,
                writes back to the current file_path.
            fieldnames (Optional[List[str]]): Column headers for the CSV file.
                Extracted automatically if data is a list of dictionaries.

        Returns:
            str: Destination file path written to.

        Raises:
            ValueError: If no data is available to write or no destination is specified.
        """
        payload = data if data is not None else self.data
        destination = output_path or self.file_path

        if not destination:
            raise ValueError("An output destination path must be specified to write CSV data.")

        if not payload:
            raise ValueError("No data provided to write.")

        # Ensure parent directory exists if path contains directories
        output_dir = os.path.dirname(destination)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        with open(destination, mode="w", encoding=self.encoding, newline="") as csvfile:
            # Check if payload is list of dictionaries
            if isinstance(payload[0], dict):
                columns = fieldnames or list(payload[0].keys())
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=columns,
                    delimiter=self.delimiter,
                )
                writer.writeheader()
                for row in payload:
                    writer.writerow(row)
            # Fallback for list of lists / tuples
            elif isinstance(payload[0], (list, tuple)):
                writer = csv.writer(csvfile, delimiter=self.delimiter)
                if fieldnames:
                    writer.writerow(fieldnames)
                for row in payload:
                    writer.writerow(row)
            else:
                raise ValueError("Unsupported data format for CSV writing. Expecting list of dicts or rows.")

        return destination


class DatabaseDataHandler(DataHandler):
    """
    Child class inheriting from DataHandler for database connections.

    Serves as an extensible class for SQL-based databases (e.g. SQLite, PostgreSQL).

    Attributes:
        connection_string (str): Database connection string / URI.
        data (List[Dict[str, Any]]): Result set records from executed queries.
    """

    def __init__(self, connection_string: Optional[str] = None) -> None:
        """
        Initialize the DatabaseDataHandler.

        Args:
            connection_string (Optional[str]): Database connection string.
        """
        super().__init__(data_source=connection_string)
        self.data: List[Dict[str, Any]] = []

    @property
    def connection_string(self) -> Optional[str]:
        """Get the database connection string."""
        return self.data_source

    @connection_string.setter
    def connection_string(self, conn: str) -> None:
        """Set the database connection string."""
        self.data_source = conn

    def read(self, query: str = "", *args, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute a read query against the database.

        Args:
            query (str): SQL SELECT query string.

        Returns:
            List[Dict[str, Any]]: Query result rows.
        """
        if not self.data_source:
            raise ValueError("Database connection string must be configured.")
        if not query:
            raise ValueError("A SQL query must be provided to read data.")

        # Mock / Extensible stub implementation
        # Can be integrated with sqlite3, psycopg2, sqlalchemy, etc.
        print(f"Executing query on [{self.data_source}]: {query}")
        return self.data

    def write(self, data: Optional[Any] = None, table_name: str = "", *args, **kwargs) -> Any:
        """
        Insert or update records in a target database table.

        Args:
            data (Optional[Any]): Data to insert or update.
            table_name (str): Destination database table name.
        """
        if not self.data_source:
            raise ValueError("Database connection string must be configured.")
        if not table_name:
            raise ValueError("A target table name must be specified.")

        payload = data if data is not None else self.data
        print(f"Writing {len(payload) if hasattr(payload, '__len__') else 'data'} record(s) to table '{table_name}'.")
        return True


if __name__ == "__main__":
    # Demonstration of CSVDataHandler usage
    sample_data = [
        {"id": "1", "name": "Alice", "role": "Data Engineer"},
        {"id": "2", "name": "Bob", "role": "Data Analyst"},
        {"id": "3", "name": "Charlie", "role": "ML Engineer"},
    ]

    temp_csv = "temp_sample.csv"
    handler = CSVDataHandler(file_path=temp_csv)

    print("--- Writing Data to CSV ---")
    handler.write(data=sample_data)
    print(f"Successfully wrote data to {temp_csv}")

    print("\n--- Reading Data from CSV ---")
    loaded_data = handler.read()
    print("Loaded records:")
    for record in loaded_data:
        print(record)

    # Clean up temporary demonstration file
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
        print(f"\nCleaned up {temp_csv}")

