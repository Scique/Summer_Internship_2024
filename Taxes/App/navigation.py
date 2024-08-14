import streamlit as sl

# Page 1 - Chatbot page
chatbotPage = sl.Page("./Chat_Bot.py", title="Chat Bot", icon="🤖")

# Page 2 - Search Page
searchPage = sl.Page("./Search_Engine.py", title="Search Tax Database", icon="🔍")

# Page 3 - Data Visualization
datavisualPage = sl.Page("./Data_Visualization.py", title="Data Visualization", icon="📉")

page = sl.navigation([chatbotPage, searchPage, datavisualPage])
    
page.run()