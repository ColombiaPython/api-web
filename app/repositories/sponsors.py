from app.repositories.base import BaseRepository

class SponsorsRepository(BaseRepository):
    """Repository for retrieving sponsor records from the database."""

    async def all(self) -> list[dict]:
        """
        Retrieve all active sponsors.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each sponsor's details, including
            its identifier, name, website URL, and logo image.
        """

        query: str = """
            SELECT
                public.sponsors.id AS id,
                public.sponsors.name AS name,
                public.sponsors.website_url AS website_url,
                public.sponsors.logo_image AS logo_image
            FROM
                public.sponsors
            WHERE
                public.sponsors.is_active = true
        """

        return await self.query(query)
