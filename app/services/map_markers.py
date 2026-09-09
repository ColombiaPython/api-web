from app.repositories.map_markers import MapMarkersRepository

class MapMarkersService:
    """Service layer for exposing community map marker data to the API."""

    def __init__(self) -> None:
        """
        Initialize the map markers service.

        The service creates the repository used to retrieve community map
        marker data.
        """
        self.repository = MapMarkersRepository()

    async def all(self) -> list[dict]:
        """
        Retrieve all community map markers.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each community's identifier,
            name, description, city, geographic coordinates, and URL.
        """

        data: list[dict] = await self.repository.all()

        return [
            {
                "id": marker["id"],
                "name": marker["name"],
                "description": marker["description"],
                "city": marker["city"],
                "coordinates": {
                    "lat": marker["latitude"],
                    "lng": marker["longitude"],
                },
                "communityUrl": marker["url"],
            }
            for marker in data
        ]
