# Calendar

# Libraries
import streamlit as st
from streamlit_calendar import calendar

from PIL import Image
from io import BytesIO

import os
import base64
import pickle
import pandas as pd
from pathlib import Path
import datetime
from datetime import datetime, timedelta

from utils.Optimization import optimizer
from utils.SQL import connect_to_database, get_events_between_dates, db_config

# Email Notification

from dotenv import load_dotenv
from email.message import EmailMessage
import ssl
import smtplib


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
logo_path = "cogniedulogo.png"
logo_small = Image.open(logo_path).resize((100, 100))
buffered = BytesIO()
logo_small.save(buffered, format="PNG")
img_str_small = base64.b64encode(buffered.getvalue()).decode()

# Display the Logo Above the Navigation
st.sidebar.markdown(f'''
    <div style="text-align: center; padding: 20px 0;">
        <img src="data:image/png;base64,{img_str_small}" style="width: 150px;">
    </div>
''', unsafe_allow_html=True)

# Sidebar Navigation
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

# Define the CSS for the Custom Styling
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
        .fc-button-primary {
            background-color: #5285F2; /* Changed from #3B47CE to a lighter blue #5285F2 */
            border-color: #5285F2;
        }
        .fc-button-primary:hover {
            background-color: #3d6dd0; /* Hover state in dark blue */
            border-color: #3d6dd0;
        }
        .fc-button-primary:focus {
            background-color: #5285F2;
            border-color: #5285F2;
            box-shadow: none;
        }
        .fc-button-primary:active {
            background-color: #5285F2;
            border-color: #5285F2;
        }
        .fc-button-primary.fc-button-active {
            background-color: #3d6dd0;
            border-color: #3d6dd0;
        }
        .fc-today-button {
            background-color: #A3B9FF; /* Lighter blue for the "Today" button */
            border-color: #A3B9FF;
        }
        .fc-today-button:hover {
            background-color: #809aff;
            border-color: #809aff;
        }
        .fc-today-button:focus {
            background-color: #A3B9FF;
            border_color: #A3B9FF;
            box_shadow: none;
        }
        .fc-today-button:active {
            background-color: #A3B9FF;
            border-color: #A3B9FF;
        }
        .fc-today-button.fc-button-active {
            background-color: #809aff;
            border_color: #809aff;
        }
    </style>
"""

# Calendar Banner
calendar_image_path = "CalendarTitle.png"
calendar_image = Image.open(calendar_image_path)
buffered = BytesIO()
calendar_image.save(buffered, format="PNG")
img_str_calendar = base64.b64encode(buffered.getvalue()).decode()

st.markdown(f'''
    <div style="text-align: center;">
        <img src="data:image/png;base64,{img_str_calendar}" style="width: 100%;">
    </div>
''', unsafe_allow_html=True)

# Function to Fetch Events from the Database
def get_events_dict(events):
    if events:
        event_dict = {i: {'Title': event[0], 'Start Time': event[1], 'End Time': event[2]} for i, event in enumerate(events)}
        return event_dict
    else:
        return {}

# Function to Display the Combined Calendar
def display_combined_calendar():
    
    # Custom CSS for Vertical Events Display
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
                background-color: #3d6dd0;
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
        </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Initialize Session State
    if 'combined_events' not in st.session_state:
        st.session_state.combined_events = []

    if 'calendar_generated' not in st.session_state:
        st.session_state.calendar_generated = False

    # Calendar Options
    calendar_options = {
        "initialView": "timeGridWeek",
        "headerToolbar": {
            "left": "prev,next,today",
            "center": "title",
            "right": "timeGridDay,timeGridWeek,dayGridMonth"
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
            # Get Optimizer Schedule
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
            study_color = "#F2A799"  # Light blue for optimized study sessions
            class_color = "#004AAD"  # Navy blue for class events
            other_event_color = "#5271FF"  # Pink for other non-study and non-class events

            for day, sessions in optimizer_schedule.items():
                date = datetime.strptime(day.split('(')[1].split(')')[0], '%Y-%m-%d')
                for subject, start_time, end_time in sessions:
                    start_time = float(start_time)  # Convert numpy.int64 to Python float
                    end_time = float(end_time)  # Convert numpy.int64 to Python float
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
                        "color": event_color
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

            # Define the Path for the user_credentials.pkl File
            combined_events_path = project_root / 'combined_events.pkl'   

            # Save the DataFrame to a Pickle File
            combined_events_df.to_pickle(combined_events_path)
            
            # Load Combined Events from Pickle File
            directory = '/home/jupyter/2. Capstone 2/0. Capstone2_App/'
            file_path = os.path.join(directory, 'combined_events.pkl')

            # Check if File Exists
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    combined_events = pickle.load(file)
                    
            # Function to Format Dates and Times
            def format_datetime(datetime_str):
                return pd.to_datetime(datetime_str).strftime('%B %d, %Y %I:%M %p')

            # Extract Date from Start Datetime
            combined_events['date'] = pd.to_datetime(combined_events['start']).dt.date

            # Group by Date and Format
            grouped_events = combined_events.groupby('date')

            formatted_info = []
            for date, group in grouped_events:
                formatted_events = []
                for index, row in group.iterrows():
                    title = row['title']
                    start_datetime = format_datetime(row['start'])
                    end_datetime = format_datetime(row['end'])
                    formatted_events.append(f"    {index + 1}. {title} \n     ({start_datetime} - {end_datetime})")
                formatted_info.append(f"<b>{date.strftime('%B %d, %Y')}:</b>\n" + "\n".join(formatted_events))

            final_output = "\n\n".join(formatted_info)    

            formatted_event_info = final_output
            
            # Email Parameters
            load_dotenv()
            email_sender = 'convocrafters.uchicago@gmail.com'
            email_password = os.getenv('email_password')
            email_receiver = 'nickramen.uchicago@gmail.com'

            # Date for Subject Line
            current_date = datetime.now().strftime("%m/%d/%Y")

            # Load Combined Events from Pickle File
            directory = '/home/jupyter/2. Capstone 2/0. Capstone2_App/'
            file_path = os.path.join(directory, 'combined_events.pkl')

            # Check if the File Exists
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    combined_events = pickle.load(file)

                # Email Content
                subject = f"Ed's Schedule Digest as of {current_date}"
                body = f"""
                <html>
                <body>
                <p>Hello, Nick!</p>
                <p>Here are this week's events from your calendar:</p>
                <pre>{formatted_event_info}</pre>
                <p>Good luck with your studying!</p>
                <p>Best,</p>
                <p>Ed</p>
                </body>
                </html>
                """

                # Create Email Message
                email = EmailMessage()
                email['From'] = email_sender
                email['To'] = email_receiver
                email['Subject'] = subject
                email.set_content(body, subtype='html')

                # Create SSL Context
                context = ssl.create_default_context()

                # Send Email Using SMTP_SSL
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                    smtp.login(email_sender, email_password)
                    smtp.sendmail(email_sender, email_receiver, email.as_string())
            else:
                print(f"File Not Found: {file_path}")

    # Create and Display the Calendar
    if st.session_state.calendar_generated:
        cal = calendar(events=st.session_state.combined_events, options=calendar_options, custom_css=custom_css)
        
# Run the Streamlit App
if __name__ == "__main__":
    st.markdown(custom_css, unsafe_allow_html=True)
    display_combined_calendar()
