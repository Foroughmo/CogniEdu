# Log In Page

# Libraries
import streamlit as st
from streamlit_modal import Modal
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
       .login-title {
           text-align: center;
           font-size: 24px;
           font-weight: bold;
           margin-bottom: 20px;
       }
       .login-input {
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
       .remember-forgot-container {
           display: flex;
           justify-content: space-between;
           align-items: center;
           margin-bottom: 15px;
       }
       .forgot-password {
           color: #3B47CE;
           text-decoration: none;
           font-size: 14px;
       }
       .forgot-password:hover {
           text-decoration: underline;
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

# Create the Form Container
st.markdown('<div class="login-container">', unsafe_allow_html=True)

# Logo
logo_path = "cogniedulogo.png"
logo = Image.open(logo_path)
buffered = BytesIO()
logo.save(buffered, format="PNG")
img_str = base64.b64encode(buffered.getvalue()).decode()
st.markdown(f'''
   <div class="logo-container">
       <img src="data:image/png;base64,{img_str}" class="logo">
       <div class="login-title">Log in to your account</div>
   </div>
''', unsafe_allow_html=True)

# Email and Password Fields
email = st.text_input("Email Address", "", key="email", placeholder="Email Address", help="Enter Your Email") 
password = st.text_input("Password", "", key="password", type="password", placeholder="Password", help="Enter Your Password") 

# "Remember Me" Checkbox and Forgot Password Link
st.markdown('<div class="remember-forgot-container">', unsafe_allow_html=True)
remember_me = st.checkbox('Remember Me', key="remember_me")
st.markdown('<a href="#" class="forgot-password">Forgot Password?</a>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

logged_in = False

# Login Button and Logic
if st.button("Log In"):
    if not email or not password:
        st.error("Please enter your login information.")
    else:
        logged_in = True

# Initialize Modal
modal = Modal("Welcome Back! 👋", key="welcome_modal")

# Open Modal After Successful Login
if logged_in:
    modal.open()

if modal.is_open():
    with modal.container():
        st.write("") 

        # Load and Display Image
        image_path = "PopupLoginEd.png"
        image = Image.open(image_path)
        st.image(image, width=250) 
        st.write("Hope you are having a great day! Let's get back on track with your optimized study plan!")
        
        # "Go to Home Page" Button
        if st.button("Go to Home Page"):
            st.switch_page("pages/5_Home.py")

# End of Form Container
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
