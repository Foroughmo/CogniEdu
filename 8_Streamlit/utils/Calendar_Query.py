### Calendar Querying Logic 

# system
import os
import json
import warnings
import operator
import io
import uuid
from datetime import datetime
import logging

# PDF 
import chromadb
from PyPDF2.errors import PdfReadWarning
from typing import Callable, Any
from typing import TypedDict, Annotated
from google.cloud import storage
from pydantic import BaseModel, Field

# Vertex AI
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel


# DB
from getpass import getpass
from dotenv import set_key
from dotenv import load_dotenv
import mysql.connector


#Langchain / Langgraph
from langchain.vectorstores import Chroma
from langchain.llms import VertexAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain.agents import initialize_agent, Tool
from langchain.agents import AgentType
from langchain.memory import ConversationBufferMemory
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage, ToolMessage
from langchain.tools import BaseTool
from IPython.display import Image, display

from langchain_community.vectorstores import Chroma
from langchain_community.llms import VertexAI
from langchain_community.document_loaders import PyPDFLoader


# Initialization
# access the environment variables
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
LLM_MODEL = os.getenv("LLM_MODEL")
BUCKET_NAME = os.getenv("BUCKET_NAME")
PDF_FOLDER = os.getenv("PDF_FOLDER")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")


# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Chroma client and collection
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="class_materials")

# Initialize models
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
llm = ChatVertexAI(model_name=LLM_MODEL, temperature=0)

llm_calendar = ChatVertexAI(model_name=LLM_MODEL, temperature=.1, max_tokens=8192)



def get_events():
    # Get database connection details from environment variables
    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_database = os.getenv("DB_DATABASE")

    try:
        # Establish database connection
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_database
        )
        
        # Create cursor
        cursor = mydb.cursor()
        
        # Execute the SELECT query with ordering
        query = """
        SELECT events_json
        FROM Events
        WHERE is_deleted = 0
        ORDER BY COALESCE(start_time, due_date) ASC
        """
        
        cursor.execute(query)
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        formatted_events = []
        for row in rows:
            events_json = row[0]
            event_dict = json.loads(events_json)
            formatted_events.append(json.dumps(event_dict))
        
        # Join formatted events with double newlines
        return "\n\n".join(formatted_events)

    except mysql.connector.Error as err:
        print(f"Something went wrong: {err}")
        return None

    finally:
        # Close cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'mydb' in locals():
            mydb.close()
            
            
            
# Get the events context
events_context = get_events()



def query_calendar(query, llm):
    
    # Get current date and time
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the context with a header and code block
    formatted_context = f"""
    
    This is the current date and time: {current_datetime}
    
    Below is a list of events in the student's calendar, ordered chronologically. Each event is represented as a JSON object:

    ```
    {events_context}
    ```
    
    All events have the following fields:
    - tag: The type of event (class, personal, study time, quiz, discussion, or assignment)
    - title: The title of the event
    - eventDuration: The duration of the event in minutes 
    - description: A description of the event (if available)

    Each assigment, quiz, or discussion could have the following additional fields: 
    - due_date: The due date (for assignment type events)
    - instructions: instructions for the academic activity 
    
    Each event that is not an assignment, quiz, or discussion has the following fields:
    - startTime: The start time of the event (for non-assignment type events)
    - endTime: The end time of the event (for non-assignment type events)
    
    """

    prompt = f"""
    You are an AI assistant for a student calendar management system. You have been provided with the following context, which contains information about the student's events in chronological order:

    {formatted_context}

    Based on this context, please answer the following question:
    {query}

    Guidelines for your response:
    1. Provide accurate information based on the given context.
    2. If the exact answer isn't in the context, use your knowledge to give a relevant response, but clearly state that it's not directly from the calendar data.
    3. Remember that the events are already in chronological order with some events in the past and some in the future. 
    4. For assignment-type events, use the due_date field. For other events, use startTime and endTime.
    5. If asked about free time or scheduling, consider the startTime and endTime of events.
    6. Offer helpful suggestions or insights based on the student's schedule when appropriate.
    7. Keep your response concise yet informative.
    8. If you need more information to answer accurately, ask for clarification.
    9. If you ever output a date/time please convert it to standard looking date/time format (11:59 PM or August 1st, 2024)
    
    Answer (PLEASE DON'T OUTPUT IN JSON FORMAT):
    """
    
    response = llm.predict(prompt)
    return response


#TOOL FOR AGENT

@tool
def calendar_query(query: str) -> str:
    """
    Query the student's calendar for information about events, classes, assignments, and schedule.
    
    Args:
        query: The question or query about the student's calendar and schedule.
    
    Returns:
        A response based on the information found in the student's calendar.
    """
    response = query_calendar(query, llm_calendar)
    return response


# Final Calendar Query system 

def calendar_query_system():
    # Step 1: Load .env
    print("Loading environment variables...")
    load_dotenv()

    # Step 2: Initialize LLM model
    print("Initializing LLM model...")
    llm_calendar = ChatVertexAI(model_name=LLM_MODEL, temperature=.1, max_tokens=8192)

    # Step 3: Fetch events from the database
    print("Fetching events from the database...")
    events_context = get_events()
    if not events_context:
        print("Error: Failed to fetch events from the database.")
        return

    # Step 4: Set up the query system
    print("Setting up the calendar query system...")

    while True:
        user_query = input("Enter your query about the calendar (or 'quit' to exit): ")
        if user_query.lower() == 'quit':
            break

        print("Querying the calendar...")
        response = query_calendar(user_query, llm_calendar)
        print("\nResponse:")
        print(response)
        print("\n" + "-"*50 + "\n")

    print("Calendar query system orchestration completed.")

if __name__ == "__main__":
    calendar_query_system()