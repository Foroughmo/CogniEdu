# PDF RAG Query 

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

# Global
global global_chroma
global_chroma = None



# Initialization

# Access the environment variables
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
embedding_function = VertexAIEmbeddings(model_name=EMBEDDING_MODEL)

# Initialize models
llm = ChatVertexAI(model_name=LLM_MODEL, temperature=.1, max_tokens = 2000)

llm_calendar = ChatVertexAI(model_name=LLM_MODEL, temperature=.1, max_tokens=8000)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_system():
    global global_chroma, chroma_client
    
    try:
        logger.info("Initializing system...")
        chroma_client = chromadb.Client()
        logger.info("Chroma client initialized.")
        
        logger.info("Getting or creating collection...")
        collection = chroma_client.get_or_create_collection(name="class_materials")
        
        if collection.count() == 0:
            logger.info("Collection is empty, processing PDFs...")
            process_pdfs_from_gcs(BUCKET_NAME, PDF_FOLDER, collection)
            logger.info("PDF processing complete. Vector store updated.")
        else:
            logger.info("Using existing processed PDFs.")
        
        logger.info("Initializing global_chroma...")
        global_chroma = Chroma(
            client=chroma_client,
            collection_name="class_materials",
            embedding_function=embedding_function
        )
        logger.info("System initialization complete.")
        return "System initialized successfully"
    except Exception as e:
        logger.error(f"Error during system initialization: {str(e)}", exc_info=True)
        return f"Error: {str(e)}"

        
    
# # Prompt for new values (even if they already exist in .env)
# new_db_host = input("Enter new database host (or press Enter to keep current): ")
# new_db_user = input("Enter new database user (or press Enter to keep current): ")
# new_db_password = getpass("Enter new database password (input hidden, or press Enter to keep current): ")
# new_db_database = input("Enter new database name (or press Enter to keep current): ")

# # Update .env file with the new values (if provided)
# if new_db_host:
#     set_key(".env", "DB_HOST", new_db_host)
# if new_db_user:
#     set_key(".env", "DB_USER", new_db_user)
# if new_db_password:
#     set_key(".env", "DB_PASSWORD", new_db_password)
# if new_db_database:
#     set_key(".env", "DB_DATABASE", new_db_database)

# load_dotenv()  # Reload .env to get the new values



# PDF Query Logic

def extract_metadata_from_filename(filename):
    parts = filename.split('_')
    print(f"Extracting metadata from filename: {filename}")
    print(f"Filename parts: {parts}")
    
    # Determine course name
    if filename.startswith("Marketing_Analytics"):
        course_name = "Marketing Analytics"
        remaining_parts = parts[2:]
    elif filename.startswith("Statistical_Analysis"):
        course_name = "Statistical Analysis"
        remaining_parts = parts[2:]
    elif filename.startswith("Introduction_to_Art_History"):
        course_name = "Introduction to Art History"
        remaining_parts = parts[4:]
    else:
        course_name = "Unknown Course"
        remaining_parts = parts

    # Extract week information
    week_number = ""
    for i, part in enumerate(remaining_parts):
        if part == "Week" and i + 1 < len(remaining_parts):
            week_number = remaining_parts[i + 1]
            break

    # Determine document type and assignment number
    document_type = "Other"
    assignment_number = ""
    if "Assignment" in filename:
        document_type = "Assignment"
        assignment_number = remaining_parts[-1].split('.')[0]  # Get the number before .pdf
    elif "Lecture" in filename:
        document_type = "Lecture Notes"
    elif "Syllabus" in filename:
        document_type = "Syllabus"

    return course_name, document_type, week_number, assignment_number


def clean_metadata(metadata):
    """Standardize metadata formatting while preserving all fields."""
    print("Cleaning metadata:")
    print(f"Input metadata: {metadata}")
    cleaned = {}
    for k, v in metadata.items():
        if k in ['course_name', 'document_type']:
            cleaned[k] = str(v).lower() if v is not None else ""
        elif k in ['week', 'assignment_number', 'page', 'source']:
            cleaned[k] = str(v) if v is not None and v != "" else ""
        else:
            cleaned[k] = str(v) if v is not None else ""
    return cleaned



def process_pdfs_from_gcs(bucket_name, pdf_folder, collection):
    global chroma_client
    
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=pdf_folder)
    
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=300)
    
    # Suppress PyPDF2 warnings
    warnings.simplefilter("ignore", PdfReadWarning)
    warnings.filterwarnings("ignore", message="Ignoring wrong pointing object")
    
    logging.getLogger('PyPDF2').setLevel(logging.ERROR)
    
    for blob in blobs:
        if blob.name.endswith(".pdf"):
            filename = blob.name.split('/')[-1]
            temp_file_path = f"/tmp/{filename}"
            blob.download_to_filename(temp_file_path)
            
            try:
                loader = PyPDFLoader(temp_file_path)
                pages = loader.load_and_split()
                
                course_name, document_type, week_number, assignment_number = extract_metadata_from_filename(filename)
                
                for page in pages:
                    chunks = text_splitter.split_text(page.page_content)
                    all_chunks.extend(chunks)
                    
                    for chunk in chunks:
                        chunk_id = str(uuid.uuid4())
                        all_ids.append(chunk_id)
                        
                        raw_metadata = {
                            "source": filename,
                            "page": str(page.metadata.get('page', '')),
                            "course_name": course_name,
                            "document_type": document_type,
                            "week": week_number,
                            "assignment_number": assignment_number
                        }
                        
                        cleaned_metadata = clean_metadata(raw_metadata)
                        all_metadatas.append(cleaned_metadata)
                
                os.remove(temp_file_path)
            except Exception as e:
                print(f"Error processing file {filename}: {str(e)}")
                continue
    
    if not all_chunks:
        print("No valid chunks were extracted from the PDFs.")
        return
    
    print(f"Extracted {len(all_chunks)} chunks.")
    
    # Generate embeddings
    embeddings = VertexAIEmbeddings(model_name=EMBEDDING_MODEL)
    embedded_chunks = []
    for i, chunk in enumerate(all_chunks):
        try:
            embedding = embeddings.embed_query(chunk)
            embedded_chunks.append(embedding)
        except Exception as e:
            print(f"Failed to embed chunk {i}: {str(e)}")
            print(f"Chunk content: {chunk[:100]}...")
    
    print(f"Generated {len(embedded_chunks)} embeddings.")
    
    if len(all_chunks) != len(embedded_chunks):
        print("Warning: Number of chunks doesn't match number of embeddings.")
        print("Chunks without embeddings:")
        for i, chunk in enumerate(all_chunks):
            if i >= len(embedded_chunks):
                print(f"Chunk {i}: {chunk[:250]}...")
    
    # Ensure all lists have the same length
    min_length = min(len(all_ids), len(embedded_chunks), len(all_metadatas), len(all_chunks))
    all_ids = all_ids[:min_length]
    embedded_chunks = embedded_chunks[:min_length]
    all_metadatas = all_metadatas[:min_length]
    all_chunks = all_chunks[:min_length]
    
    print(f"Final count: {min_length} items.")
    
    # Add to the existing Chroma collection
    try:
        collection.add(
            ids=all_ids,
            embeddings=embedded_chunks,
            metadatas=all_metadatas,
            documents=all_chunks
        )
        print(f"Added {min_length} chunks to the collection.")
    except ValueError as e:
        print(f"Error adding documents to collection: {str(e)}")
        print("First few metadatas for debugging:")
        for metadata in all_metadatas[:5]:
            print(metadata)
    
    return collection



def extract_details_llm(query, llm_model):
    llm_prompt = f"""
    Analyze the following query and extract these details:
    1. Course Name (one of 'Marketing Analytics', 'Statistical Analysis', or 'Introduction to Art History')
    2. Document Type (e.g., 'Assignment', 'Lecture Notes', 'Syllabus', or any other relevant type)
    3. Week Number (if mentioned, e.g., from 'Week 1' extract only '1')
    4. Assignment Number (if mentioned, e.g., from 'Assignment 1' extract only '1')

    If any detail is not specified in the query, leave it blank.

    Query: {query}

    Respond ONLY with the extracted details in this EXACT format, separating each with a comma:
    <Course Name>,<Document Type>,<Week Number>,<Assignment Number>

    Example response format:
    Marketing Analytics,Assignment,,2

    Your response:
    """
    response = llm_model.predict(llm_prompt)
    response = response.strip()
    
    parts = response.split(',')
    course_name = parts[0].strip() if len(parts) > 0 else ""
    document_type = parts[1].strip() if len(parts) > 1 else ""
    week_number = parts[2].strip() if len(parts) > 2 else ""
    assignment_number = parts[3].strip() if len(parts) > 3 else ""

    return course_name, document_type, week_number, assignment_number



def generate_response(query, context, llm):
    prompt = f"""
    You are an AI assistant for university courses including Marketing Analytics, Statistical Analysis, and Introduction to Art History. You have been given the following context information from course materials:

    {context}

    Based on this context, please answer the following question:

    {query}

    If the answer is not explicitly stated in the context, use your knowledge to provide a relevant response, but make it clear that this information is not directly from the course materials.

    Your response should be:
    1. Accurate based on the given context
    2. Concise yet informative
    3. Structured in a clear, easy-to-read format
    4. Tailored to the specific course (Marketing Analytics, Statistical Analysis, or Introduction to Art History) when applicable

    Answer:
    """
    
    response = llm.predict(prompt)
    return response


def query_collection(query, top_k=5):
    global global_chroma
    
    if global_chroma is None:
        print("global_chroma is not initialized. Attempting to initialize...")
        init_status = initialize_system()
        print(f"Initialization status: {init_status}")
        if global_chroma is None:
            return "Error: Unable to initialize the system. Please check your setup."
    
    course_name, document_type, week_number, assignment_number = extract_details_llm(query, llm_calendar)
    print(f"Extracted - Course: {course_name}, Type: {document_type}, Week: {week_number}, Assignment: {assignment_number}")
    
    filter_conditions = []
    if course_name:
        filter_conditions.append({"course_name": {"$eq": course_name.lower()}})
    if document_type:
        filter_conditions.append({"document_type": {"$eq": document_type.lower()}})
    if week_number:
        filter_conditions.append({"week": {"$eq": week_number}})
    if assignment_number:
        filter_conditions.append({"assignment_number": {"$eq": assignment_number}})
    
    if len(filter_conditions) > 1:
        filter_dict = {"$and": filter_conditions}
    elif len(filter_conditions) == 1:
        filter_dict = filter_conditions[0]
    else:
        filter_dict = {}
    
    print(f"Using filter: {filter_dict}")
    
    try:
        results = global_chroma.similarity_search_with_score(
            query,
            k=top_k,
            filter=filter_dict
        )
    except Exception as e:
        print(f"Error during similarity search: {str(e)}")
        return "An error occurred while searching for relevant information."
    
    if not results:
        # If no results, try a more relaxed search
        relaxed_filter = {"course_name": {"$eq": course_name.lower()}} if course_name else {}
        try:
            results = global_chroma.similarity_search_with_score(
                query,
                k=top_k,
                filter=relaxed_filter
            )
        except Exception as e:
            print(f"Error during relaxed similarity search: {str(e)}")
            return "An error occurred while searching for relevant information."
    
    if not results:
        return "No relevant information found in the course documents."
    
    context = "\n\n".join([f"Source: {doc.metadata['source']}, Page: {doc.metadata['page']}\n{doc.page_content}" for doc, _ in results])
    response = generate_response(query, context, llm)
    return response



@tool
def pdf_rag_query(query: str) -> str:
    """
    Query PDF documents for course information, assignments, and lecture content.
    
    Args:
        query: The question or query about course materials.
    
    Returns:
        A response based on the information found in the course PDFs.
    """
    response = query_collection(query)
    return response





def pdf_query_system():
    # Step 1: Initialize the system
    print("Initializing system...")
    initialize_system()
    
    # Step 2: Confirm Chroma setup
    if global_chroma is None:
        print("Error: Chroma not properly initialized.")
        return
    
    # Step 3: Verify PDF processing
    collection = chroma_client.get_collection(name="class_materials")
    if collection.count() == 0:
        print("Warning: No documents in the collection. Processing PDFs...")
        process_pdfs_from_gcs(BUCKET_NAME, PDF_FOLDER, collection)
    else:
        print(f"Collection contains {collection.count()} documents.")
    
    # Step 4: Set up the query system
    print("PDF query system ready. You can now enter queries.")
    
    while True:
        query = input("Enter your query about the course materials (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        print("Processing query...")
        response = query_collection(query)
        print("\nResponse:")
        print(response)
        print("\n" + "-"*50 + "\n")

    print("PDF query system session ended.")

if __name__ == "__main__":
    pdf_query_system()