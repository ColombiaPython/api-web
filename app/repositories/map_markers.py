from app.repositories.base import BaseRepository

class MapMarkersRepository(BaseRepository):
    """Repository for retrieving community map marker records from the database."""

    async def all(self) -> list[dict]:
        """
        Retrieve all community map markers.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each community's identifier,
            name, description, city, geographic coordinates, and URL.
        """

        query: str = """
            SELECT
                public.communities.id AS id,
                public.communities.name AS name,
                public.communities.description AS description,
                divipola.municipalities.name AS city,
                public.map_markers.latitude AS latitude,
                public.map_markers.longitude AS longitude,
                public.communities.community_url AS url
            FROM
                public.map_markers
            INNER JOIN
                public.communities ON (
                    public.communities.id = public.map_markers.community_id
                )
            INNER JOIN
                divipola.municipalities ON (
                    divipola.municipalities.code = public.communities.municipality_code
                )
            WHERE
                public.map_markers.is_active = true
        """

        return await self.query(query)
