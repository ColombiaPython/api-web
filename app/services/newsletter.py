from app.repositories.newsletter import NewsletterRepository

class NewsletterService:
    """Service layer for managing newsletter subscriptions."""

    def __init__(self) -> None:
        """
        Initialize the newsletter service.

        The service creates the repository used to manage subscription data.
        """
        self.repository = NewsletterRepository()

    async def status(self, email: str) -> dict:
        """
        Retrieve the newsletter subscription status for an email address.

        Parameters
        ----------
        email : str
            The email address to check.

        Returns
        -------
        dict
            A dictionary with the normalized email, whether it is registered,
            and whether the subscription is currently active.
        """
        normalized_email = self._normalize_email(email)
        subscription = await self.repository.findByEmail(normalized_email)

        return {
            "email": normalized_email,
            "isRegistered": bool(subscription),
            "isActive": bool(subscription and subscription["is_active"]),
        }

    async def subscribe(self, email: str) -> dict:
        """
        Subscribe an email address to the newsletter.

        Parameters
        ----------
        email : str
            The email address to subscribe.

        Returns
        -------
        dict
            A dictionary with the normalized email and its active
            subscription status.
        """
        normalized_email = self._normalize_email(email)
        await self.repository.subscribe(normalized_email)

        return {
            "email": normalized_email,
            "isRegistered": True,
            "isActive": True,
        }

    async def unsubscribe(self, email: str) -> dict:
        """
        Unsubscribe an email address from the newsletter.

        Parameters
        ----------
        email : str
            The email address to unsubscribe.

        Returns
        -------
        dict
            A dictionary with the normalized email, its active status, and
            whether the unsubscription was applied.
        """
        normalized_email = self._normalize_email(email)
        unsubscribed = await self.repository.unsubscribe(normalized_email)

        return {
            "email": normalized_email,
            "isActive": not unsubscribed,
            "unsubscribed": unsubscribed,
        }

    @staticmethod
    def _normalize_email(email: str) -> str:
        """
        Normalize an email address for consistent storage and lookup.

        Parameters
        ----------
        email : str
            The email address to normalize.

        Returns
        -------
        str
            The trimmed, lowercased email address.
        """
        return email.strip().lower()