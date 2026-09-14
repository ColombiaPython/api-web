from datetime import datetime, timezone
from app.repositories.base import BaseRepository

class EventsRepository(BaseRepository):
    """Repository for persisting meetup event records."""

    async def saveMeetupEvent(self, event: dict) -> None:
        """
        Persist one normalized Meetup event record into the database.

        Parameters
        ----------
        event : dict
            Normalized event payload containing the community identifier,
            title, start time, location, mode, cover image, event URL, and
            external Meetup identifier.

        Returns
        -------
        None
            The method refreshes the stored record when the external identifier
            is already known and any of its fields changed, inserts it when the
            identifier is new, and does not return a value.
        """

        event_id: int | None = event.get("externalId")
        if event_id is None:
            return

        now: datetime = datetime.now(timezone.utc)
        values: tuple = (
            event["communityId"],
            event["title"],
            event["startsAt"],
            event["location"],
            event["mode"],
            event["coverImage"],
            event["eventUrl"],
        )

        update_query: str = """
            UPDATE public.events
            SET
                community_id = %s,
                title = %s,
                starts_at = %s,
                location = %s,
                mode = %s,
                cover_image = %s,
                event_url = %s,
                updated_at = %s
            WHERE
                public.events.external_id = %s
                AND (
                    public.events.community_id IS DISTINCT FROM %s
                    OR public.events.title IS DISTINCT FROM %s
                    OR public.events.starts_at IS DISTINCT FROM %s
                    OR public.events.location IS DISTINCT FROM %s
                    OR public.events.mode IS DISTINCT FROM %s
                    OR public.events.cover_image IS DISTINCT FROM %s
                    OR public.events.event_url IS DISTINCT FROM %s
                )
        """

        await self.execute(update_query, (*values, now, event_id, *values))

        insert_query: str = """
            INSERT INTO public.events (
                community_id,
                title,
                starts_at,
                location,
                mode,
                cover_image,
                event_url,
                is_active,
                created_at,
                updated_at,
                external_id
            )
            SELECT %s, %s, %s, %s, %s, %s, %s, true, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1
                FROM public.events
                WHERE public.events.external_id = %s
            )
            ON CONFLICT DO NOTHING
        """

        await self.execute(insert_query, (*values, now, now, event_id, event_id))

    async def all(self) -> list[dict]:
        """
        Retrieve all active events from the database.

        Returns
        -------
        list[dict]
            A list of dictionaries containing each active event's identifier,
            title, start date, location, mode, cover image, and event URL.
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