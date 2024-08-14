import streamlit as sl
from utils.cloud_services import cloudServices
from utils.dataManager import DataManager

rag_results = cloudServices().rag_result
datamanager = DataManager("./assets/dataset/taxdata.jsonl", "./assets/embeddings/embedtaxdata.jsonl")

sl.title("Chat Bot")


# Button in case the user wants to reset anything
resetButton = sl.button(label="Reset", key="resetButton", on_click=lambda : sl.session_state.clear())

# Chatbot code

# Initial chatbot greeting
with sl.chat_message(name="assistant", avatar="💸"):
    sl.markdown("**Tax Assistant**  \nWsg I'm a tax bot. Write yo problem down and I'll help. Alternatively, you could also just ask me a question about something tax related. ")

# Create chat history in order to preserve the chat conversation and make a contextual tax chatbot

# Checks if the messages element is present in the session - this in order for the chatbot to keep remembering the context of the conversation and so the user can see their previous messages too. 
if "messages" not in sl.session_state:
    # If not, create that part inside the session state
    sl.session_state.messages = []
else:
    # Reload any previous messages that were sent(can clear with button)
    for message in sl.session_state.messages:
        if message["role"] == "assistant":
            with sl.chat_message(name="assistant", avatar="💸"):
                sl.markdown(f"**Tax Assistant**  \n{message['content']}")
        elif message["role"] == "user":
            # Integrate user query show only
            # Query starts at index 12
            prevquery = message["content"].split("\n")[0][12:]
            with sl.chat_message(name="user", avatar="🤓"):
                sl.markdown(f"**User:**  \n{prevquery}")


# Create the chat_input element
query = sl.chat_input()
# If the user makes a message
if query != None:
    # Show the user's message in the "chat-style" for the user to see
    with sl.chat_message("user", avatar="🤓"):
        sl.markdown(f"**User**  \n{query}")

    # Add the message to the chat history file
    chatHistory = sl.session_state.messages
    
    # Display the generated message to the user
    with sl.chat_message(name="assistant", avatar="💸"):
        # let the user know that this is happening
        sl.markdown(f"**Tax Assistant**  \nGenerating answer...")
        # Send it into the RAG - will send the answer and the updated chatHistory
        chatHistory = rag_results(query, datamanager.searchData(query, 10), chatHistory)
        # Once finished getting chatHistory, the program will save it to the session_state and reload the page
        # Then, the new message will appear without the "generating answer" part

        

    # Update the chat history in the session
    sl.session_state.messages = chatHistory
    print(sl.session_state.messages)
    sl.rerun()

