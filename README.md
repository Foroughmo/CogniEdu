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

Every student juggles competing priorities, stemming from school, work and personal life. CogniEdu takes the planning out of these priorities and creates an optimized schedule, tailored according to a user’s preferences, skills and commitments. With CogniEdu, students have a dedicated partner in Ed, a conversational AI chatbot as they navigate through their academic journey. Ed assists with organizing tasks, sending out reminders, answering questions about their calendar and classes, and helping students be more successful with their academics.


# **🧠  Overview of CogniEdu** <a name="Overview"></a>

### Project Diagram <a name="Project-Diagram"></a>
<img width="785" alt="Process Flow" src="https://github.com/user-attachments/assets/619dee8c-ef0a-494f-9755-826eba91cd2e">

### Front-End <a name="Front-End"></a>
<img width="785" alt="Front-End" src="https://github.com/user-attachments/assets/4a3baec3-f092-4bb4-85d3-fffd2568ab9f">


# 🧩 Project Components <a name="Project-Components"></a>

### [📋 Onboarding Experience](https://github.com/Foroughmo/CogniEdu/tree/main/1_API_Integrations) <a name="Onboarding-Experience"></a>
Each user undergoes an onboarding experience that integrates their calendar and academic platform through API calls. During this process, users complete an onboarding questionnaire that Ed uses to learn about their study habits and academic preferences. This information allows Ed to personalize the planning experience according to each user’s needs. 

<h5 align="center"> Onboarding </h5>
<p align="center">
<img width="485" alt="Onboarding" src="https://github.com/user-attachments/assets/881a35f2-f323-4dc0-9331-21047dae264a">
</p>

### [🗄️ Database Management with SQL](https://github.com/Foroughmo/CogniEdu/tree/main/2_SQL_Database) <a name="Database"></a> 
Upon user signup, the onboarding questionnaire populates the users table in MySQL. By integrating with the user’s Google account, the application continuously syncs their Google Calendar event data with the MySQL database. Additionally, assignment information, such as due dates and instructions, is extracted from Google Classroom, transformed, and loaded into the MySQL database. The RAG (Retrieval-Augmented Generation) application then leverages this comprehensive data set to provide personalized and optimized solutions.                                                

<h5 align="center"> Calendar Sync Overview </h5>
<p align="center">
<img width="400" alt="Calendar Sync Overview" src="https://github.com/user-attachments/assets/e418f9e5-2097-46da-8a15-bf9c5570982d">
</p> 

### [🕛 Time Estimations by LLM for Optimizer Algorithm](https://github.com/Foroughmo/CogniEdu/tree/main/3_Time_Estimation_LLM) <a name="Time"></a> 
Text

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
                                           
### [💬 Ed: Our Conversational AI RAG Application Utilizing Langraph](https://github.com/Foroughmo/CogniEdu/tree/main/5_Chatbot) <a name="Ed"></a> 
The chatbot leverages LangGraph's latest features to implement two powerful capabilities. The first is PDF Retrieval-Augmented Generation (RAG), which accesses students' Google Classroom materials to provide efficient, relevant query results. The second feature enables conversational interaction with the student's calendar. These functionalities allow students to seamlessly query their course resources and manage their schedules through natural language conversations.

<h5 align="center"> Ed's Pipeline </h5>
<p align="center">
<img width="700" alt="Ed's Pipeline" src="https://github.com/user-attachments/assets/957b6b9b-9a18-414d-ba60-9caf8d9a9ec4">
</p> 

### [🔔 Proactive Alerts for On Task Management](https://github.com/Foroughmo/CogniEdu/tree/main/6_Email_Notification) <a name="Notifications"></a> 
Managing one's schedule effectively can often prove to be challenging. Ed sends proactive alerts to help users stay on track by extracting calendar data, formatting it into informative emails, automating the process, and securely integrating with external services via API calls and SSL for safe message transmission.

<p align="center">
<img width="200" alt="Screenshot 2024-06-18 at 12 08 32 PM" src="https://github.com/user-attachments/assets/64b48560-ff0e-40f6-9799-2719de11e769">
</p> 

# [📊  Model Evaluation](https://github.com/Foroughmo/CogniEdu/tree/main/7_Model_Evaluation) <a name="Model-Evaluation"></a>                                             
In selection of the model powering Ed, two models were compared, two of Google's Large Language Models were compared, Gemini 1.5 Pro and Gemini 1.5 Flash, using LangChain and AI. 

<img width="1040" alt="Implementation Evaluation Dashboard" src="https://github.com/user-attachments/assets/40f93cc8-04ea-4612-adc3-545ff1e3252a">


# [📱 Streamlit Built User Interface](https://github.com/Foroughmo/CogniEdu/tree/main/8_Streamlit) <a name="Streamlit"></a>                                             
CogniEdu utilizes Streamlit alongside custom CSS to develop an intuitive user interface, ensuring a cohesive user experience. The deployment involved leveraging Cloud Run and NGROK to facilitate seamless accessibility and scalability of the data science application.

### UI/UX Design <a name="UI/UX Design"></a>
#### Home Page <a name="Home Page"></a>
  <p align="left">
  <img width="500" alt="ConvoCraftersLogo.png" src="https://github.com/user-attachments/assets/a4d75f09-b690-4da2-a92a-2194cbd59da5">

*Calendar is set to a day view for focused viewing of the day's schedule with a red line and arrow indicating the current time. Upcoming events show the next 3 events and Ed is located below to direct the student to utilize his AI Chatbot assistance.*

#### Calendar Page <a name="Calendar Page"></a> 
  <p align="left">
  <img width="500" alt="Cal 4" src="https://github.com/user-attachments/assets/8a19a5b7-7bfe-4e1f-abea-ab90f0242319">

*Full week of optimized schedule is generated in week view. Light blue indicates the student's google calendar events, navy indicates Classes from Google Classroom, and pink indicates Ed's optimized study schedules.*


#### Ed, AI Chatbot Page <a name="ED AI Chatbot Page"></a> 
  <p align="left">
  <img width="500" alt="Ed 2" src="https://github.com/user-attachments/assets/ec3c4fe4-14d5-44c2-ab5f-a4cbb709f131">

*Recommended questions are provided and is hidden once the student asks Ed questions*

# **🤔 Technical Challenges** <a name="Technical-Challenges"></a>



# **🤝🏻 CogniEdu's Market Presence and Opportunities** <a name="Market-Presence-and-Opportunities"></a>



# 🚀 Future Work <a name="Future-Work"></a>  

### Possibilities with CogniEdu <a name="Possibilities-with-CogniEdu"></a>
<img width="650" alt="Possibilities with CogniEdu" src="https://github.com/user-attachments/assets/633cf65d-1e75-4efc-ad30-af5f8e34408b">

* Given that LLMs are at the core of CogniEdu's framework, improving various LLM components can enhance the robustness of the time estimation algorithm for the optimizer and make Ed's responses smarter as he learns more about the student.
* CogniEdu's positive impact on students can be expanded by enhancing each component of the project to accommodate more students and allow for long-term planning. This can also involve partnering with the academic industry, parents, and instructors to support students' success in academia.
* To further enhance CogniEdu's impact, a feedback loop can be implemented to track student progress and monitor the success of CogniEdu's recommendations.

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

