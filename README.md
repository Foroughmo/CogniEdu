<h1 align="center"> CogniEdu: AI-Powered Academic Planning for Student Success </h1>

<p align="center">
<img width="300" alt="Screenshot 2024-06-18 at 12 08 32 PM" src="https://github.com/user-attachments/assets/a96051c6-6110-489b-9ff9-5fde6e5402ed">
</p>

CogniEdu is an academic planning tool designed to help students effectively manage their academic schedules alongside other commitments.

# **📑 Table of Contents**

1. [Project Motivation](#Project-Motivation)

2. [Overview of CogniEdu](#Overview)
   * [Project Diagram](#Project-Diagram)  
   * [Front-End](#Front-End)  

4. [Project Components](#Project-Components) 
   * [Onboarding Experience](#Onboarding-Experience)      
   * [Database Management with SQL](#Database)
   * [Time Estimations by LLM for Optimizer Algorithm](#Time)   
   * [Optimizing Student’s Study Time with Heuristic Algorithm and Gemini](#Optimizing)
   * [Ed: Our Conversational AI RAG Application Utilizing Langraph](#Ed) 
   * [Proactive Alerts for On Task Management](#Notifications)
      
5. [Model Evaluation](#Model-Evaluation)

6. [Streamlit Built User Interface](#Streamlit)
   
7. [Technical Challenges](#Technical-Challenges)

8. [CogniEdu's Market Presence and Opportunities](#Market-Presence-and-Opportunities)

9. [Future Work](#Future-Work)
   * [Next Steps](#Next-Steps)    
    
11. [Tools Utilized](#Tools-Utilized)

12. [Acknowledgements/About Us](#Acknowledgements)


# **🎯 Project Motivation** <a name="Project-Motivation"></a>
<p align="center">
<img width="300" alt="Screenshot 2024-08-06 at 5 23 52 PM" src="https://github.com/user-attachments/assets/d0c417e2-8c76-48de-a637-a6fc32184ce5">
</p>
We begin our story with our hypothetical student Nick Ramen. Nick Ramen is a college student dealing with a situation a lot of us can empathize to: he wants to have the best college experience possible, all the while maintaining good grades, a healthy sleep schedule, and a social life. However, it comes to a point where he has overcommited and becomes overwhelmed, leading to a decline in grades and is lost as to how to navigate his academic decline.

Like Nick, approximtely 86% of college students face challenges in effectively managing their time, leading to procrastination, stress, and a decline in academic performance.

Here is how CogniEdu can help:

CogniEdu takes the planning out of these priorities and creates an optimized schedule, tailored according to the student’s preferences, skills and commitments. With CogniEdu, students have a dedicated AI Chatbot Assistant in Ed, a conversational AI chatbot as they navigate through their academic journey. Ed assists with organizing tasks, sending out email reminders, answering questions about their calendar and classes, and helping students be more successful with their academics.


# **🧠  Overview of CogniEdu** <a name="Overview"></a>

### Project Diagram <a name="Project-Diagram"></a>
<img width="785" alt="Process Flow" src="https://github.com/user-attachments/assets/619dee8c-ef0a-494f-9755-826eba91cd2e">

### Front-End <a name="Front-End"></a>
<img width="785" alt="Front-End" src="https://github.com/user-attachments/assets/4a3baec3-f092-4bb4-85d3-fffd2568ab9f">


# 🧩 Project Components <a name="Project-Components"></a>

### [📋 Onboarding Experience](https://github.com/Foroughmo/CogniEdu/tree/main/1_API_Integrations) <a name="Onboarding-Experience"></a>
Each student undergoes an onboarding experience that integrates their calendar and academic platform through API calls. During this process, users complete an onboarding questionnaire that Ed uses to learn about their study habits and academic preferences. This information allows Ed to personalize the planning experience according to each student’s needs. 

<h5 align="center"> Onboarding </h5>
<p align="center">
<img width="485" alt="Onboarding" src="https://github.com/user-attachments/assets/881a35f2-f323-4dc0-9331-21047dae264a">
</p>

### [🗄️ Database Management with SQL](https://github.com/Foroughmo/CogniEdu/tree/main/2_SQL_Database) <a name="Database"></a> 
Upon user signup, the onboarding questionnaire populates the student's table in MySQL. By integrating with the student's Google account, the application continuously syncs their Google Calendar event data with the MySQL database. 

<h5 align="center"> Calendar Sync Overview </h5>
<p align="center">
<img width="400" alt="Calendar Sync Overview" src="https://github.com/user-attachments/assets/e418f9e5-2097-46da-8a15-bf9c5570982d">
</p> 

The calendar sync involves an initial import of the student's full calendar, while the continuous sync regularly updates every X number of minutes. The sync also stores events and handles NEW, UPDATED, and DELETED items chunked and embedded for future retrieval, per a logic. 

<h5 align="center"> Calendar Sync Logic </h5>

<p align="center">
<img width="400" alt="Calendar Sync Overview" src="https://github.com/user-attachments/assets/69833ef1-ab3f-4bb3-8258-1be97508510e">
</p> 

The MySQL database also houses assignment information, such as due dates and instructions, which is extracted from Google Classroom, and then transformed, before being loaded into said database. The RAG (Retrieval-Augmented Generation) application then leverages this comprehensive data set to provide personalized and optimized solutions.                                                
### [🕛 Time Estimations by LLM for Optimizer Algorithm](https://github.com/Foroughmo/CogniEdu/tree/main/3_Time_Estimation_LLM) <a name="Time"></a> 
### Time Estimation

The time estimation algorithm serves as the preliminary phase in preparing data for the optimizer. This process is executed in two steps utilizing Large Language Models (LLMs) through prompt engineering.

**Step 1: Assignment Difficulty Level**
The LLM evaluates the difficulty level of each assignment based on its content. Assignments are then categorized on a scale of easy, medium, or hard. These qualitative scales are converted into numerical values and stored accordingly.

**Step 2: Time Estimation**
Based on the assignment's content and its assigned difficulty level, the LLM estimates the time required to complete the assignment. Once the time estimation is determined, it is provided to the optimizer to create an optimized study plan.

<h5 align="center"> Time Estimation LLM </h5>
<p align="center">
<img width="700" alt="Time Estimation LLM" src="https://github.com/user-attachments/assets/15c2e554-d316-45a9-ab1c-8f2e4fac1416">
</p> 

### [🗓️ Optimized Scheduling via Heuristics and LLM Prompting](https://github.com/Foroughmo/CogniEdu/tree/main/4_Optimizer) <a name="Optimizing"></a> 
Leveraging Gemini’s advanced reasoning capabilities, our application generates a study schedule based on specified study durations (e.g., 2 hours, 4 hours). These durations are processed through a greedy heuristic optimization algorithm, which considers the student's availability and preferences. The algorithm strategically places these study sessions at optimal times throughout the day. The outcome is a comprehensive schedule that seamlessly integrates the student’s personal events with the newly optimized study times.

<h5 align="center"> Optimizer Algorithm </h5>
<p align="center">
<img width="700" alt="Optimizer" src="https://github.com/user-attachments/assets/fc7f1e59-e9be-41ea-ac6c-8cdfbc0a3014">
</p> 
                                           
### [💬 Ed: Our Conversational AI Agent](https://github.com/Foroughmo/CogniEdu/tree/main/5_Chatbot) <a name="Ed"></a> 
CogniEdu's chatbot, Ed, is built on the ReAct (Reasoning and Acting) paradigm, leveraging LangGraph to create a dynamic, multi-tool agent. The system employs three key capabilities:

1. PDF Retrieval-Augmented Generation (RAG): This tool accesses and queries students' Google Classroom materials, providing efficient and relevant information from course documents.

2. Calendar Interaction: A dedicated tool enables conversational access to the student's personal and academic calendar, allowing for schedule queries and management.

3. Web Search Integration: Utilizing Tavily, the agent can fetch external resources to supplement course materials and provide additional learning support.

<h5 align="center"> ReAct Framework </h5>
<p align="center">
<img width="267" alt="ReAct Framework" src="https://github.com/user-attachments/assets/4fb2feec-ee06-4b08-adfd-99872d1d76db">
</p> 

Ed processes user queries through an iterative cycle of reasoning (using a Large Language Model) and acting (employing these specialized tools). This ReAct architecture allows the agent to break down complex queries, determine the most appropriate tools to use, and synthesize information from multiple sources. By integrating these functionalities, students can seamlessly query their course resources, manage their schedules, and access relevant external content through natural language conversations. The LangGraph framework enables Ed to maintain context and make informed decisions throughout these interactions, enhancing the overall user experience and academic support.

<h5 align="center"> Ed's Pipeline </h5>
<p align="center">
<img width="700" alt="Ed's Pipeline" src="https://github.com/user-attachments/assets/957b6b9b-9a18-414d-ba60-9caf8d9a9ec4">
</p> 

### [🔔 Proactive Alerts for On Task Management](https://github.com/Foroughmo/CogniEdu/tree/main/6_Email_Notification) <a name="Notifications"></a> 
Managing one's schedule effectively can often prove to be challenging. Ed sends email notifications with optimized calendar information to help users stay on track by extracting calendar data, formatting it into informative emails, and automating the process. Emails are securely sent by integrating with external email servers via Simple Mail Transfer Protocol (SMTP) and Secure Sockets Layer (SSL) for safe message transmission.

<p align="center">
<img width="200" alt="Screenshot 2024-06-18 at 12 08 32 PM" src="https://github.com/user-attachments/assets/64b48560-ff0e-40f6-9799-2719de11e769">
</p> 

# [📊  Model Evaluation](https://github.com/Foroughmo/CogniEdu/tree/main/7_Model_Evaluation) <a name="Model-Evaluation"></a>                                             
In selection of the model powering Ed, two models were compared, two of Google's Large Language Models were compared, Gemini 1.5 Pro and Gemini 1.5 Flash, using LangChain and AI. 

<img width="1040" alt="Implementation Evaluation Dashboard" src="https://github.com/user-attachments/assets/40f93cc8-04ea-4612-adc3-545ff1e3252a">


# [📱 Streamlit Built User Interface](https://github.com/Foroughmo/CogniEdu/tree/main/8_Streamlit) <a name="Streamlit"></a>                                             
CogniEdu utilizes Streamlit alongside custom CSS to develop an intuitive user interface, ensuring a cohesive user experience. The deployment involved leveraging Cloud Run and NGROK to facilitate seamless accessibility and scalability of the data science application.

### UI/UX Design <a name="UI/UX Design"></a>
#### Landing Page <a name="Landing Page"></a>
<p align="left">
<img width="600" alt="Screenshot 2024-08-06 at 5 33 39 PM" src="https://github.com/user-attachments/assets/8a641e3c-eef9-4013-9361-4b0c196f917d">

The Landing Page directs new students to "Register Here" and returning students to "Log in Here".

#### New Student Registeration <a name="New Student Registration"></a>
##### Register Here Page <a name="Register Here Page"></a>

New students are directed to input their email address, full name, and password to create a new account.

##### Integration Page <a name="Integration Page"></a>

Here is where the integration happens. New students integrate their Google Classroom and Google Calendar platforms.

##### Ed Says Hi! <a name="Ed Says Hi!"></a>

New students are shown a pop up of Ed introducing himself as your personal AI Chatbot assistant.

##### Questionnaire Page <a name="Questionnaire Page"></a>

Ed directs you to tailor your experience with CogniEdu! This is where you provide your preferences in studying time, whether you are a morning person or not, preferred break times, etc.

#### Returning Student Log-in <a name="Returning Student Log-in"></a>
##### Log-in Page <a name="Log-in Page"></a>

Returning students are directed to input their email address and password to log back into their account

##### Welcome Back! <a name="Welcome Back!"></a>

Returning students are shown a pop up welcoming you back to CogniEdu

#### Home Page <a name="Home Page"></a>
  <p align="left">
  <img width="600" alt="ConvoCraftersLogo.png" src="https://github.com/user-attachments/assets/a4d75f09-b690-4da2-a92a-2194cbd59da5">

The Home Page includes the optimized calendar, a dedicated section for Ed, the student's friendly AI chatbot, and a view of the upcoming events. 
* The calendar is set to a day view for focused viewing of the day's schedule with a red line and arrow indicating the current time.
* Upcoming events show the next 3 events, as well as relevant details pertaining to them.
* Ed is located below to direct the student to utilize his AI Chatbot assistance.*

#### Calendar Page <a name="Calendar Page"></a> 
  <p align="left">
  <img width="600" alt="Cal 4" src="https://github.com/user-attachments/assets/8a19a5b7-7bfe-4e1f-abea-ab90f0242319">

The Calendar Page is the student's dedicated space to view a full week's optimized schedule. The event colors represent their source:
* Light Blue: Student's Google Calendar Events
* Navy: Classes from Google Classroom
* Pink: Ed's Optimizer Events


#### Ed, AI Chatbot Page <a name="ED AI Chatbot Page"></a> 
  <p align="left">
  <img width="600" alt="Ed 2" src="https://github.com/user-attachments/assets/ec3c4fe4-14d5-44c2-ab5f-a4cbb709f131">

The Ed, AI Chatbot Page allows for conversation pertaining to the student's course materials and their calendar. Recommended questions are provided to assist the student in making queries to Ed.

# **🤔 Technical Challenges** <a name="Technical-Challenges"></a>
#### 1. AI Hallucinations: 
AI systems can produce hallucinations, generation misleading or incorrect information. In order to reduce hallucinations, we provided specific prompts, clear constraints, and relevant data sources to curate Ed's responses. 
#### 2. Privacy Concerns: 
Students provide student data from their emails, Google Calendar, and Google Classroom that need safeguarding.
#### 3. Limited Training Data: 
Limited data given reliance on student data. We utilized generative AI (Chatgpt) to create synthetic data to test out our chatbot.
#### 4. Agentic System Run Time: 
Increase Complexity affects run time.
#### 5. Agentic System Tool Selection: 
Implementing the correct logic for the agent to chose the right tool based on context.
#### 6. LLM Inconsistency: 
LLM responses can be random or inconsistent.


# **🤝🏻 CogniEdu's Market Presence and Opportunities** <a name="Market-Presence-and-Opportunities"></a>
Cogniedu addresses a significant market need for academic planning and organization tools that integrate seamlessly with existing technologies like Google Calendar and Google Classroom. With the increasing complexity of student schedules and the growing reliance on academic digital tools, CogniEdu is well-positioned for the educational technology market. We hope to enhance and expand our platform by collaborating with academic institutions and universities and by expanding integration to other popular platforms like Outlook Calendar and Canvas so that CogniEdu is a pre-installed feature for ease of access for students. 


# 🚀 Future Work <a name="Future-Work"></a>  

### Possibilities with CogniEdu <a name="Possibilities-with-CogniEdu"></a>

#### Feedback Loop​​
* Feedback Loop to Track Student’s Progress and Success of CogniEdu Recommendations​

#### Improving LLMs
* With the Permission of Students, Their Data Can Be Used for the LLMs to Return Smarter, User-Specific Responses​

#### Partnerships​
* Partner With Teachers, Parents, and Universities to Help Students on a Broader Scale​

#### Robust Time Estimation
* More Robust Time Estimation Algorithm for Optimizer​

#### Scale Features
* Each Component Can Be Scaled to Accommodate More Students and Plan for Longer Time-Periods​​

### Next Steps <a name="Next-Steps"></a>
<img width="650" alt="Next Steps" src="https://github.com/user-attachments/assets/2314411f-1da3-4179-a681-36ea29817c71">



# **🛠️ Tools Utilized** <a name="Tools-Utilized"></a>

|  | Category | Tool(s) |
|----------|----------|----------|
| 1 | Data Visualization | ![Power Bi](https://img.shields.io/badge/power_bi-F2C811?style=for-the-badge&logo=powerbi&logoColor=black) |
| 2 | Database Management | ![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=for-the-badge&logo=mysql&logoColor=white) | 
| 3 | Design | ![Canva](https://img.shields.io/badge/Canva-%2300C4CC.svg?style=for-the-badge&logo=Canva&logoColor=white) ![Figma](https://img.shields.io/badge/figma-%23F24E1E.svg?style=for-the-badge&logo=figma&logoColor=white) <img width="97" alt="Screenshot 2024-08-06 at 2 21 06 PM" src="https://github.com/user-attachments/assets/28e7d4cc-db4b-4016-bc78-a7c73aa13f42"> <img width="85" alt="Screenshot 2024-08-06 at 2 34 32 PM" src="https://github.com/user-attachments/assets/fa685bf1-901c-4dec-b78c-a1afe60d2ecb">|
| 4 | Frameworks | ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white) ![NGROK](https://img.shields.io/badge/ngrok-140648?style=for-the-badge&logo=Ngrok&logoColor=white) <img width="110" alt="Screenshot 2024-08-06 at 2 29 58 PM" src="https://github.com/user-attachments/assets/3d76bfd5-84a6-482f-ba87-4c87ef0923b7"> |
| 5 | IDEs | ![Jupyter Notebook](https://img.shields.io/badge/jupyter-%23FA0F00.svg?style=for-the-badge&logo=jupyter&logoColor=white) | 
| 6 | Languages | ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) <img width="76" alt="Screenshot 2024-08-06 at 2 52 09 PM" src="https://github.com/user-attachments/assets/d24a382e-b3c9-4976-8b46-2d6d37e5718d">|
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

