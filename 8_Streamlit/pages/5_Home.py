#Home Page 

# Streamlit
import streamlit as st
from streamlit_calendar import calendar
from streamlit_card import card

# Images
from PIL import Image
import base64
from io import BytesIO

# Time/Date
from datetime import datetime, timedelta

# System
from pathlib import Path  # Importing Path

# Import from Utils Folder
import plotly.express as px 
import pandas as pd
from utils.Optimization import optimizer
from utils.SQL import connect_to_database, get_events_between_dates, db_config

# Page Configuration
st.set_page_config(layout="wide")

# Sidebar Navigation
st.markdown(
    """
    <style>
    .main {
        background-color: white;
    }
    .stMarkdown, .stSidebar, .css-145kmo2 p, .css-10trblm p, .css-1cpxqw2 p, .css-9s5bis p, .stTextInput label, .stTextInput div, .stTextInput input, .stTextInput textarea, .stDataFrame label, .stDataFrame div, .stDataFrame input, .stDataFrame textarea, .stHeader, .stSubheader {
        color: black !important;
    }
    .header-text, .subheader-text {
        color: black !important;
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    .sidebar .sidebar-content h2 {
        color: #4B4B4B;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown('<h2>Navigation</h2>', unsafe_allow_html=True)

# Logo
logo_small = Image.open("cogniedulogo.png").resize((200, 200))
buffered = BytesIO()
logo_small.save(buffered, format="PNG")
img_str_small = base64.b64encode(buffered.getvalue()).decode()

# Display the Logo Above the Navigation
st.sidebar.markdown(f'''
    <div style="text-align: center; padding: 20px 0;">
        <img src="data:image/png;base64,{img_str_small}" style="width: 150px;">
    </div>
''', unsafe_allow_html=True)

st.sidebar.page_link('pages/5_Home.py', label='🏠 Home')
st.sidebar.page_link('pages/6_Calendar.py', label='📆 Calendar')
st.sidebar.page_link('pages/7_Chatbot.py', label='🧠 Ed')

# CSS for Custom Styling
st.markdown("""
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        .header-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px 50px;
        }
        .header {
            font-size: 30px;
            font-weight: bold;
            color: #5285F2;
        }
    </style>
""", unsafe_allow_html=True)

custom_css = """
    <style>
        .main-header {
            background-color: #3B47CE;
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .main-header h1 {
            margin: 0;
            color: white;
            text-align: center;
        }
        .stDataFrame {
            border: 1px solid #5285F2;
            border-radius: 10px;
            overflow: hidden;
        }
        .dataframe {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }
        .dataframe th {
            background-color: #5285F2;
            color: white;
            font-weight: bold;
            text-align: left;
            padding: 10px;
        }
        .dataframe td {
            padding: 10px;
            border-top: 1px solid #ddd;
        }
        .dataframe tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #5285F2;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        .stButton>button:hover {
            background-color: #3d6dd0;
        }
        .success-message {
            background-color: #28a745;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .error-message {
            background-color: #dc3545;
            color: white;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .fc-button {
            background-color: #5285F2 !important;
            color: white !important;
            border-color: #5285F2 !important;
        }
        .fc-button:hover {
            background-color: #3d6dd0 !important;
            color: white !important;
            border-color: #3d6dd0 !important;
        }
        .fc-toolbar-title {
            font-size: 2rem;
            color: #5285F2 !important;
        }
        .fc-timegrid-event {
            background-color: #5285F2 !important;
            color: white !important;
            border-color: #5285F2 !important;
        }
        .fc-timegrid-event:hover {
            background-color: #3d6dd0 !important;
            color: white !important;
            border-color: #3d6dd0 !important;
        }
        .fc-event-title {
            font-weight: 700;
            color: white !important;
        }
        .fc-event-time {
            font-style: italic;
            color: #5285F2 !important;
        }
        .fc {
            padding: 1rem;
        }
        .event-box-vertical {
            width: 100%;  /* Take up full width */
            max-width: 300px;  /* Set a max width */
            border: 1px solid #5285F2;
            border-radius: 5px;
            padding: 10px;
            margin: 5px auto;  /* Center the boxes */
            text-align: center;
            vertical-align: top;
            box-sizing: border-box;
            background-color: #ADD8E6;  /* Light blue background color */
        }
        .events-container-vertical {
            display: flex;
            flex-direction: column;
            align-items: center;
            margin-top: 10px; /* Adjusted to shift down */
        }
    </style>
"""

# Main Header
welcome_image_path = "WelcomeNick.png"
welcome_image = Image.open(welcome_image_path).resize((1500, 300))  # Resize the image
buffered = BytesIO()
welcome_image.save(buffered, format="PNG")
img_str_welcome = base64.b64encode(buffered.getvalue()).decode()

st.markdown(f'''
    <div style="text-align: center; padding: 0;">
        <img src="data:image/png;base64,{img_str_welcome}" style="width: 100%;">
    </div>
''', unsafe_allow_html=True)

# Function to Fetch Events from the Database
def get_events_dict(events):
    if events:
        event_dict = {i: {'Title': event[0], 'Start Time': event[1], 'End Time': event[2]} for i, event in enumerate(events)}
        return event_dict
    else:
        return {}

# Function to Display the Combined Calendar and Upcoming Events
def display_dashboard():
    col1, col2 = st.columns([3, 1])

    with col1:
        # Load the Calendar Banner Image
        calendar_banner = Image.open("HomeCalendar.png")
        buffered = BytesIO()
        calendar_banner.save(buffered, format="PNG")
        img_str_calendar = base64.b64encode(buffered.getvalue()).decode()

        # Display the Calendar Banner
        st.markdown(f'''
            <div style="text-align: center; padding: 0px 0;">
                <img src="data:image/png;base64,{img_str_calendar}" style="width: 50%;">
            </div>
        ''', unsafe_allow_html=True)
        
        # Initialize Session State
        if 'combined_events' not in st.session_state:
            st.session_state.combined_events = []

        if 'calendar_generated' not in st.session_state:
            st.session_state.calendar_generated = False

        # Calendar Options
        calendar_options = {
            "initialView": "timeGridDay",  # Day View
            "headerToolbar": {
                "left": "prev,next,today",
                "center": "title",
                "right": "timeGridDay"  # Only Day View Option
            },
            "slotMinTime": "06:00:00",
            "slotMaxTime": "22:00:00",
            "editable": False,
            "selectable": True,
            "selectMirror": True,
            "height": "auto",
            "nowIndicator": True  # Show the Current Time
        }

        # Generate the Combined Schedule Once
        if not st.session_state.calendar_generated:
            with st.spinner('Generating schedule...'):
                # Get optimizer schedule
                optimizer_schedule = optimizer()

                if not optimizer_schedule:
                    st.error("Failed to generate schedule. Please check the optimizer function.")
                    return

                # Connect to Database and Fetch Current Events
                db_connection = connect_to_database(db_config)
                current_events_sql = {}
                if db_connection is not None:
                    events = get_events_between_dates(db_connection, str(datetime.today().date()), str((datetime.today() + timedelta(days=7)).date()))
                    current_events_sql = get_events_dict(events)
                    db_connection.close()

                # Combine Optimizer Schedule and Current Events
                combined_events = []

                # Process Optimizer Schedule
                study_color = "#F2A799"  # Light Blue for Optimized Study Sessions
                class_color = "#004AAD"  # Navy Blue for Class Events
                other_event_color = "#5271FF"  # Pink for Other Non-Study and Non-Class Events

                for day, sessions in optimizer_schedule.items():
                    date = datetime.strptime(day.split('(')[1].split(')')[0], '%Y-%m-%d')
                    for subject, start_time, end_time in sessions:
                        start_time = float(start_time)  
                        end_time = float(end_time)  
                        start = date + timedelta(hours=start_time)
                        end = date + timedelta(hours=end_time)
                        combined_events.append({
                            "title": f"{subject} Study",
                            "start": start.isoformat(),
                            "end": end.isoformat(),
                            "color": study_color
                        })

                # Process Current Events from SQL
                for key, event in current_events_sql.items():
                    try:
                        start_time = event["Start Time"]
                        end_time = event["End Time"]

                        if not isinstance(start_time, datetime):
                            start_time = datetime.fromisoformat(start_time)
                        if not isinstance(end_time, datetime):
                            end_time = datetime.fromisoformat(end_time)

                        if event["Title"].startswith("Class:"):
                            event_color = class_color
                        elif "Study" in event["Title"]:
                            event_color = study_color
                        else:
                            event_color = other_event_color

                        combined_events.append({
                            "title": event["Title"],
                            "start": start_time.isoformat(),
                            "end": end_time.isoformat(),
                            "backgroundColor": event_color,
                            "borderColor": event_color
                        })
                    except Exception as e:
                        st.error(f"Error processing event {key}: {str(e)}")

                st.session_state.combined_events = combined_events
                st.session_state.calendar_generated = True

                combined_events_df = pd.DataFrame(combined_events)

                # Get the Directory of the Current Script
                script_dir = Path(__file__).resolve().parent

                # Get the Project Root Directory
                project_root = script_dir.parent

        # Create and Display the Calendar
        if st.session_state.calendar_generated:
            cal = calendar(events=st.session_state.combined_events, options=calendar_options, custom_css=custom_css)

    with col2:
        css = """
            <style>
            .title {
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .icon {
                font-size: 40px;
            }

            h1 {
                font-size: 40px;
                color: #3366FF;
                margin: 0;
            }

            .events-container-vertical {
                display: flex;
                flex-direction: column;
                align-items: center;
                margin-top: 10px;  /* Adjusted to shift down */
            }
            .event-box-vertical {
                background: #E0E6FF; /* Light blue background color */
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
                width: 100%; /* Take up full width */
                max-width: 300px;  /* Set a max width */
                text-align: center;
                border: 1px solid #5285F2; /* Optional: to add a border */
            }
            </style>
        """

        # Apply CSS
        st.markdown(css, unsafe_allow_html=True)

        # Load the Upcoming Events Banner
        upcoming_events_banner = Image.open("HomeUpcoming.png").resize((1500, 300))
        buffered = BytesIO()
        upcoming_events_banner.save(buffered, format="PNG")
        img_str_upcoming_events = base64.b64encode(buffered.getvalue()).decode()

        # Display the Upcoming Events Banner
        st.markdown(f'''
            <div style="text-align: center; padding: 0;">
                <img src="data:image/png;base64,{img_str_upcoming_events}" style="width: 90%;">
            </div>
        ''', unsafe_allow_html=True)

        if 'combined_events' in st.session_state:
            upcoming_events = sorted(
                st.session_state.combined_events, 
                key=lambda x: datetime.fromisoformat(x['start'])
            )

            upcoming_events = [
                event for event in upcoming_events 
                if datetime.fromisoformat(event['start']) > datetime.now()
            ][:3]

            if upcoming_events:
                st.markdown('<div class="events-container-vertical">', unsafe_allow_html=True)
                for event in upcoming_events:
                    start_dt = datetime.fromisoformat(event['start'])
                    end_dt = datetime.fromisoformat(event['end'])
                    day_name = start_dt.strftime('%A')
                    start_time = start_dt.strftime('%I:%M %p').lstrip('0')
                    end_time = end_dt.strftime('%I:%M %p').lstrip('0')
                    now = datetime.now()
                    time_left = start_dt - now
                    days_left = time_left.days
                    if days_left < 0:
                        countdown_text = "(Now)"
                    elif days_left == 0:
                        countdown_text = "Happening Tomorrow"
                    elif days_left == 1:
                        countdown_text = "Due Tomorrow"
                    else:
                        countdown_text = f"({days_left} days left)"
                    st.markdown(f"""
                        <div class="event-box-vertical">
                            <strong>{day_name}</strong><br>
                            {event['title']}<br>
                            {start_time} - {end_time}<br>
                            <span style="color: #FF0000;">{countdown_text}</span>
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown("No upcoming events found.")

        # Load the Chat with Ed Banner Image
        chat_with_ed_banner = Image.open("HomeChat.png").resize((1500, 300))
        buffered = BytesIO()
        chat_with_ed_banner.save(buffered, format="PNG")
        img_str_chat_with_ed = base64.b64encode(buffered.getvalue()).decode()

        # Display the Chat with Ed Banner Image
        st.markdown(f'''
            <div style="text-align: center; padding: 20px 0;">
                <img src="data:image/png;base64,{img_str_chat_with_ed}" style="width: 90%;">
            </div>
        ''', unsafe_allow_html=True)
        
        # Avatar
        avatar_path = "Ed_Avatar.png"
        avatar_image = Image.open(avatar_path)
        buffered = BytesIO()
        avatar_image.save(buffered, format="PNG")
        img_str_avatar = base64.b64encode(buffered.getvalue()).decode()

        st.markdown(f'''
            <div style="text-align: center; padding: 10px; margin-bottom: 25px;">
                <img src="data:image/png;base64,{img_str_avatar}" style="width: 150px; height:150px">
            </div>
        ''', unsafe_allow_html=True)
        
        st.markdown("""
            <div style="text-align: center;">
                <p>Ask Ed about your course documents and calendar events!</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("Click Here to Begin Chatting with Ed"):
            st.switch_page("pages/7_Chatbot.py")

# Run the Streamlit App
if __name__ == "__main__":
    st.markdown(custom_css, unsafe_allow_html=True)
    display_dashboard()

