# Onboarding_Page

# Libraries
import streamlit as st
import pandas as pd
import subprocess
import os
import sys
import datetime
from PIL import Image
import base64
from io import BytesIO

# Page Configuration
st.set_page_config(layout="wide")

# Inline CSS for Custom Styling
st.markdown("""
   <style>
       body {
           font-family: Arial, sans-serif;
       }
       .logo-container {
           display: flex;
           flex-direction: column;
           align-items: center;
           justify-content: center;
           margin: 50px auto;
           text-align: center;
       }
       .logo {
           width: 700px;
           height: auto;
           margin-bottom: 10px;
       }   
       .logo-icon {
           font-size: 100px;
           margin-bottom: 10px;
       }
       .onboarding-title {
           text-align: center;
           font-size: 24px;
           font-weight: bold;
           margin-bottom: 20px;
       }
       .button-container {
           display: flex;
           justify-content: flex-end;
           margin-top: 20px;
           margin-right: 50px;
       }
       .button {
           background-color: #3B47CE;
           color: white;
           border: none;
           padding: 10px 20px;
           text-align: center;
           font-size: 16px;
           cursor: pointer;
           border-radius: 5px;
           margin-right: 10px;
       }
       .button:hover {
           background-color: #2D36A6;
       }
       .footer {
           display: flex;
           justify-content: space-between;
           font-size: 12px;
           color: #555;
           margin-top: 50px;
           padding: 0 50px;
       }
       .footer hr {
           border: none;
           border-top: 1px solid #ccc;
           margin-bottom: 10px;
       }
       .question {
           color: #5271FF;
           font-weight: bold;
       }
   </style>
""", unsafe_allow_html=True)

# Custom CSS for Buttons
custom_css = """
    <style>
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
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Load and Display Image
uploaded_image_path = 'onboarding.png'
logo = Image.open(uploaded_image_path)
buffered = BytesIO()
logo.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()
st.markdown(f'''
   <div class="logo-container">
       <img src="data:image/png;base64,{img_str}" class="logo">
   </div>
''', unsafe_allow_html=True)

# Space Between Header and Questions
st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)

# Question 1: Preferred Start Time
st.markdown('<span class="question">**1. What is your preferred time to start studying?**</span>', unsafe_allow_html=True)
start_time = st.time_input("Enter your preferred start time:", value=datetime.time(0, 0))

# Question 2: Preferred End Time
st.markdown('<span class="question">**2. What is your preferred time to end studying?**</span>', unsafe_allow_html=True)
end_time = st.time_input("Enter your preferred end time:", value=datetime.time(23, 0))

# Check if Start Time Is Not Greater Than or Equal to End Time
if start_time >= end_time:
    st.error("Preferred start time must be earlier than the end time.")

# Question 3: Morning Person
st.markdown('<span class="question">**3. Are you a morning person?**</span>', unsafe_allow_html=True)
morning_person = st.radio("Select True or False:", ("True", "False"))

# Question 4: Break Duration
st.markdown('<span class="question">**4. How long do you want your breaks to be between studying sessions?**</span>', unsafe_allow_html=True)
break_duration = st.selectbox("Select your break duration (in minutes):", (15, 30, 45, 60))

# Convert Break Duration to Decimal
break_duration_decimal = break_duration / 60
st.write(f"Your break duration in decimal hours: {break_duration_decimal:.2f}")

# Question 5: Courses
st.markdown('<span class="question">**5. Rank the course(s) you are taking this semester/quarter in order of highest priority to lowest priority. **</span>', unsafe_allow_html=True)
courses = st.text_area("Enter the course names, separated by commas:")

# Question 6: Semester/Quarter Start Date
st.markdown('<span class="question">**6. When does your semester/quarter start?**</span>', unsafe_allow_html=True)
semester_start = st.date_input("Select the start date:")

# Question 7: Semester/Quarter End Date
st.markdown('<span class="question">**7. When does your semester/quarter end?**</span>', unsafe_allow_html=True)
semester_end = st.date_input("Select the end date:")

# Convert Time to Decimal Hours
def time_to_decimal(t):
    return t.hour + t.minute / 60

start_time_decimal = time_to_decimal(start_time)
end_time_decimal = time_to_decimal(end_time)

# Spacer
st.markdown('<div style="height: 25px;"></div>', unsafe_allow_html=True)

# Display Summary
st.markdown("### Summary of Your Preferences")
st.write(f"**Preferred Start Time:** {start_time}")
st.write(f"**Preferred End Time:** {end_time}")
st.write(f"**Morning Person:** {morning_person}")
st.write(f"**Break Duration (minutes):** {break_duration}")
st.write(f"**Courses:** {courses}")
st.write(f"**Semester Start Date:** {semester_start}")
st.write(f"**Semester End Date:** {semester_end}")
st.write("")

if st.button("Finish"):
    if start_time >= end_time:
        st.error("Please adjust the start and end times so that the start time is earlier than the end time.")
    else:
        user_data = {
            "start_time": [start_time_decimal],
            "end_time": [end_time_decimal],
            "morning_person": [morning_person],
            "break_duration": [break_duration / 60], # Store in Hours
            "courses": [courses],
            "semester_start": [semester_start],
            "semester_end": [semester_end]
        }

        user_preferences_df = pd.DataFrame(user_data)

        # Save the DataFrame to a Pickle File
        user_preferences_df.to_pickle('user_preferences.pkl')
        
        # Run Time Estimation
        st.text("Estimating assignment completion times...")
        
        # Locate and Run the time_estimation.py Script
        script_path = os.path.join(os.path.dirname(__file__), '..', 'utils', 'Time_Estimation.py')
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                check=True
            )
            st.text(result.stdout)
            if result.stderr:
                st.error(f"Error in time estimation: {result.stderr}")
        except subprocess.CalledProcessError as e:
            st.error(f"Error running time estimation: {e}")
            st.error(f"Error output: {e.stderr}")

        # Check if the File Was Created
        if os.path.exists('Time_Completion.pkl'):
            st.success("Time estimations complete!")
        else:
            st.error("Time estimation file was not created.")

        # Navigate to Home Page
        st.success("Preferences saved! Assignment time estimated! Proceeding to next step.")
        st.switch_page("pages/5_Home.py")

# Footer
st.markdown('''
   <div class="footer">
       <span>ConvoCrafters © 2024</span>
       <span><a href="#">Privacy Policy</a></span>
   </div>
''', unsafe_allow_html=True)

# Run the Streamlit App
if __name__ == "__main__":
    pass
