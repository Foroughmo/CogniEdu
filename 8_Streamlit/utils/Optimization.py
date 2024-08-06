#System

import os
import json
import ast
import re

#import calendar
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timedelta

# Vertex AI
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession
import vertexai.preview.generative_models as generative_models


def load_user_preferences():
    return pd.read_pickle('user_preferences.pkl')


# Get the path to the directory for Optimizer.py script
base_dir = Path(__file__).resolve().parent

# Construct the path to the Time_Completion.pkl file in the utils folder
pickle_path = base_dir / 'Time_Completion.pkl'

# Load the DataFrame from the pickle file
try:
    df = pd.read_pickle(pickle_path)
    print("Successfully loaded Time_Completion.pkl")
    print(df.head()) 
except FileNotFoundError:
    print(f"Error: Time_Completion.pkl not found at {pickle_path}")
except Exception as e:
    print(f"Error loading Time_Completion.pkl: {e}")



def authenticate_and_initialize_services():
    load_dotenv()
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/classroom.courses.readonly',
        'https://www.googleapis.com/auth/classroom.coursework.me.readonly'
    ]

    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print("Service account file does not exist.")
        return None, None

    try:
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        calendar_service = build('calendar', 'v3', credentials=creds)
        classroom_service = build('classroom', 'v1', credentials=creds)
        
        return calendar_service, classroom_service
    
    except Exception as e:
        print(f"An error occurred during authentication: {str(e)}")
        return None, None

# Usage
calendar_service, classroom_service = authenticate_and_initialize_services()
    
    
    
def get_free_time_slots(service, calendar_id, min_time, max_time):
    if isinstance(min_time, str):
        min_time = datetime.fromisoformat(min_time)
    if isinstance(max_time, str):
        max_time = datetime.fromisoformat(max_time)

    local_tz = ZoneInfo("America/Chicago")
    min_time = min_time.replace(tzinfo=local_tz)
    max_time = max_time.replace(tzinfo=local_tz)

    events_result = service.events().list(calendarId=calendar_id,
                                          timeMin=min_time.isoformat(),
                                          timeMax=max_time.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    
    free_slots = [(min_time, max_time)]

    for event in events:
        start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
        
        # Set the timezone 
        start = start.replace(tzinfo=local_tz)
        end = end.replace(tzinfo=local_tz)
        
        # Adjust for potential DST differences
        if start.dst() != min_time.dst():
            start += timedelta(hours=1)
        if end.dst() != min_time.dst():
            end += timedelta(hours=1)

        new_free_slots = []
        for free_start, free_end in free_slots:
            if end <= free_start or start >= free_end:
                new_free_slots.append((free_start, free_end))
            else:
                if start > free_start:
                    new_free_slots.append((free_start, start))
                if end < free_end:
                    new_free_slots.append((end, free_end))
        free_slots = new_free_slots

    return free_slots

chicago_tz = ZoneInfo("America/Chicago")
current_time = datetime.now(chicago_tz)

# Set the start time to the current time, rounded to the nearest minute
min_time = current_time.replace(second=0, microsecond=0)

# Set the end time to 7 days from the current time
max_time = min_time + timedelta(days=7)


# Get free time slots
free_slots = get_free_time_slots(calendar_service, 'nickramen.uchicago@gmail.com', min_time, max_time)
#print(free_slots)



def list_calendar_events(service, calendar_id, min_time, max_time):
    """
    List events from a Google Calendar within a specified time range.

    :param service: Authenticated Google Calendar API service object
    :param calendar_id: ID of the calendar to fetch events from
    :param min_time: Start of the time range (datetime or ISO format string)
    :param max_time: End of the time range (datetime or ISO format string)
    :return: List of event dictionaries
    """
    # Convert string times to datetime objects if necessary
    if isinstance(min_time, str):
        min_time = datetime.fromisoformat(min_time)
    if isinstance(max_time, str):
        max_time = datetime.fromisoformat(max_time)

    # Set timezone
    local_tz = ZoneInfo("America/Chicago")
    min_time = min_time.replace(tzinfo=local_tz)
    max_time = max_time.replace(tzinfo=local_tz)

    # Fetch events from the calendar
    events_result = service.events().list(calendarId=calendar_id,
                                          timeMin=min_time.isoformat(),
                                          timeMax=max_time.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    # Process and return the events
    processed_events = []
    for event in events:
        start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')))
        end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')))
        
        # Set timezone and adjust for DST
        start = start.replace(tzinfo=local_tz)
        end = end.replace(tzinfo=local_tz)
        
        processed_events.append({
            'summary': event.get('summary', 'No title'),
            'start': start,
            'end': end,
            'id': event['id']        })

    return processed_events

# Example usage:

chicago_tz = ZoneInfo("America/Chicago")
current_time = datetime.now(chicago_tz)
min_time = current_time.replace(second=0, microsecond=0)
max_time = min_time + timedelta(days=7)

events = list_calendar_events(calendar_service, 'nickramen.uchicago@gmail.com', min_time, max_time)


# for start, end in free_slots:
#     print(start)
    
    
def parse_time_slots(free_slots):
    formatted_slots = {}
    
    for start, end in free_slots:
        current = start
        while current < end:
            day = current.strftime('%A')
            day_end = datetime.combine(current.date(), datetime.max.time()).replace(tzinfo=current.tzinfo)
            slot_end = min(end, day_end)
            
            # Round start_hour to nearest quarter hour
            start_hour = round((current.hour + current.minute / 60) * 4) / 4
            
            # Calculate duration
            duration = (slot_end - current).total_seconds() / 3600  # Duration in hours
            
            # Round duration to nearest quarter hour
            duration = round(duration * 4) / 4
            
            formatted_slots.setdefault(day, []).append((start_hour, duration))
            
            if slot_end == end:
                break
            current = slot_end.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    # Adjust the first day if it doesn't start at midnight
    if formatted_slots:
        first_day = list(formatted_slots.keys())[0]
        first_slot = formatted_slots[first_day][0]
        if first_slot[0] > 0:
            formatted_slots[first_day] = [(first_slot[0], first_slot[1])]
    
    return formatted_slots

weekly_time_slots = parse_time_slots(free_slots)

weekly_time_slots

def parse_study_plan(content):
    # Remove any leading/trailing whitespace and the ```python and ``` if present
    content = content.strip().lstrip('```python').rstrip('```').strip()
    try:
        # Attempt to directly evaluate the string as a Python literal
        return ast.literal_eval(content)
    except:
        return None
    
    
    
def parse_deadline(deadline_str, start_date):
    """
    Parse various deadline formats and return a datetime object.
    
    Supported formats:
    - "in X days"
    - "YYYY-MM-DD"
    - "Day at HH:MM AM/PM"
    - ISO 8601 format
    """
    # Check for "in X days" format
    in_days_match = re.match(r'in (\d+) days?', deadline_str, re.IGNORECASE)
    if in_days_match:
        days = int(in_days_match.group(1))
        return start_date + timedelta(days=days)
    
    # Check for YYYY-MM-DD format
    try:
        return datetime.strptime(deadline_str, "%Y-%m-%d")
    except ValueError:
        pass
    
    # Check for "Day at HH:MM AM/PM" format
    day_time_match = re.match(r'(\w+) at (\d{1,2}):(\d{2}) (AM|PM)', deadline_str, re.IGNORECASE)
    if day_time_match:
        day, hour, minute, ampm = day_time_match.groups()
        hour = int(hour)
        if ampm.upper() == 'PM' and hour != 12:
            hour += 12
        elif ampm.upper() == 'AM' and hour == 12:
            hour = 0
        target_date = start_date + timedelta(days=(list(calendar.day_name).index(day) - start_date.weekday() + 7) % 7)
        return target_date.replace(hour=hour, minute=int(minute), second=0, microsecond=0)
    
    # Check for ISO 8601 format
    try:
        return datetime.fromisoformat(deadline_str)
    except ValueError:
        pass
    
    raise ValueError(f"Unsupported deadline format: {deadline_str}")

    
def get_enhanced_deadline_info(deadline_date, start_date):
    """Convert a deadline date to a more informative format."""
    days_until = (deadline_date - start_date).days
    weekday = deadline_date.strftime("%A")
    date_str = deadline_date.strftime("%Y-%m-%d")
    time_str = deadline_date.strftime("%I:%M %p")

    if days_until < 0:
        return f"Past due ({abs(days_until)} days ago) - {weekday}, {date_str} at {time_str}"
    elif days_until == 0:
        return f"Today ({weekday}) at {time_str}"
    elif days_until == 1:
        return f"Tomorrow ({weekday}) at {time_str}"
    elif days_until < 7:
        return f"In {days_until} days ({weekday}, {date_str}) at {time_str}"
    else:
        return f"In {days_until} days - {weekday}, {date_str} at {time_str}"

    
def prepare_enhanced_deadlines(deadlines, start_date):
    """Prepare deadlines with enhanced information."""
    enhanced_deadlines = {}
    for subject, deadline in deadlines.items():
        deadline_date = parse_deadline(deadline, start_date)
        enhanced_deadlines[subject] = get_enhanced_deadline_info(deadline_date, start_date)
    return enhanced_deadlines


# Example usage:
#start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
# deadlines = {
#     "Math": "in 4 days",
#     "English": "in 5 days",
#     "Biology": "in 7 days",
#     "Chemistry": "in 3 days"
# }

# enhanced_deadlines = prepare_enhanced_deadlines(deadlines, start_date)
# print(enhanced_deadlines)


def multiturn_generate_content(assignments, enhanced_deadlines, priorities, start_date):
    vertexai.init(project="adsp-capstone-convocrafters", location="us-central1")
    model = GenerativeModel("gemini-1.5-pro-preview-0514")
    
    weekdays = [start_date + timedelta(days=i) for i in range(7)]
    weekdays_str = ", ".join([day.strftime("%A (%Y-%m-%d)") for day in weekdays])
    
    prompt = f"""
    Create a balanced study plan based on these assignments, deadlines, and priorities:

    Assignments and Durations:
    {assignments}

    Enhanced Deadlines:
    {enhanced_deadlines}

    Priorities (listed from highest to lowest):
    {priorities}

    Available Days (in order):
    {weekdays_str}

    Follow these constraints and guidelines:
    1. Use the provided durations exactly. The total study time for each subject must match the given duration.
    2. Spread the assignments across the available days based on deadlines and priorities.
    3. Prioritize subjects with imminent or past due deadlines. Allocate more time to these subjects earlier in the week.
    4. Only use the days provided in the Available Days list.
    5. For past due assignments, allocate time as soon as possible to catch up.
    6. Try to balance the workload across the week, avoiding excessive studying on any single day if possible.
    7. Consider both the priority order and deadlines when scheduling. Subjects listed earlier in the Priorities list are generally more important to the student.
    8. If a subject has less than 1 hour total duration, you may schedule it as a single session.
    9. Do not schedule any 0-hour study sessions. If a subject is included for a day, it must have a duration greater than 0.

    Output only the study plan as a Python dictionary with each available day as a key, and the value as a list of tuples.
    Each tuple should contain (subject, duration in hours, priority score).
    The priority score should be a number from 1 to 5, where 5 is the highest priority. This score should be based on a combination of:
    - The subject's position in the Priorities list
    - The urgency of the deadline
    - Any past due status

    Example format:
    {{
        {weekdays[0].strftime('%A (%Y-%m-%d)')}: [("Math Assignment 1", 2, 5), ("English Assignment 1", 1.5, 4)], 
        {weekdays[1].strftime('%A (%Y-%m-%d)')}: [("Biology Assignment 1", 2, 3), ("Math Assignment 1", 1, 5)]
    }}

    Ensure that the study plan is realistic, takes into account the urgency of deadlines, and never includes 0-hour study sessions.
    Subjects with higher priority scores should generally be given more favorable time slots or more frequent sessions.
    Do not include any explanations or additional code. Only output the study plan dictionary.
    """

    try:
        response = model.generate_content(prompt)
        content = response.text
        print("Raw response:", content)  # Debug print
        study_plan = parse_study_plan(content)
        if study_plan is None:
            raise ValueError("Unable to parse a valid study plan dictionary from the response")
        
        # Verify the study plan
        total_hours = {subject: sum(duration for day in study_plan.values() for s, duration, _ in day if s == subject)
                       for subject in assignments}
        
        if total_hours != assignments:
            raise ValueError(f"Study plan does not match the given estimates. Expected: {assignments}, Got: {total_hours}")
        
        # Check for 0-hour sessions
        for day, sessions in study_plan.items():
            if any(duration == 0 for _, duration, _ in sessions):
                raise ValueError(f"Study plan contains 0-hour sessions on {day}")
        
        return study_plan
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
    

#assignments = {"Intro to Art Assignment 1": df["Time_Completion"][0], "Marketing Analytics Assignment 1": df["Time_Completion"][3], "Statistical Analysis Assignment 1": df["Time_Completion"][7]}
#priorities = ["Statistical Analysis", "Marketing Analytics", "Intro to Art"]
#start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

#weekly_study_plan = multiturn_generate_content(assignments, enhanced_deadlines, priorities, start_date)

#weekly_study_plan

# for day, sessions in weekly_study_plan.items():
#         # Extract just the day name from the full date string
#         day_name = day.split()[0]
#         print(day_name)
        
        
def fit_study_times_into_timed_slots(weekly_plan, weekly_slots, start_hour, end_hour, buffer=0.5, morning_person=True):
    weekly_schedule = {}
    
    for day, sessions in weekly_plan.items():
        day_name = day.split()[0]
        
        sessions.sort(key=lambda x: x[2], reverse=True)
        daily_schedule = []
        time_slots = weekly_slots.get(day_name, [])
        
        # Apply buffer to both start and end of each slot
        adjusted_slots = []
        for start_time, duration in time_slots:
            slot_start = max(start_time + buffer, start_hour)
            slot_end = min(start_time + duration - buffer, end_hour)
            if slot_end > slot_start:
                adjusted_slots.append((slot_start, slot_end))
        
        adjusted_slots.sort(key=lambda x: x[0], reverse=not morning_person)
        
        for subject, duration, priority in sessions:
            for i, (slot_start, slot_end) in enumerate(adjusted_slots):
                if slot_end - slot_start >= buffer:  # Ensure there's enough time for at least the buffer
                    study_start = slot_start + buffer if daily_schedule else slot_start
                    study_time = min(duration, slot_end - study_start)
                    study_end = study_start + study_time
                    
                    if study_time > 0:
                        daily_schedule.append((subject, study_start, study_end))
                        duration -= study_time
                        adjusted_slots[i] = (study_end, slot_end)  # Update the remaining slot time
                        
                        if duration == 0:
                            break
        
        if daily_schedule:
            weekly_schedule[day] = daily_schedule
    
    return weekly_schedule


# scheduled_week = fit_study_times_into_timed_slots(
#     weekly_study_plan, weekly_time_slots, start_hour=9, end_hour=20, buffer=0.50, morning_person=True)

# scheduled_week


# Main - Orchestrated execution

def optimizer():

    # Load user preferences
    user_preferences = load_user_preferences()
    print(user_preferences.head())
    time_estimation = df
    
    # Extract preferences
    start_hour = user_preferences['start_time'].iloc[0]
    end_hour = user_preferences['end_time'].iloc[0]
    morning_person = user_preferences['morning_person'].iloc[0] == 'True'
    #break_duration = user_preferences['break_duration'].iloc[0]  # in hours
    courses = user_preferences['courses'].iloc[0]
    semester_start = user_preferences['semester_start'].iloc[0]
    semester_end = user_preferences['semester_end'].iloc[0]
    
    buffer = user_preferences['break_duration'].iloc[0]  #  in hours
    print(buffer)
    
    # Define the time range for the current week
    chicago_tz = ZoneInfo("America/Chicago")
    current_time = datetime.now(chicago_tz).replace(second=0, microsecond=0)
    min_time = current_time
    max_time = min_time + timedelta(days=7)

    # Fetch free time slots
    calendar_id = 'nickramen.uchicago@gmail.com'  
    free_slots = get_free_time_slots(calendar_service, calendar_id, min_time, max_time)
    print("Free Time Slots:", free_slots)

    # Process free time slots into a weekly schedule
    weekly_time_slots = parse_time_slots(free_slots)
    print("Weekly Time Slots:", weekly_time_slots)

    # Define study assignments and priorities
    assignments = {"Intro to Art Assignment 1": df["Time_Completion"][0], "Marketing Analytics Assignment 1": df["Time_Completion"][3], "Statistical Analysis Assignment 1": df["Time_Completion"][7]}
    priorities = ["Statistical Analysis", "Marketing Analytics", "Intro to Art"]

    # Generate enhanced deadline information
    deadlines = {
        "Intro to Art Assignment 1": "in 4 days",
        "Marketing Analytics Assignment 1": "in 5 days",
        "Statistical Analysis Assignment 1": "in 5 days"
    }
    enhanced_deadlines = prepare_enhanced_deadlines(deadlines, current_time)
    print("Enhanced Deadlines:", enhanced_deadlines)

    # Generate weekly study plan using an AI-driven content generator
    weekly_study_plan = multiturn_generate_content(assignments, enhanced_deadlines, priorities, current_time)
    print("Generated Weekly Study Plan:", weekly_study_plan)

    # Fit the study times into the timed slots based on the generated plan
    scheduled_week = fit_study_times_into_timed_slots(weekly_study_plan, weekly_time_slots, start_hour, end_hour, buffer, morning_person)
    print("Scheduled Week:", scheduled_week)

    return scheduled_week

if __name__ == '__main__':
    schedule = optimizer()
    print("Scheduled Week:", schedule)


    
 #    optimizer ouptut format
 #    {'Thursday (2024-06-27)': [('Math', 13.0, 15.0), ('Chemistry', 15.0, 17.0)],
 # 'Friday (2024-06-28)': [('Math', 11.0, 13.0), ('Chemistry', 13.0, 15.0)],
 # 'Saturday (2024-06-29)': [('Math', 9, 11), ('English', 11, 13)],
 # 'Sunday (2024-06-30)': [('Math', 9, 11), ('English', 11, 12)],
 # 'Monday (2024-07-01)': [('English', 11.0, 13.0)],
 # 'Tuesday (2024-07-02)': [('Biology', 9, 9.5), ('Biology', 12.0, 13.5)]}

