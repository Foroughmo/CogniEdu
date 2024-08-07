from datetime import datetime, date
from google_calendar_api import authenticate_and_get_service, list_calendar_events
from db_operations import (
    get_db_connection, close_db_connection, get_user_academic_period,
    get_all_google_events, update_event, update_last_synced, insert_event,
    mark_events_as_deleted, get_last_sync_time, update_last_sync_time
)
from utils import error_handler, setup_logger

logger = setup_logger(__name__)

@error_handler
def perform_continuous_sync():
    connection = get_db_connection()
    if not connection:
        logger.error("Failed to establish database connection")
        return

    service = authenticate_and_get_service()

    last_sync_time = get_last_sync_time(connection)
    if not last_sync_time:
        logger.warning("No last sync time found. Please run initial import first.")
        return

    # Convert last_sync_time to datetime if it's a string
    if isinstance(last_sync_time, str):
        last_sync_time = datetime.fromisoformat(last_sync_time)

    # Get the user's academic period
    academic_start, academic_end = get_user_academic_period(connection)
    if not academic_start or not academic_end:
        logger.error("Failed to get user's academic period. Aborting continuous sync.")
        return

    # Convert date objects to datetime objects
    if isinstance(academic_start, date):
        academic_start = datetime.combine(academic_start, datetime.min.time())
    if isinstance(academic_end, date):
        academic_end = datetime.combine(academic_end, datetime.max.time())

    now = datetime.utcnow()
    
    # Set sync window to the entire academic period
    min_time = academic_start
    max_time = academic_end

    # Fetch events from Google Calendar for the entire academic period
    google_events = list_calendar_events(service, min_time, max_time)

    # Fetch all existing Google events from the database within the academic period
    db_events = get_all_google_events(connection, min_time, max_time)

    # Keep track of processed event IDs
    processed_event_ids = set()

    # Process each event from Google Calendar
    for event in google_events:
        processed_event_ids.add(event['google_event_id'])
        if event['google_event_id'] in db_events:
            # Event exists, check for updates
            if update_event(connection, event):
                logger.info(f"Updated event: {event['title']}")
            else:
                update_last_synced(connection, event['google_event_id'])
                logger.info(f"No changes for event: {event['title']}")
        else:
            # New event, insert it
            insert_event(connection, event)

    # Find deleted events within the academic period
    deleted_event_ids = set(db_events.keys()) - processed_event_ids
    if deleted_event_ids:
        mark_events_as_deleted(connection, list(deleted_event_ids))
        logger.info(f"Marked {len(deleted_event_ids)} events as deleted")

    update_last_sync_time(connection, now)
    
    close_db_connection(connection)
    logger.info("Continuous sync completed successfully.")

if __name__ == "__main__":
    perform_continuous_sync()