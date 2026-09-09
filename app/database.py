import psycopg
from psycopg import AsyncConnection, DatabaseError
from app.config import DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD

class PostgreSQL:
    """
    Manage an asynchronous connection to a PostgreSQL database.

    The connection settings are loaded from :mod:`app.config`. The instance
    stores the active connection and provides methods for connection lifecycle
    and transaction management.
    """

    def __init__(self) -> None:
        """
        Initialize a PostgreSQL connection manager.

        The connection is not opened until :meth:`connect` is called.

        Attributes
        ----------
        connection : psycopg.AsyncConnection or None
            The active asynchronous database connection, or ``None`` when no
            connection has been opened.
        """
        self.connection: AsyncConnection | None = None

    async def connect(self) -> AsyncConnection:
        """
        Open an asynchronous connection to PostgreSQL.

        Returns
        -------
        psycopg.AsyncConnection
            The open asynchronous connection.

        Raises
        ------
        ValueError
            If the connection fails or an unexpected error occurs.
        """
        try:
            self.connection = await psycopg.AsyncConnection.connect(
                user=DB_USERNAME,
                password=DB_PASSWORD,
                host=DB_HOST,
                dbname=DB_DATABASE,
                port=DB_PORT,
            )
            return self.connection

        except DatabaseError as e:
            raise ValueError(f"Error connecting to the database: {e}")

        except Exception as e:
            raise ValueError(f"An unexpected error occurred: {e}")

    def _get_connection(self) -> AsyncConnection:
        """
        Return the active database connection.

        Returns
        ------
        psycopg.AsyncConnection
            The active asynchronous database connection.

        Raises
        ------
        RuntimeError
            If no open database connection is available.
        """
        if self.connection is None or self.connection.closed:
            raise RuntimeError("The database connection is not open")
        return self.connection

    async def close(self) -> None:
        """
        Close the current database connection.

        This method has no effect if no connection has been opened or if the
        connection is already closed.
        """
        if self.connection is not None and not self.connection.closed:
            await self.connection.close()

    async def commit(self) -> None:
        """
        Commit the current transaction.

        Raises
        ------
        RuntimeError
            If no open database connection is available.
        """
        await self._get_connection().commit()

    async def rollback(self) -> None:
        """
        Roll back the current transaction.

        Raises
        ------
        RuntimeError
            If no open database connection is available.
        """
        await self._get_connection().rollback()

    async def beginTransaction(self) -> None:
        """
        Begin a database transaction.

        Raises
        ------
        RuntimeError
            If no open database connection is available.
        """
        await self._get_connection().execute("BEGIN")
