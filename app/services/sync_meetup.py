from datetime import datetime, timezone
import httpx
from app.config import HASH_MEETUP
from app.repositories.communities import CommunitiesRepository
from app.repositories.events import EventsRepository

class SyncMeetupService:

    api_url: str = "https://www.meetup.com/gql2"
    sha256_hash: str = HASH_MEETUP

    @staticmethod
    def currentTimestamp() -> str:
        """
        Return the current UTC timestamp in Meetup-compatible ISO format.

        Returns
        -------
        str
            A UTC timestamp string with millisecond precision, formatted as
            ``YYYY-MM-DDTHH:MM:SS.mmmZ``.
        """
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")

    def __init__(self) -> None:
        """
        Initialize the SyncMeetupService instance with repository instances for
        communities and events.
        """
        self._communities_repo = CommunitiesRepository()
        self._events_repo = EventsRepository()

    def createPayload(self, urlname: str, after_date_time: str | None = None) -> dict:
        """
        Build the GraphQL request payload for a Meetup group query.

        Parameters
        ----------
        urlname : str
            Meetup group slug used as the query identifier.
        after_date_time : str or None, optional
            Lower bound for event retrieval in ISO-8601 format. If not provided,
            the current UTC timestamp is used.

        Returns
        -------
        dict
            Payload sent to the Meetup GraphQL endpoint.
        """

        if after_date_time is None:
            after_date_time = self.currentTimestamp()

        return {
            "operationName": "getUpcomingGroupEvents",
            "variables": {
                "urlname": urlname,
                "afterDateTime": after_date_time
            },
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": self.sha256_hash
                }
            }
        }

    @staticmethod
    def eventCoverImage(event: dict) -> str | None:
        """
        Extract the most relevant cover image URL from the Meetup event payload.

        Parameters
        ----------
        event : dict
            Meetup event node returned by the GraphQL API.

        Returns
        -------
        str or None
            The highest-quality available image URL, or ``None`` if no image is
            available.
        """
        for photo_key in ("featuredEventPhoto", "displayPhoto"):
            photo = event.get(photo_key) or {}
            for key in ("highResUrl", "highresLink", "photoLink", "url", "link"):
                value = photo.get(key)
                if value:
                    return value
        return None

    @staticmethod
    def eventLocation(event: dict) -> str:
        """
        Resolve a human-readable location string for the event.

        Parameters
        ----------
        event : dict
            Meetup event node.

        Returns
        -------
        str
            The venue name or a fallback location descriptor. Meetup returns a
            null venue for many published events, so a placeholder is used to
            honor the not-null constraint of the events table.
        """
        venue = event.get("venue") or {}
        candidates = [
            venue.get("name"),
            venue.get("city"),
            venue.get("address"),
            event.get("location"),
            event.get("city"),
            event.get("address"),
        ]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate.strip()

        mode = SyncMeetupService.eventMode(event)
        return mode if mode == "Virtual" else "Por definir"

    @staticmethod
    def eventMode(event: dict) -> str:
        """
        Normalize the Meetup event mode to the values accepted by the database.

        Parameters
        ----------
        event : dict
            Meetup event node.

        Returns
        -------
        str
            A normalized mode value: ``Presencial``, ``Virtual`` or ``Híbrido``.
        """
        event_type = str(event.get("eventType") or "").upper()
        if event_type == "HYBRID":
            return "Híbrido"
        if event.get("isOnline") or event_type in {"ONLINE", "VIRTUAL"}:
            return "Virtual"
        return "Presencial"

    @staticmethod
    def eventTitle(event: dict) -> str:
        """
        Return the Meetup event title with a fallback value.

        Parameters
        ----------
        event : dict
            Meetup event node.

        Returns
        -------
        str
            The event title or a default label when it is missing.
        """
        return event.get("title") or "Meetup Event"

    @staticmethod
    def eventStartsAt(event: dict) -> datetime | None:
        """
        Parse the event start timestamp from the Meetup payload.

        Parameters
        ----------
        event : dict
            Meetup event node.

        Returns
        -------
        datetime or None
            A timezone-aware UTC datetime instance, or ``None`` when the value is
            missing or invalid.
        """
        raw_value = (
            event.get("dateTime")
            or event.get("startTime")
            or event.get("date")
            or event.get("startsAt")
        )
        if raw_value is None:
            return None

        if isinstance(raw_value, datetime):
            return raw_value if raw_value.tzinfo is not None else raw_value.replace(tzinfo=timezone.utc)

        value = str(raw_value).replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    @staticmethod
    def normalizeMeetupEvent(community_id: int, event: dict) -> dict:
        """
        Normalize a Meetup event node into the structure expected by the database.

        Parameters
        ----------
        community_id : int
            Identifier of the community linked to the meetup slug.
        event : dict
            Raw event node returned by Meetup.

        Returns
        -------
        dict
            A normalized payload ready to be persisted into the events table.
        """
        external_id = event.get("id")
        if isinstance(external_id, str):
            try:
                external_id = int(external_id)
            except ValueError:
                external_id = None

        event_url = event.get("eventUrl") or event.get("url") or event.get("link") or ""

        return {
            "communityId": community_id,
            "title": SyncMeetupService.eventTitle(event),
            "startsAt": SyncMeetupService.eventStartsAt(event),
            "location": SyncMeetupService.eventLocation(event),
            "mode": SyncMeetupService.eventMode(event),
            "coverImage": SyncMeetupService.eventCoverImage(event),
            "eventUrl": event_url,
            "externalId": external_id,
        }

    @staticmethod
    def extractMeetupEvents(response_data: dict) -> list[dict]:
        """
        Extract raw event nodes from the Meetup GraphQL response.

        Parameters
        ----------
        response_data : dict
            Full GraphQL JSON response.

        Returns
        -------
        list[dict]
            Event nodes from the ``events`` edge list.
        """
        group_data = response_data.get("data", {}).get("groupByUrlname") or {}
        events_data = group_data.get("events") or group_data.get("upcomingEvents") or {}
        edges = events_data.get("edges") or []

        extracted: list[dict] = []
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            node = edge.get("node") or edge
            if isinstance(node, dict):
                extracted.append(node)

        return extracted

    async def handle(self):
        """
        Synchronize upcoming Meetup events for every active community slug.

        Returns
        -------
        None
            This method issues the GraphQL requests and persists all normalized
            event records through the repository.
        """
        meetup_slugs: list[dict] = await self._communities_repo.meetupSlugs()

        for slug_data in meetup_slugs:
            urlname = (slug_data.get("slug") or "").strip()
            community_id = slug_data.get("community_id")

            if not urlname or community_id is None:
                continue

            payload = self.createPayload(urlname)

            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                meetup_response = response.json()

            for event in self.extractMeetupEvents(meetup_response):
                normalized_event = self.normalizeMeetupEvent(community_id, event)
                if normalized_event.get("externalId") is None or normalized_event.get("startsAt") is None:
                    continue
                await self._events_repo.saveMeetupEvent(normalized_event)