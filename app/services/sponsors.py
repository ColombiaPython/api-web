from app.repositories.sponsors import SponsorsRepository

class SponsorsService:
    """Service layer for exposing sponsor data to the API."""

    def __init__(self) -> None:
        """
        Initialize the sponsors service.

        The service creates the repository used to retrieve sponsor data.
        """
        self.repository = SponsorsRepository()

    async def all(self) -> list[dict]:
        """
        Retrieve all active sponsors.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each sponsor's details, including
            its identifier, name, website URL, and logo image.
        """

        data: list[dict] = await self.repository.all()

        return [
            {
                "id": sponsor["id"],
                "name": sponsor["name"],
                "websiteUrl": sponsor["website_url"],
                "logoImage": sponsor["logo_image"],
            }
            for sponsor in data
        ]
