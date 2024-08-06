# SQL.py

import streamlit as st
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from .env
db_config = {
    'host': os.getenv("DB_HOST"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'database': os.getenv("DB_DATABASE")
}

def connect_to_database(config):
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as err:
        st.error(f"Failed to connect to the database: {err}")
        return None

def get_events_between_dates(connection, start_date_str, end_date_str):
    if connection is None:
        return []

    cursor = connection.cursor()
    try:
        # Convert dates from strings to datetime objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        query = """
        SELECT title, start_time, end_time
        FROM Events
        WHERE DATE(start_time) BETWEEN %s AND %s
        """
        cursor.execute(query, (start_date, end_date))
        return cursor.fetchall()
    except mysql.connector.Error as err:
        st.error(f"Error retrieving events: {err}")
        return []
    finally:
        cursor.close()

def display_events(events):
    if events:
        for title, start, end in events:
            st.write(f"Title: {title}, Start Time: {start}, End Time: {end}")
    else:
        st.write("No events found within the specified date range.")

        
# Layout for display SQL 
def main():
    st.title('Database Event Viewer')
    
    # Inputs for date range
    start_date_input = st.text_input("Enter start date (YYYY-MM-DD): ", value="2024-01-01")
    end_date_input = st.text_input("Enter end date (YYYY-MM-DD): ", value="2024-01-31")
    
    # Button to fetch events
    if st.button('Fetch Events'):
        db_connection = connect_to_database(db_config)
        events = get_events_between_dates(db_connection, start_date_input, end_date_input)
        display_events(events)
        if db_connection:
            db_connection.close()

if __name__ == "__main__":
    main()
