# Streamlit
import streamlit as st

# Standard
import pandas as pd
import os
from pathlib import Path

# Images
from PIL import Image
import base64
from io import BytesIO

# CSS for Custom Styling
st.markdown("""
   <style>
       .logo-container {
           display: flex;
           flex-direction: column; 
           align-items: center;
           justify-content: center;
           margin: 50px auto;
           text-align: center; 
       }
        .logo {
            width: 200px;
            height: auto;
            margin-bottom: 10px;
        }           
       .logo-icon {
           font-size: 100px;
           margin-bottom: 0px; 
       }
       .registration-title {
           text-align: center;
           font-size: 24px;
           font-weight: bold;
           margin-bottom: 20px;
       }
       .registration-title {
           text-align: center;
           font-size: 24px;
           font-weight: bold;
           margin-bottom: 20px;
       }
       .registration-input {
           margin-bottom: 15px;
           width: 100%;
           padding: 10px;
           border: 1px solid #ccc;
           border-radius: 5px;
       }
       .button-container {
           display: flex;
           justify-content: center;
           margin-top: 20px;
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
       }
       .button:hover {
           background-color: #2D36A6;
       }
       .terms-checkbox {
           margin-bottom: 15px;
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

# Logo
logo_path = "cogniedulogo.png"
logo = Image.open(logo_path)
buffered = BytesIO()
logo.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()
st.markdown(f'''
   <div class="logo-container">
       <img src="data:image/png;base64,{img_str}" class="logo">
       <div class="registration-title">Connect with Ed and bring your academic dreams to life</div>
   </div>
''', unsafe_allow_html=True)

# Form Fields in Two Columns
email = st.text_input("Email Address", "", key="email", placeholder="Email Address", help="Enter Your Email")  
col1, col2 = st.columns(2)
with col1:
    first_name = st.text_input("First Name", "", key="first_name", placeholder="First Name", help="Enter Your First Name")
with col2:
    last_name = st.text_input("Last Name", "", key="last_name", placeholder="Last Name", help="Enter Your Last Name")

col3, col4 = st.columns(2)
with col3:
    password = st.text_input("Password", "", key="password", type="password", placeholder="Password", help="Enter Your Password")
with col4:
    repeat_password = st.text_input("Repeat Password", "", key="repeat_password", type="password", placeholder="Repeat Password", help="Repeat Your Password")

# Terms and Conditions Checkbox
terms = st.checkbox('I Agree With Terms and Conditions', key="terms")

# Create Account Button
if st.button('Create Account'):
    if not email or not first_name or not last_name or not password or not repeat_password:
        st.error("Please enter the required information.")
    elif password != repeat_password:
        st.error("The passwords do not match.")
    elif not terms:
        st.error("Please review the terms and conditions.")
    else: 
        user_credentials = {
            "name": [first_name + " " + last_name],
            "email": [email]
        }

    user_credentials_df = pd.DataFrame(user_credentials)
    
    # Get the Directory of the Current Script
    script_dir = Path(__file__).resolve().parent

    # Get the Project Root Directory
    project_root = script_dir.parent

    # Define the Path for the user_credentials.pkl File
    user_credentials_path = project_root / 'user_credentials.pkl'   
    
    # Save the DataFrame to a Pickle File
    user_credentials_df.to_pickle(user_credentials_path)

    if st.success("Account created successfully!"):
        st.switch_page("pages/2_Integration_Page.py")

# End of Form Container
st.markdown('</div>', unsafe_allow_html=True)

# End of Logo Container
st.markdown('</div>', unsafe_allow_html=True)

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
