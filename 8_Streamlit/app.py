# Streamlit
import streamlit as st

# Images
from PIL import Image
import base64
from io import BytesIO

# Page Configuration for App
st.set_page_config(
   page_title="CogniEdu",
   page_icon="🧠",
   layout="wide"
)

# Inline CSS for Custom Styling
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
        .landing-title {
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 0px;
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
        <div class="landing-title">Let's start planning with CogniEdu</div>
    </div>
''', unsafe_allow_html=True)

# Space Between Logo/Subheader and Buttons
st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)

# Button Layout (Using Columns)
col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15, col16, col17, col18, col19 = st.columns([1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1])

# Buttons
with col10:
    if st.button('Register Here', key='registration_button'):
        st.switch_page("pages/1_Registration_Page.py")
    if st.button('Log In Here', key='login_button'):
        st.switch_page("pages/4_LogIn_Page.py")
        
# Space Between Middle and Footer 
st.markdown('<div style="height: 100px;"></div>', unsafe_allow_html=True)

# Footer
st.markdown('''
    <div class="footer">
        <span>ConvoCrafters © 2024</span>
        <span><a href="#">Privacy Policy</a></span>
    </div>
''', unsafe_allow_html=True)