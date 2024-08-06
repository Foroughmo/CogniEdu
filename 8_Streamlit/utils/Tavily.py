# Tavily Search Engine

# Import Libraries 

#Tavily
from tavily import TavilyClient
from langchain.utilities.tavily_search import TavilySearchAPIWrapper
from langchain.tools.tavily_search import TavilySearchResults

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

# Vertex AI
import vertexai
from vertexai.language_models import TextEmbeddingModel, TextGenerationModel


# DB
from getpass import getpass
from dotenv import set_key
from dotenv import load_dotenv
import mysql.connector


# Langchain / Langgraph
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

# For Agent Class
from langchain.tools import Tool, tool
from typing import Union, Callable

# Import from utility files
from utils.PDF_RAG_Query import pdf_rag_query, process_pdfs_from_gcs
from utils.Calendar_Query import calendar_query


# Set up API key
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def content_recommendations(query: str) -> str:
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    tavily_client = TavilyClient(api_key = tavily_api_key)

    search_query = f"What are some highly recommended, freely accessible resources to learn about {query}? Focus on reputable blog posts, open-access articles, and educational websites."

    response = tavily_client.search(search_query, search_depth="advanced", include_answer=True, max_results=3)

    recommendations = f"Here are some recommended resources based on a few keywords taken from the content: {query}:\n\n"

    for i, result in enumerate(response['results'], 1):
        logger.info(f"Processing result {i}: {result}")
        
        title = result.get('title', 'No title available')
        url = result.get('url', 'No URL available')
        content = result.get('content', 'No content available')
        score = result.get('score', 0.0)

        # Clean and truncate the summary
        #summary = ' '.join(content.split())[:200] + '...' if content else 'No summary available'

        recommendations += f"{i}. {title} (Relevance: {score:.2f})\n"
        recommendations += f"   URL: {url}\n"
        #recommendations += f"   Summary: {summary}\n\n"

    return recommendations



# Tool for content recommendations
@tool
def get_content_recommendations(query: str) -> str:
    """
    Get content recommendations for learning about a specific subject.
    
    Args:
        query: The subject or topic the user wants to learn about.
    
    Returns:
        A string containing relevant links and brief descriptions of recommended resources.
    """
    recommendations = content_recommendations(query)
    return recommendations
