from datetime import datetime, date
from google_calendar_api import authenticate_and_get_service, list_calendar_events
from db_operations import get_db_connection, close_db_connection, insert_event, update_last_sync_time, get_user_academic_period
from utils import error_handler, setup_logger

logger = setup_logger(__name__)

@error_handler
def perform_initial_import():
    connection = get_db_connection()
    if not connection:
        logger.error("Failed to establish database connection")
        return
    

    service = authenticate_and_get_service()
    
    # Get the user's academic period
    academic_start, academic_end = get_user_academic_period(connection)
    if not academic_start or not academic_end:
        logger.error("Failed to get user's academic period. Aborting initial import.")
        return

    # Convert date objects to datetime objects
    if isinstance(academic_start, date):
        academic_start = datetime.combine(academic_start, datetime.min.time())
    if isinstance(academic_end, date):
        academic_end = datetime.combine(academic_end, datetime.max.time())

    # Set sync window to the entire academic period
    min_time = academic_start
    max_time = academic_end

    events = list_calendar_events(service, min_time, max_time)

    successful_imports = 0
    for event in events:
        try:
            insert_event(connection, event)
            successful_imports += 1
        except Exception as e:
            logger.error(f"Error importing event: {e}")

    now = datetime.utcnow()
    update_last_sync_time(connection, now)
    
    close_db_connection(connection)
    logger.info(f"Initial import completed. Successfully imported {successful_imports} out of {len(events)} events.")

if __name__ == "__main__":
    perform_initial_import()