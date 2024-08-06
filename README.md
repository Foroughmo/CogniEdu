<h1 align="center"> CogniEdu: AI-Powered Academic Planning for Student Success </h1>

<p align="center">
<img width="300" alt="Screenshot 2024-06-18 at 12 08 32 PM" src="https://github.com/user-attachments/assets/a96051c6-6110-489b-9ff9-5fde6e5402ed">
</p>

CogniEdu is an academic planning tool designed to help students effectively manage their academic schedules alongside other commitments.


# **📑 Table of Contents**

1. [Project Motivation](#Project-Motivation)

2. [Overview of CogniEdu](#Overview) 

3. [Project Components](#Project-Components) 
   * [Onboarding Experience](#Onboarding-Experience)   
   * [Accessing Data through API Integration](#Accessing-Data)     
   * [Database Management with SQL](#Database)
   * [Time Estimations by LLM for Optimizer Algorithm](#Time)   
   * [Optimizing Student’s Study Time with Heuristic Algorithm and Gemini](#Optimizing)
   * [Ed: Our Conversational AI RAG Application Utilizing Langraph](#Ed) 
   * [Proactive Alerts for On Task Management](#Notifications)
      
4. [Model Evaluation](#Model-Evaluation)

5. [Streamlit Built User Interface](#Streamlit)
   
6. [Technical Challenges](#Technical-Challenges)

7. [Competitors and Market Opportunities](#Competitors-and-Market-Opportunities)

8. [Future Work](#Future-Work)
    
9. [Tools Utilized](#Tools-Utilized)

10. [Acknowledgements/About Us](#Acknowledgements)


# **🎯 Project Motivation** <a name="Project-Motivation"></a>

Every student juggles competing priorities, stemming from school, work and personal life. CogniEdu takes the planning out of these priorities and creates an optimized schedule, tailored according to a user’s preferences, skills and commitments. With CogniEdu, students have a dedicated partner in Ed, a conversational AI chatbot as they navigate through their academic journey. Ed assists with organizing tasks, sending out reminders, answering questions about their calendar and classes, and helping students be more successful with their academics.


# **🧠  Overview of CogniEdu** <a name="Overview"></a>
#### UI/UX Design <a name="UI/UX Design"></a>
  <p align="left">
  <img width="350" alt="ConvoCraftersLogo.png" src="https://github.com/user-attachments/assets/a4d75f09-b690-4da2-a92a-2194cbd59da5">
  <img width="350" alt="Cal 4" src="https://github.com/user-attachments/assets/8a19a5b7-7bfe-4e1f-abea-ab90f0242319">

#### Project Diagram <a name="Project Diagram"></a>
[Project Diagram (TBD)]


# 🧩 Project Components <a name="Project-Components"></a>

#### 📋 Onboarding Experience <a name="Onboarding-Experience"></a>
Each user undergoes an onboarding experience that integrates their calendar and academic platform through API calls. During this process, users complete an onboarding questionnaire that Ed uses to learn about their study habits and academic preferences. This information allows Ed to personalize the planning experience according to each user’s needs. 

#### 📥  Accessing Data through API Integration <a name="Accessing-Data"></a>  
Student data accessed via API to access calendar information.                                                

#### 🗄️ Database Management with SQL <a name="Database"></a> 
Upon user signup, the onboarding questionnaire populates the users table in MySQL. By integrating with the user’s Google account, the application continuously syncs their Google Calendar event data with the MySQL database. Additionally, assignment information, such as due dates and instructions, is extracted from Google Classroom, transformed, and loaded into the MySQL database. The RAG (Retrieval-Augmented Generation) application then leverages this comprehensive data set to provide personalized and optimized solutions.                                                

#### 🕛 Time Estimations by LLM for Optimizer Algorithm <a name="Time"></a> 
Text

#### 🗓️ Optimized Scheduling via Heuristics and LLM Prompting <a name="Optimizing"></a> 
Leveraging Gemini’s advanced reasoning capabilities, our application generates a study schedule based on specified study durations (e.g., 2 hours, 4 hours). These durations are processed through a greedy heuristic optimization algorithm, which considers the student's availability and preferences. The algorithm strategically places these study sessions at optimal times throughout the day. The outcome is a comprehensive schedule that seamlessly integrates the student’s personal events with the newly optimized study times.
                                           
#### 💬 Ed: Our Conversational AI RAG Application Utilizing Langraph <a name="Ed"></a> 
The chatbot leverages LangGraph's latest features to implement two powerful capabilities. The first is PDF Retrieval-Augmented Generation (RAG), which accesses students' Google Classroom materials to provide efficient, relevant query results. The second feature enables conversational interaction with the student's calendar. These functionalities allow students to seamlessly query their course resources and manage their schedules through natural language conversations.

#### 🔔 Proactive Alerts for On Task Management <a name="Notifications"></a> 
Managing one's schedule effectively can often prove to be challenging. Ed sends proactive alerts to help users stay on track by extracting calendar data, formatting it into informative emails, automating the process, and securely integrating with external services via API calls and SSL for safe message transmission.


# 📊  Model Evaluation <a name="Model-Evaluation"></a>                                             
In selection of the model powering Ed, two models were compared, two of Google's Large Language Models were compared, Gemini 1.5 Pro and Gemini 1.5 Flash, using LangChain and AI. 

<img width="1040" alt="Implementation Evaluation Dashboard" src="https://github.com/user-attachments/assets/40f93cc8-04ea-4612-adc3-545ff1e3252a">


# 📱 Streamlit Built User Interface <a name="Streamlit"></a>                                             
CogniEdu utilizes Streamlit alongside custom CSS to develop an intuitive user interface, ensuring a cohesive user experience. The deployment involved leveraging Cloud Run and NGROK to facilitate seamless accessibility and scalability of the data science application.

[Images of Streamlit (TBD)]


# **🤔 Technical Challenges** <a name="Technical-Challenges"></a>
[TBD]


# **🤝🏻 Competitors and Market Opportunities** <a name="Competitors-and-Market-Opportunities"></a>
[TBD]


# 🚀 Future Work <a name="Future-Work"></a>  
[TBD]


# **🛠️ Tools Utilized** <a name="Tools-Utilized"></a>

|  | Category | Tool(s) |
|----------|----------|----------|
| 1 | Data Visualization | ![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black) |
| 2 | Database Management | ![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white) | 
| 3 | Design | ![Canva](https://img.shields.io/badge/Canva-%2300C4CC.svg?style=for-the-badge&logo=Canva&logoColor=white) ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) |
| 4 | Frameworks | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white) ![NGROK](https://img.shields.io/badge/ngrok-140648?style=for-the-badge&logo=Ngrok&logoColor=white) ![LangChain](https://img.shields.io/badge/🦜️🔗LangChain-blue) |
| 5 | IDEs | ![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white) | 
| 6 | Languages | ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) |
| 7 | Platforms | ![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white) |
| 8 | Project Management | ![Trello](https://img.shields.io/badge/Trello-%23026AA7.svg?style=for-the-badge&logo=Trello&logoColor=white) |


# 👤 Acknowledgements/About Us <a name="Acknowledgements"></a>                                                
  <p align="left">
  <img width="100" alt="ConvoCraftersLogo.png" src="https://github.com/user-attachments/assets/7e9d4d18-c9d6-4457-b0bf-fa4daa24de77">

  Roselyn Rozario  ([@roselynrozario](https://github.com/roselynrozario))  
  Adela Cho  ([@Adelach0](https://github.com/Adelach0))  
  Michael Meissner  ([@mikemeissner1](https://github.com/mikemeissner1))  
  Forough Mofidi ([@Foroughmo](https://github.com/Foroughmo))  
  Joseph Strickland ([@JCStrick](https://github.com/JCStrick))

