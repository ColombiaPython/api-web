from app.repositories.base import BaseRepository

class NewsletterRepository(BaseRepository):
    """Repository for managing newsletter subscription records in the database."""

    async def findByEmail(self, email: str) -> dict:
        """
        Retrieve a newsletter subscription by email address.

        Parameters
        ----------
        email : str
            The email address to search for.

        Returns
        -------
        dict
            A dictionary with the subscription details, or an empty dictionary
            if no subscription is found for the given email.
        """
        query: str = """
            SELECT
                id,
                email,
                is_active,
                subscription_date,
                unsubscription_date
            FROM newsletter.subscribed_emails
            WHERE email = %s
        """

        return await self.find(query, (email,))

    async def subscribe(self, email: str) -> None:
        """
        Create or reactivate a newsletter subscription for an email address.

        If the email is already registered, its subscription is reactivated
        and the unsubscription date is cleared.

        Parameters
        ----------
        email : str
            The email address to subscribe.
        """
        query: str = """
            INSERT INTO newsletter.subscribed_emails (email, is_active, subscription_date, unsubscription_date)
            VALUES (%s, true, CURRENT_TIMESTAMP, NULL)
            ON CONFLICT (email) DO UPDATE
            SET
                is_active = true,
                subscription_date = CURRENT_TIMESTAMP,
                unsubscription_date = NULL
        """

        await self.execute(query, (email,))

    async def unsubscribe(self, email: str) -> bool:
        """
        Deactivate an active newsletter subscription for an email address.

        Parameters
        ----------
        email : str
            The email address to unsubscribe.

        Returns
        -------
        bool
            ``True`` if an active subscription was found and deactivated,
            ``False`` otherwise.
        """
        query: str = """
            UPDATE newsletter.subscribed_emails
            SET
                is_active = false,
                unsubscription_date = CURRENT_TIMESTAMP
            WHERE email = %s AND is_active = true
            RETURNING id
        """

        return bool(await self.find(query, (email,)))