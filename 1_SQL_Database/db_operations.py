import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG, USER_ID
from utils import setup_logger
from datetime import datetime

logger = setup_logger(__name__)

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            db_info = connection.get_server_info()
            logger.info(f"Connected to MySQL Server version {db_info}")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            logger.info(f"You're connected to database: {db_name}")
            cursor.close()
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL database: {e}")
        return None

def close_db_connection(connection):
    if connection.is_connected():
        connection.close()

def get_user_academic_period(connection):
    query = "SELECT academic_period_start, academic_period_end FROM Users WHERE id = %s"
    cursor = connection.cursor()
    try:
        cursor.execute(query, (USER_ID,))
        result = cursor.fetchone()
        if result:
            return result[0], result[1]
        else:
            logger.error(f"No academic period found for user ID {USER_ID}")
            return None, None
    except Error as e:
        logger.error(f"Error getting user academic period: {e}")
        return None, None
    finally:
        cursor.close()

def get_all_google_events(connection, min_time, max_time):
    query = """
    SELECT google_event_id, title, start_time, end_time, description
    FROM Events
    WHERE user_id = %s 
    AND google_event_id IS NOT NULL
    AND (
        (start_time BETWEEN %s AND %s)
        OR (end_time BETWEEN %s AND %s)
        OR (start_time <= %s AND end_time >= %s)
    )
    """
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(query, (USER_ID, min_time, max_time, min_time, max_time, min_time, max_time))
        return {row['google_event_id']: row for row in cursor.fetchall()}
    except Error as e:
        logger.error(f"Error fetching Google events: {e}")
        return {}
    finally:
        cursor.close()

def update_event(connection, event):
    query = """
    UPDATE Events
    SET title = %s, start_time = %s, end_time = %s, description = %s, last_synced = %s, is_deleted = FALSE
    WHERE google_event_id = %s AND user_id = %s
        AND (title != %s OR start_time != %s OR end_time != %s OR description != %s OR is_deleted = TRUE)
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, (
            event['title'], event['start_time'], event['end_time'], event.get('description', ''),
            datetime.utcnow(), event['google_event_id'], USER_ID,
            event['title'], event['start_time'], event['end_time'], event.get('description', '')
        ))
        connection.commit()
        if cursor.rowcount > 0:
            logger.info(f"Event updated: {event['title']}")
        return cursor.rowcount > 0
    except Error as e:
        logger.error(f"Error updating event: {e}")
        return False
    finally:
        cursor.close()

def update_last_synced(connection, google_event_id):
    query = """
    UPDATE Events
    SET last_synced = %s
    WHERE google_event_id = %s AND user_id = %s
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, (datetime.utcnow(), google_event_id, USER_ID))
        connection.commit()
        logger.info(f"Last synced updated for event: {google_event_id}")
    except Error as e:
        logger.error(f"Error updating last_synced: {e}")
    finally:
        cursor.close()

def insert_event(connection, event):
    query = """
    INSERT INTO Events (user_id, google_event_id, title, start_time, end_time, description, last_synced)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, (
            USER_ID, event['google_event_id'], event['title'], 
            event['start_time'], event['end_time'], event.get('description', ''),
            datetime.utcnow()
        ))
        connection.commit()
        logger.info(f"New event inserted: {event['title']}")
    except Error as e:
        logger.error(f"Error inserting event: {e}")
    finally:
        cursor.close()

def mark_events_as_deleted(connection, google_event_ids):
    if not google_event_ids:
        return  # No events to mark as deleted

    placeholders = ', '.join(['%s'] * len(google_event_ids))
    query = f"""
    UPDATE Events
    SET is_deleted = TRUE, last_synced = %s
    WHERE google_event_id IN ({placeholders}) AND user_id = %s
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, 
                       [datetime.utcnow()] + google_event_ids + [USER_ID])
        connection.commit()
        logger.info(f"Marked {cursor.rowcount} events as deleted")
    except Error as e:
        logger.error(f"Error marking events as deleted: {e}")
        connection.rollback()
    finally:
        cursor.close()

def get_last_sync_time(connection):
    query = "SELECT value FROM AppState WHERE `key` = 'last_sync_time'"
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        logger.error(f"Error getting last sync time: {e}")
        return None
    finally:
        cursor.close()

def update_last_sync_time(connection, sync_time):
    query = """
    INSERT INTO AppState (`key`, value)
    VALUES ('last_sync_time', %s)
    ON DUPLICATE KEY UPDATE
    value = VALUES(value)
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, (sync_time.isoformat(),))
        connection.commit()
        logger.info(f"Last sync time updated: {sync_time}")
    except Error as e:
        logger.error(f"Error updating last sync time: {e}")
    finally:
        cursor.close()