# Time Estimation and Assignment Difficulty Level by LLM 

# Import libraries
import os
import io
import re
import sys
import logging
import numpy as np
import pandas as pd
from google.cloud import storage
import PyPDF2
import vertexai
from vertexai.generative_models import GenerativeModel

# .env set up
from dotenv import load_dotenv
from pathlib import Path

# Get the path to the directory containing script
base_dir = Path(__file__).resolve().parent.parent

# Construct the path to the .env file
dotenv_path = base_dir / '.env'

# Load the .env file
load_dotenv(dotenv_path)


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Vertex AI
try:
    PROJECT_ID = os.getenv("PROJECT_ID")
    LOCATION = os.getenv("LOCATION")
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    PDF_FOLDER = os.getenv("PDF_FOLDER")
    folder_name = os.getenv("PDF_FOLDER")


    vertexai.init(project=PROJECT_ID, location=LOCATION)
except Exception as e:
    logging.error(f"Failed to initialize Vertex AI: {e}")
    sys.exit(1)



def load_pdf_from_gcs(bucket_name, blob_name):
    """Load PDF content from Google Cloud Storage and clean it."""
    try:
        logging.info(f"Attempting to load PDF from bucket: {bucket_name}, blob: {blob_name}")
        
        # Initialize the Google Cloud Storage client
        storage_client = storage.Client()
        
        # Get the bucket
        bucket = storage_client.bucket(bucket_name)
        
        # Get the blob (file)
        blob = bucket.blob(blob_name)
        
        # Download the blob's content as bytes
        pdf_content = blob.download_as_bytes()
        logging.info(f"Successfully downloaded PDF content for {blob_name}")
        
        # Use PyPDF2 to extract text from the PDF content
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        text_content = ""
        for page in pdf_reader.pages:
            text_content += page.extract_text() + " "
        
        logging.info(f"Successfully extracted text from PDF {blob_name}")
        
        # Clean text
        # Remove extra whitespace
        text_content = " ".join(text_content.split())
        
        # Remove special characters while preserving words
        text_content = re.sub(r'(\b\w*)\W+(\w*\b)', r'\1 \2', text_content)
        
        logging.info(f"Cleaned text for {blob_name}. Length: {len(text_content)} characters")
        
        return text_content
    
    except storage.exceptions.NotFound:
        logging.error(f"Bucket or blob not found: {bucket_name}/{blob_name}")
        return None
    except storage.exceptions.Forbidden:
        logging.error(f"Access denied to bucket or blob: {bucket_name}/{blob_name}")
        return None
    except PyPDF2.errors.PdfReadError as e:
        logging.error(f"Error reading PDF {blob_name}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error loading PDF from GCS: {str(e)}", exc_info=True)
        return None

    
    
def extract_names(file_name):
    """Extract course name and assignment name from filename."""
    parts = file_name.split('_')
    if len(parts) >= 3:
        if file_name.startswith("Marketing_Analytics"):
            course_name = "Marketing Analytics"
            remaining_parts = parts[2:]
        elif file_name.startswith("Statistical_Analysis"):
            course_name = "Statistical Analysis"
            remaining_parts = parts[2:]
        elif file_name.startswith("Introduction_to_Art_History"):
            course_name = "Introduction to Art History"
            remaining_parts = parts[4:]
        else:
            course_name = "Unknown Course"
            remaining_parts = parts
        assignment_name = parts[-2] + ' ' + parts[-1].split('.')[0]
        return course_name, assignment_name
    else:
        return None, None

def get_llm_response(input_text, temperature=0.1):
    try:
        model = GenerativeModel("gemini-1.0-pro-002")
        responses = model.generate_content(
            [input_text],
            generation_config={
                "max_output_tokens": 2048,
                "temperature": temperature,
                "top_p": 1
            },
            stream=True,
        )
        
        full_response = ""
        for response in responses:
            full_response += response.text
        
        return full_response
    except Exception as e:
        logging.error(f"Error in LLM response: {e}")
        return None

def process_assignments(df):
    grouped_assignments = df.groupby('Course Name')
    all_difficulties = {}
    
    for course, group in grouped_assignments:
        assignments = group['Content'].tolist()
        assignment_names = group['Assignment Name'].tolist()
        
        assignment_descriptions = [f"{name}: {content}" for name, content in zip(assignment_names, assignments)]
        
        prompt = f"""
        For the course '{course}', evaluate the difficulty level of each assignment based on the following descriptions:

        {'. '.join(assignment_descriptions)}
        
         Assign a difficulty level (Easy, Medium, or Hard) to each assignment. Here is an example of how to assign difficulty level to each assignment:
        
         This is an example of an easy assignment: 
         Assignment: Introduction to Art History - Easy Level

         Title: Understanding Renaissance Art
         Objective:  
         Introduce students to Renaissance art by analyzing a famous artwork.

         Instructions:
         1. Choose an Artwork: Select one of the following:
            - "Mona Lisa" by Leonardo da Vinci
            - "The Last Supper" by Leonardo da Vinci
            - "The School of Athens" by Raphael
            - "The Birth of Venus" by Sandro Botticelli

         2. Research: Use at least two credible sources for information.

         3. Write a 500-word Essay: Include:
            - Introduction: Artist, title, and creation date.
            - Description: Subject matter, composition, color, techniques.
            - Historical Context: Significance and reflection of Renaissance values.
            - Personal Reflection: Personal thoughts and feelings about the artwork.

         4. Submission: Submit as a PDF via Canvas by [due date].
        
         Here is another example for marketing analytics with difficulty level of hard :
         Assignment: Marketing Analytics - Hard Level

         Title: Advanced Customer Segmentation Analysis

         Objective:  Conduct a detailed customer segmentation analysis using advanced clustering techniques to identify distinct customer groups and provide strategic marketing insights.

         Instructions:

         1. Dataset: Use the provided dataset with customer purchase history, demographics, and engagement metrics.

         2. Data Preprocessing: Clean and preprocess the data, handle missing values, and normalize the data.

         3. Clustering Analysis: Apply at least two clustering algorithms (e.g., K-Means, Hierarchical Clustering), and determine the optimal number of clusters using methods like the Elbow Method and Silhouette Score.

         4. Segmentation Analysis:Analyze and interpret the resulting clusters, profiling each segment based on key attributes.

         5. Strategic Insights: Provide actionable marketing strategies and personalized campaigns for each segment.

         6. Report (1500 words max): Include an introduction, methodology, results with visualizations, and recommendations. Submit the report and code/script as a ZIP file via Canvas by [due date].

        
        Assign a difficulty level (Easy, Medium, or Hard) to each assignment.
        Format your response as follows:
        * **Assignment X:** Difficulty

        Only provide the difficulty levels, no additional explanation.
        """
        
        llm_response = get_llm_response(prompt)
        
        if not llm_response:
            logging.warning(f"No valid response received for course '{course}'. Skipping.")
            continue
        
        difficulty_map = {'Easy': 1, 'Medium': 2, 'Hard': 3}
        course_difficulties = {}
        
        for line in llm_response.split('\n'):
            line = line.strip()
            match = re.search(r'\*\*Assignment (\d+):\*\* (\w+)', line)
            if match:
                assignment_num, difficulty = match.groups()
                assignment_name = f"Assignment {assignment_num}"
                course_difficulties[assignment_name] = difficulty_map.get(difficulty.strip(), float('nan'))
        
        all_difficulties[course] = course_difficulties
        logging.info(f"Parsed difficulties for {course}: {course_difficulties}")
    
    df['Difficulty_Level'] = df.apply(
        lambda row: all_difficulties.get(row['Course Name'], {}).get(row['Assignment Name'], float('nan')),
        axis=1
    )
    
    return df

def estimate_completion_time(row):
    prompt = f"""
    Based on the following assignment details, estimate the time (in hours) it would take an average student to complete the assignment. Restrict time estimation for each assignment to a maximum of 8 hours and do not go above the time limit. Be very brief in your response and briefly explain the reasons. 

    Assignment Name: {row['Assignment Name']}
    Course: {row['Course Name']}
    Content: {row['Content']}
    Assignment Type: {row['Assignment Type']}
    Difficulty Level: {row['Difficulty_Level']} (on a scale of 1-3, where 3 is most difficult)
    
    Please provide your estimate as a single number representing hours. For example: 5.5
    """
    
    logging.info(f"Sending prompt for assignment: {row['Assignment Name']}")
    response = get_llm_response(prompt)
    logging.info(f"Received response: {response}")
    
    if response is None:
        logging.warning(f"No response received from LLM for assignment: {row['Assignment Name']}")
        return float('nan')
    
    try:
        numbers = re.findall(r'\d+(?:\.\d+)?', response)
        if numbers:
            estimated_time = float(numbers[0])
            return min(estimated_time, 8.0)  # Cap at 8 hours
        else:
            logging.warning(f"No numeric estimate found in LLM response for assignment: {row['Assignment Name']}")
            return float('nan')
    except ValueError as e:
        logging.error(f"Error parsing time estimate from LLM response for assignment: {row['Assignment Name']}. Error: {e}")
        return float('nan')

def main():
    try:
        
        logging.info(f"Current working directory: {os.getcwd()}")
        logging.info(f"BUCKET_NAME: {os.getenv('BUCKET_NAME')}")
        logging.info(f"PDF_FOLDER: {os.getenv('PDF_FOLDER')}")
        
        BUCKET_NAME = os.getenv("BUCKET_NAME")
        PDF_FOLDER = os.getenv("PDF_FOLDER")
        PROJECT_ID = os.getenv("PROJECT_ID")
        LOCATION = os.getenv("LOCATION")
        folder_name = os.getenv("PDF_FOLDER")
        
        vertexai.init(project=PROJECT_ID, location=LOCATION)

        filenames = [
            'Introduction_to_Art_History_Week_1_Assignment_1.pdf',
            'Introduction_to_Art_History_Week_2_Assignment_2.pdf',
            'Introduction_to_Art_History_Week_3_Assignment_3.pdf',
            'Marketing_Analytics_Week_1_Assignment_1.pdf',
            'Marketing_Analytics_Week_2_Assignment_2.pdf',
            'Marketing_Analytics_Week_3_Assignment_3.pdf',
            'Marketing_Analytics_Week_4_Assignment_4.pdf',
            'Statistical_Analysis_Week_1_Assignment_1.pdf',
            'Statistical_Analysis_Week_2_Assignment_2.pdf',
            'Statistical_Analysis_Week_3_Assignment_3.pdf',
            'Statistical_Analysis_Week_4_Assignment_4.pdf'
        ]

        docs = []
        course_names = []
        assignment_names = []

        for filename in filenames:
            blob_name = f'{PDF_FOLDER}/{filename}'
            try:
                pdf_content = load_pdf_from_gcs(BUCKET_NAME, blob_name)
                course_name, assignment_name = extract_names(filename)
                if course_name and assignment_name and pdf_content:
                    docs.append(pdf_content)
                    course_names.append(course_name)
                    assignment_names.append(assignment_name)
                    logging.info(f'Successfully Loaded and Cleaned: {filename}')
            except Exception as e:
                logging.error(f'Error Loading {filename}: {e}')

        data = {
            'Assignment Name': assignment_names,
            'Course Name': course_names,
            'Content': docs
        }

        df = pd.DataFrame(data)

        # Assign assignment types
        conditions = [
            df['Course Name'] == 'Introduction to Art History',
            df['Course Name'] == 'Statistical Analysis',  
            df['Course Name'] == 'Marketing Analytics'
        ]
        choices = ['Essay', 'Problem Set', 'Coding']
        df['Assignment Type'] = np.select(conditions, choices, default=np.nan)

        # Process assignments to get difficulty levels
        df = process_assignments(df)

        # Estimate completion time
        df['Time_Completion'] = df.apply(estimate_completion_time, axis=1)

        # Save to pickle file
        file_path = os.path.join(os.getcwd(), 'Time_Completion.pkl')
        logging.info(f"Attempting to save file to: {file_path}")
        df[['Time_Completion']].to_pickle(file_path)
        if os.path.exists(file_path):
            logging.info(f"Time completion data saved to {file_path}")
            logging.info(f"File size: {os.path.getsize(file_path)} bytes")
        else:
            logging.error(f"Failed to save file at {file_path}")

    except Exception as e:
        logging.error(f"An error occurred in the main function: {e}")
        raise

if __name__ == "__main__":
    main()