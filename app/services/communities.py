from app.repositories.communities import CommunitiesRepository

class CommunitiesService:
    """Service layer for exposing community data to the API."""

    def __init__(self) -> None:
        """
        Initialize the communities service.

        The service creates the repository used to retrieve community data.
        """
        self.repository = CommunitiesRepository()

    async def all(self) -> list[dict]:
        """
        Retrieve all communities.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each community's details, including its identifier, name, description, city, cover image, and URL.
        """

        data: list[dict] = await self.repository.all()

        return [
            {
                "id": community["id"],
                "name": community["name"],
                "description": community["description"],
                "city": community["city"],
                "coverImage": community["cover_image"],
                "communityUrl": community["community_url"],
            }
            for community in data
        ]
