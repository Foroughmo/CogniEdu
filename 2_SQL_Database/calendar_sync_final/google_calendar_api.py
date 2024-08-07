from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
from config import SERVICE_ACCOUNT_FILE, CALENDAR_ID
import pytz

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_and_get_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('calendar', 'v3', credentials=creds)

def get_local_timezone():
    try:
        return ZoneInfo("America/Chicago")
    except ZoneInfoNotFoundError:
        print("Warning: 'America/Chicago' timezone not found. Using UTC.")
        return pytz.UTC

def list_calendar_events(service, min_time, max_time):
    local_tz = get_local_timezone()
    
    min_time = min_time.astimezone(local_tz)
    max_time = max_time.astimezone(local_tz)

    try:
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=min_time.isoformat(),
            timeMax=max_time.isoformat(),
            singleEvents=True,
            orderBy='updated'
        ).execute()
    except Exception as e:
        print(f"Error fetching events from Google Calendar: {e}")
        return []

    events = events_result.get('items', [])
    processed_events = []

    for event in events:
        start = parse_datetime(event['start'].get('dateTime', event['start'].get('date')))
        end = parse_datetime(event['end'].get('dateTime', event['end'].get('date')))
        
        start = start.replace(tzinfo=local_tz)
        end = end.replace(tzinfo=local_tz)
        
        processed_event = {
            'google_event_id': event['id'],
            'title': event.get('summary', 'No title'),
            'start_time': start,
            'end_time': end,
            'description': event.get('description', ''),
        }
        processed_events.append(processed_event)

    return processed_events

def parse_datetime(dt_string):
    if isinstance(dt_string, str):
        try:
            return datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        except ValueError:
            # Handle all-day events
            return datetime.strptime(dt_string, "%Y-%m-%d")
    return dt_string