from fastapi import APIRouter
from app.services.map_markers import MapMarkersService
from app.services.communities import CommunitiesService
from app.services.events import EventsService
from app.services.sponsors import SponsorsService
from app.services.newsletter import NewsletterService
from app.services.sync_meetup import SyncMeetupService

router = APIRouter(prefix="/api")

map_markers_service = MapMarkersService()
communities_service = CommunitiesService()
events_service = EventsService()
sponsors_service = SponsorsService()
newsletter_service = NewsletterService()
sync_meetup_service = SyncMeetupService()

@router.get("/map-markers", tags=["map-markers"])
async def getMapMarkers() -> list[dict]:
    """
    Retrieve all community map markers.

    Returns
    -------
    list[dict]
        A list of dictionaries with each community's map marker details.
    """
    return await map_markers_service.all()

@router.get("/communities", tags=["communities"])
async def getCommunities() -> list[dict]:
    """
    Retrieve all active communities.

    Returns
    -------
    list[dict]
        A list of dictionaries with each community's details.
    """
    return await communities_service.all()

@router.get("/events", tags=["events"])
async def getEvents() -> list[dict]:
    """
    Retrieve all active events.

    Returns
    -------
    list[dict]
        A list of dictionaries with each event's details.
    """
    return await events_service.all()

@router.get("/sponsors", tags=["sponsors"])
async def getSponsors() -> list[dict]:
    """
    Retrieve all active sponsors.

    Returns
    -------
    list[dict]
        A list of dictionaries with each sponsor's details.
    """
    return await sponsors_service.all()

@router.get("/newsletter/subscription", tags=["newsletter"])
async def getNewsletterSubscription(email: str) -> dict:
    """
    Retrieve the newsletter subscription status for an email address.

    Parameters
    ----------
    email : str
        The email address to check.

    Returns
    -------
    dict
        A dictionary with the subscription status for the given email.
    """
    return await newsletter_service.status(email)

@router.post("/newsletter/subscribe", tags=["newsletter"])
async def subscribeToNewsletter(email: str) -> dict:
    """
    Subscribe an email address to the newsletter.

    Parameters
    ----------
    email : str
        The email address to subscribe.

    Returns
    -------
    dict
        A dictionary with the resulting subscription status.
    """
    return await newsletter_service.subscribe(email)

@router.post("/newsletter/unsubscribe", tags=["newsletter"])
async def unsubscribeFromNewsletter(email: str) -> dict:
    """
    Unsubscribe an email address from the newsletter.

    Parameters
    ----------
    email : str
        The email address to unsubscribe.

    Returns
    -------
    dict
        A dictionary with the resulting subscription status.
    """
    return await newsletter_service.unsubscribe(email)

@router.get("/sync-meetup", tags=["sync-meetup"])
async def syncMeetup() -> dict:
    """
    Trigger the synchronization of Meetup events.

    Returns
    -------
    dict
        A dictionary with the synchronization result, describing success or the
        specific failure raised while processing the Meetup data.
    """
    try:
        await sync_meetup_service.handle()
        return {
            "success": True,
            "message": "Meetup synchronization completed successfully.",
        }
    except Exception as exc:
        return {
            "success": False,
            "message": "Meetup synchronization failed.",
            "error": str(exc),
        }