from app.repositories.events import EventsRepository


class EventsService:
    """Service layer for exposing event data to the API."""

    def __init__(self) -> None:
        """
        Initialize the events service.

        The service creates the repository used to retrieve event data.
        """
        self.repository = EventsRepository()

    async def all(self) -> list[dict]:
        """
        Retrieve all active events.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each event's details, including
            its identifier, title, start date, location, mode, cover image, and URL.
        """

        data: list[dict] = await self.repository.all()

        return [
            {
                "id": event["id"],
                "title": event["title"],
                "startsAt": event["starts_at"],
                "location": event["location"],
                "mode": event["mode"],
                "coverImage": event["cover_image"],
                "eventUrl": event["event_url"],
            }
            for event in data
        ]