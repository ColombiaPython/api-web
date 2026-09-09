from app.repositories.base import BaseRepository

class EventsRepository(BaseRepository):
    """Repository for retrieving event records from the database."""

    async def all(self) -> list[dict]:
        """
        Retrieve all active events.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each event's details, including
            its identifier, title, start date, location, mode, cover image, and URL.
        """

        query: str = """
            SELECT
                public.events.id AS id,
                public.events.title AS title,
                public.events.starts_at AS starts_at,
                public.events.location AS location,
                public.events.mode AS mode,
                public.events.cover_image AS cover_image,
                public.events.event_url AS event_url
            FROM
                public.events
            WHERE
                public.events.is_active = true
        """

        return await self.query(query)