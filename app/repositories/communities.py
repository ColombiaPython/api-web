from app.repositories.base import BaseRepository

class CommunitiesRepository(BaseRepository):
    """Repository for retrieving community records from the database."""

    async def all(self) -> list[dict]:
        """
        Retrieve all communities.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each community's details, including its identifier, name, description, city, cover image, and URL.
        """

        query: str = """
            SELECT
                public.communities.id AS id,
                public.communities.name AS name,
                divipola.municipalities.name AS city,
                public.communities.description AS description,
                public.communities.cover_image AS cover_image,
                public.communities.community_url AS community_url
            FROM
                public.communities
            INNER JOIN
                divipola.municipalities ON (
                    divipola.municipalities.code = public.communities.municipality_code
                )
            WHERE
                public.communities.is_active = true
        """

        return await self.query(query)

    async def meetupSlugs(self) -> list[dict]:
        """
        Retrieve all meetup slugs for the communities.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each community's meetup slug.
        """

        query: str = """
            SELECT
                public.communities_meetup_slugs.community_id AS community_id,
                public.communities_meetup_slugs.slug AS slug
            FROM
                public.communities_meetup_slugs
            INNER JOIN
                public.communities ON (
                    public.communities.id = public.communities_meetup_slugs.community_id
                )
            WHERE
                public.communities.is_active = true
        """

        return await self.query(query)