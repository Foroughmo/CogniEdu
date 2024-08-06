# Chatbot - Ed - Agentic Design 

# Import Necessary Libraries: 

# System
import os
import json
import warnings
import operator
import io
import uuid
from datetime import datetime
import logging
import streamlit as st

# Images
import PIL.Image
import base64
from io import BytesIO
import os

# PDF 
import chromadb
from PyPDF2.errors import PdfReadWarning
from typing import Callable, Any
from typing import TypedDict, Annotated
from google.cloud import storage
from pydantic import BaseModel, Field
import re

# Vertex AI
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel

# DB
from getpass import getpass
from dotenv import set_key
from dotenv import load_dotenv
import mysql.connector

# LangChain / LangGraph
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
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import SystemMessage, HumanMessage, AnyMessage, ToolMessage, AIMessage
from langchain.tools import BaseTool
from difflib import SequenceMatcher

from langchain_community.vectorstores import Chroma
from langchain_community.llms import VertexAI
from langchain_community.document_loaders import PyPDFLoader

# Agent Class
from langchain.tools import Tool, tool
from typing import Union, Callable
import logging

# Import from Utility Files
from utils.PDF_RAG_Query import pdf_rag_query, initialize_system, global_chroma
from utils.Calendar_Query import calendar_query
from utils.Tavily import content_recommendations, get_content_recommendations



# Initialization:
st.set_page_config(layout="wide")

# Access the Environment Variables
load_dotenv()
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
LLM_MODEL = os.getenv("LLM_MODEL")
BUCKET_NAME = os.getenv("BUCKET_NAME")
PDF_FOLDER = os.getenv("PDF_FOLDER")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize Models
llm = ChatVertexAI(model_name=LLM_MODEL, temperature=0, max_tokens=4000)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@st.cache_resource
def cached_initialize_system():
    status = initialize_system()
    return status

@st.cache_resource
def get_llm_calendar():
    return ChatVertexAI(model_name="gemini-1.5-flash-001", temperature=0.1, max_tokens=8192)

# Define Agent Classes:
memory = SqliteSaver.from_conn_string(":memory:")

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

class Agent:
    def __init__(self, model, tools, checkpointer, system=""):
        self.system = system
        graph = StateGraph(AgentState)
        graph.add_node("llm", self.call_gemini)
        graph.add_node("action", self.take_action)
        graph.add_conditional_edges(
            "llm",
            self.exists_action,
            {True: "action", False: END}
        )
        graph.add_edge("action", "llm")
        graph.set_entry_point("llm")
        self.graph = graph.compile(checkpointer=checkpointer)
        self.tools = {t.name: t for t in tools}
        self.model = model.bind_tools(tools)
        
    def log_state(self, state: AgentState, location: str):
        print(f"\n--- State at {location} ---")
        print(f"Number of messages: {len(state['messages'])}")
        print(f"Last message type: {type(state['messages'][-1])}")
        if isinstance(state['messages'][-1], ToolMessage):
            print(f"Last tool used: {state['messages'][-1].name}")
            print(f"Tool result: {state['messages'][-1].content}...")  # First 100 chars
        elif hasattr(state['messages'][-1], 'tool_calls'):
            print(f"Tool calls: {state['messages'][-1].tool_calls}")
        print("------------------------\n")

    def exists_action(self, state: AgentState):
        self.log_state(state, "exists_action")
        result = state['messages'][-1]
        return len(result.tool_calls) > 0

    def call_gemini(self, state: AgentState):
        self.log_state(state, "call_gemini (before)")
        messages = state['messages']
        if self.system:
            messages = [SystemMessage(content=self.system)] + messages
        message = self.model.invoke(messages)
        new_state = {'messages': [message]}
        self.log_state(new_state, "call_gemini (after)")
        return new_state

    def take_action(self, state: AgentState):
        self.log_state(state, "take_action (before)")
        tool_calls = state['messages'][-1].tool_calls
        results = []
        for t in tool_calls:
            print(f"Calling: {t}")
            if t['name'] not in self.tools:
                print("\n....bad tool name....")
                result = "bad tool name, retry"
            else:
                result = self.tools[t['name']].invoke(t['args'])
            results.append(ToolMessage(tool_call_id=t['id'], name=t['name'], content=str(result)))
        print("Back to the model!")
        new_state = {'messages': results}
        self.log_state(new_state, "take_action (after)")
        return new_state
    
    def run(self, query):
        initial_state = {"messages": [HumanMessage(content=query)]}
        final_state = self.graph.invoke(initial_state)
        return final_state

@st.cache_resource
def create_agent():
    agent_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prompt = f"""
    Current datetime: {agent_datetime}
    You are an AI assistant supporting university students. Your primary goal is to provide comprehensive, helpful responses by effectively utilizing the following tools:

    1. pdf_rag_query: Retrieves content from course documents (assignments, lecture notes, syllabi).
       - USE THIS TOOL FIRST for any query about specific course content, including lecture notes, assignments, or syllabus information.
       - Utilizes for query: course name, assignment number, week number, and document type (lecture notes, assignment, syllabus).
       - Example query: "Marketing Analytics Assignment 4 instructions" or "Week 3 Lecture Notes Statistical Analysis"

    2. calendar_query: Searches through calendar events (classes, assignments, discussions AND discussion content, personal events).
       - USE THIS TOOL ONLY for queries about schedules, deadlines, upcoming events, or when a student asks "what do I have" or "when is something due".
       - Example query: "next due assignment" or "upcoming Marketing Analytics classes" or "what do I have due today?"

    3. get_content_recommendations: Web search tool for finding relevant educational resources.
       - USE THIS TOOL ONLY after gathering specific information from pdf_rag_query/calendar_query or when explicitly asked for external resources from the user.
       - Use (only) 2 key terms or concepts for the web search.
       - Example query: "predictive modeling, optimization analysis"

    DECISION-MAKING FRAMEWORK:
    1. Carefully analyze the student's query. Identify the specific information needed to provide a complete answer.
    2. Think and determine the most appropriate tool(s) for the query based on these guidelines:
       - If the query is about course content (lectures, assignments, syllabus), use pdf_rag_query FIRST.
       - If the query is about schedules or deadlines, use calendar_query.
       - If the query is about finding external resources, use get_content_recommendations AFTER using pdf_rag_query/calendar_query or just plainly use get_content_recommendations when students ask for resources on a topic that's not directly from course/calendar content.
    3. Plan your approach step by step:
       a. Decide which tool(s) to use and in what order.
       b. Consider how information from one tool might inform the use of another.
    4. Use tools ONE AT A TIME, in the most logical order to answer the query comprehensively.
    5. For each tool use:
       a. Formulate specific queries based on the student's question and any previously gathered information.
       b. Include relevant course names, assignment numbers, or key concepts as needed.
    6. After each tool use, evaluate:
       a. Review the information received.
       b. Have you gathered all necessary information?
       c. Do you need to use additional tools based on this new information?
       d. Can you now provide a comprehensive answer?
    7. If another tool is needed, formulate the next query based on all information gathered so far.
    8. Only proceed to the next tool after fully processing the results of the previous tool.
    9. For get_content_recommendations, always base your search terms on concrete information from the query or previous tool results, not assumptions.

    EXAMPLES OF TOOL USAGE PATTERNS:
    1. For "Can you give me some resources for the next assignment?":
       - Use calendar_query to identify the next assignment
       - Then use pdf_rag_query to get details about that assignment
       - Finally use get_content_recommendations with key terms from the assignment details

    2. For "What resources would you recommend based on marketing analytics assignment 2?":
       - First use pdf_rag_query to get the content of Marketing Analytics Assignment 2
       - Review the assignment content
       - Then use get_content_recommendations with 2 key concepts from the actual assignment content

    Remember: Each query is unique. Adapt your tool usage based on the specific information needed. Process tools sequentially, using the output of one to inform the use of the next if needed. Do not call multiple tools simultaneously.

    RESPONSE GUIDELINES:
    1. Address the student directly in a helpful, encouraging manner.
    2. Provide a clear, structured response that answers all aspects of the query.
    3. Explain your reasoning if you've made any assumptions or interpretations.
    4. Encourage the student to explore recommended resources when applicable.
    5. Please include all tool responses in the final response.

    Always prioritize providing the most relevant and helpful information to the student based on their specific query and the actual information gathered from the tools.
    """
    llm_calendar = get_llm_calendar()
    return Agent(llm_calendar, [pdf_rag_query, calendar_query, get_content_recommendations], system=prompt, checkpointer=memory)

def should_start_new_thread(previous_query: str, current_query: str) -> bool:
    # Check if the Queries Are Similar
    similarity = SequenceMatcher(None, previous_query.lower(), current_query.lower()).ratio()
    
    # Check if the Current Query Is a Follow-up Question
    follow_up_patterns = [
        r"^(what|how) about",
        r"^and ",
        r"^also",
        r"^additionally",
        r"^moreover",
        r"^furthermore",
        r"^in addition",
    ]
    
    is_follow_up = any(re.match(pattern, current_query.lower()) for pattern in follow_up_patterns)
    
    # Start a New Thread if the Queries Are Not Similar and It’s Not a Follow-up Question
    return similarity < 0.7 and not is_follow_up

last_query = ""
current_thread_id = str(uuid.uuid4())

def process_query(query: str) -> str:
    global last_query, current_thread_id
    
    # Check if We Should Start a New Thread
    if should_start_new_thread(last_query, query):
        current_thread_id = str(uuid.uuid4())
        print(f"Starting new thread with ID: {current_thread_id}")
    
    agent = create_agent()
    messages = [HumanMessage(content=query)]
    thread = {"configurable": {"thread_id": current_thread_id}}
    result = agent.graph.invoke({"messages": messages}, thread)
    
    # Extract the Calendar Query Response and Content Recommendations
    calendar_response = ""
    content_recommendations = ""
    pdf_rag_response = ""
    
    tool_responses_found = False
    
    for message in result['messages']:
        if isinstance(message, ToolMessage):
            tool_responses_found = True
            if message.name == 'calendar_query':
                calendar_response = message.content
            elif message.name == 'get_content_recommendations':
                content_recommendations = message.content
            elif message.name == 'pdf_rag_query':
                pdf_rag_response = message.content
    
    if tool_responses_found:
        # Combine the Responses if Tools Were Used
        final_response = f"{calendar_response}\n\n{pdf_rag_response}\n\n{content_recommendations}".strip()
    else:
        # Use the Agent’s Direct Response if No Tools Were Used
        final_response = result['messages'][-1].content
    
    # Update the Last Query
    last_query = query
    
    return final_response

def run_agent_page():
    logger.info("Starting run_agent_page")
    init_status = cached_initialize_system()
    st.sidebar.write(f"Initialization Status: {init_status}")
    logger.info(f"Initialization Status: {init_status}")

    # Check if Initialization Was Successful
    if "successfully" not in init_status.lower():
        st.error("System initialization failed. Please check the logs and try restarting the application.")
        logger.error("System initialization failed. Exiting run_agent_page.")
        return  # Exit the function if initialization failed

    logger.info("System initialized successfully. Continuing with run_agent_page.")
    
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
            .fc-button-primary {
                background-color: #3B47CE;
                border-color: #3B47CE;
            }
            .fc-button-primary:hover {
                background-color: #2d389e;
                border-color: #2d389e;
            }
            .fc-button-primary:focus {
                background-color: #3B47CE;
                border-color: #3B47CE;
                box-shadow: none;
            }
            .fc-button-primary:active {
                background-color: #3B47CE;
                border-color: #3B47CE;
            }
            .fc-button-primary.fc-button-active {
                background-color: #2d389e;
                border-color: #2d389e;
            }
            .fc-today-button {
                background-color: #A3B9FF;
                border-color: #A3B9FF;
            }
            .fc-today-button:hover {
                background-color: #809aff;
                border-color: #809aff;
            }
            .fc-today-button:focus {
                background-color: #A3B9FF;
                border-color: #A3B9FF;
                box-shadow: none;
            }
            .fc-today-button:active {
                background-color: #A3B9FF;
                border-color: #A3B9FF;
            }
            .fc-today-button.fc-button-active {
                background-color: #809aff;
                border-color: #809aff;
            }
            .st-chat-input {
                background-color: #D8EFFF;
                border: 1px solid #3B47CE;
                color: black !important;
                padding: 10px;
                border-radius: 5px;
                font-size: 16px;
                font-weight: bold;
            }
            .recommended-question {
                background-color: white;
                border: 3px solid #3B47CE;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
                cursor: pointer;
                text-align: center;
            }
            .recommended-question:hover {
                background-color: #f0f2f6;
            }
        </style>
    """
    
    st.markdown(custom_css, unsafe_allow_html=True)

    # Main Header
    ed_image_path = open("EdBanner.png", "rb") 
    ed_image = PIL.Image.open(ed_image_path)
    buffered = BytesIO()
    ed_image.save(buffered, format="PNG")
    img_str_ed = base64.b64encode(buffered.getvalue()).decode()

    st.markdown(f'''
        <div style="text-align: center;">
            <img src="data:image/png;base64,{img_str_ed}" style="width: 100%;">
        </div>
    ''', unsafe_allow_html=True)

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.show_recommended = True
    
    if "last_query" not in st.session_state:
        st.session_state.last_query = ""
        
    if "current_thread_id" not in st.session_state:
        st.session_state.current_thread_id = str(uuid.uuid4())
        
    # Clear Conversation Button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_query = ""
        st.session_state.current_thread_id = str(uuid.uuid4())
        st.session_state.show_recommended = True
        st.experimental_rerun()
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar='🧠' if message["role"] == "user" else '🧑‍🎓'):
            st.markdown(message["content"])
            
    # Show Recommended Questions Only if No Query Has Been Asked Yet
    if st.session_state.show_recommended:
        st.markdown("#### Recommended Questions")
        if st.button("Ask about your schedule on Friday", key="q1", use_container_width=True):
            prompt = "What is my schedule on Friday?"
            st.session_state.show_recommended = False
        elif st.button("Ask about your course syllabus", key="q2", use_container_width=True):
            prompt = "What is the course syllabus?"
            st.session_state.show_recommended = False
        elif st.button("Ask about your next assignment due date", key="q3", use_container_width=True):
            prompt = "When is my next assignment due?"
            st.session_state.show_recommended = False

    # React to User Input
    if prompt := st.chat_input("What would you like to know?", key="chat_input"):
        
        if should_start_new_thread(st.session_state.last_query, prompt):
            st.session_state.current_thread_id = str(uuid.uuid4())
            st.info(f"Starting new conversation thread.")
            
        st.session_state.show_recommended = False
        # Display User Message in Chat Message Container
        st.chat_message("user", avatar='🧑‍🎓').markdown(prompt)
        # Add User Message to Chat History
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get Response from Agent
        with st.spinner("Ed is Thinking..."):
            agent = create_agent()
            messages = [HumanMessage(content=prompt)]
            thread = {"configurable": {"thread_id": st.session_state.current_thread_id}}
            result = agent.graph.invoke({"messages": messages}, thread)

            # Process the Result
            tool_responses_found = False
            calendar_response = ""
            content_recommendations = ""
            pdf_rag_response = ""

            for message in result['messages']:
                if isinstance(message, ToolMessage):
                    tool_responses_found = True
                    if message.name == 'calendar_query':
                        calendar_response = message.content
                    elif message.name == 'get_content_recommendations':
                        content_recommendations = message.content
                    elif message.name == 'pdf_rag_query':
                        pdf_rag_response = message.content

            if tool_responses_found:
                response = f"{calendar_response}\n\n{pdf_rag_response}\n\n{content_recommendations}".strip()
            else:
                response = result['messages'][-1].content
        
        # Display Assistant Response in Chat Message Container
        with st.chat_message("assistant", avatar='🧠'):
            st.markdown(response)

        # Add Assistant Response to Chat History
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.last_query = prompt

if __name__ == "__main__":
    run_agent_page()
    
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
logo = open("cogniedulogo.png", "rb")
logo_small = PIL.Image.open(logo).resize((100, 100))
buffered = BytesIO()
logo_small.save(buffered, format="PNG")
img_str_small = base64.b64encode(buffered.getvalue()).decode()

# Display Logo Above the Navigation
st.sidebar.markdown(f'''
    <div style="text-align: center; padding: 20px 0;">
        <img src="data:image/png;base64,{img_str_small}" style="width: 150px;">
    </div>
''', unsafe_allow_html=True)

st.sidebar.page_link('pages/5_Home.py', label='🏠 Home')
st.sidebar.page_link('pages/6_Calendar.py', label='📆 Calendar')
st.sidebar.page_link('pages/7_Chatbot.py', label='🧠 Ed')
