from app.database import PostgreSQL

class BaseRepository:
    """
    Base repository class for managing database connections.

    This class provides a singleton-like pattern for managing PostgreSQL database
    connections across repository instances.

    Attributes
    ----------
    conn_instance : PostgreSQL or None
        Cached PostgreSQL connection instance. Initialized on first access.
    """

    conn_instance: PostgreSQL | None = None

    async def connection(self) -> PostgreSQL:
        """
        Get or create a PostgreSQL database connection.

        Returns the cached connection instance if available, otherwise creates
        a new connection and caches it for future use.

        Returns
        -------
        PostgreSQL
            The PostgreSQL connection instance.
        """
        if self.conn_instance is None:
            self.conn_instance = await PostgreSQL().connect()
        return self.conn_instance

    async def query(self, query: str, parameters: tuple = ()) -> list[dict]:
        """
        Execute a SELECT query and return results as dictionaries.

        Executes the provided SQL query and returns all rows as a list of
        dictionaries, where each dictionary maps column names to their values.

        Parameters
        ----------
        query : str
            The SQL SELECT query to execute.

        Returns
        -------
        list[dict]
            A list of dictionaries, one per row. Each dictionary maps column
            names to their corresponding values.
        """
        async with (await self.connection()).cursor() as cursor:
            await cursor.execute(query, parameters)
            result = await cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in result]

    async def find(self, query: str, parameters: tuple = ()) -> dict:
        """
        Execute a SELECT query and return the first result as a dictionary.

        Executes the provided SQL query and returns the first row as a dictionary,
        where the dictionary maps column names to their values. If no rows are
        returned, an empty dictionary is returned.

        Parameters
        ----------
        query : str
            The SQL SELECT query to execute.

        Returns
        -------
        dict
            A dictionary mapping column names to their corresponding values
            for the first row of the result set, or an empty dictionary if no
            rows are returned.
        """
        async with (await self.connection()).cursor() as cursor:
            await cursor.execute(query, parameters)
            row = await cursor.fetchone()
            if row is None:
                return {}
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))

    async def execute(self, query: str, parameters: tuple = ()) -> None:
        """
        Execute a SQL query without returning any results.

        This method is useful for executing INSERT, UPDATE, DELETE, or other
        SQL statements that do not return rows.

        Parameters
        ----------
        query : str
            The SQL query to execute.
        """
        async with (await self.connection()).cursor() as cursor:
            await cursor.execute(query, parameters)
            await (await self.connection()).commit()
