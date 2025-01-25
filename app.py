import streamlit as st
import requests
import json
import os
import uuid


host = os.environ["DATABRICKS_HOST"]

# Set your Databricks serving endpoint URL
DATABRICKS_ENDPOINT = f"https://{host}/serving-endpoints/react_agent/invocations"

# Streamlit UI
st.title("Ticket Chatbot")

# Sidebar for configuration
st.sidebar.header("Configuration")
databricks_token = st.sidebar.text_input("Databricks Token", type="password")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4()) 

st.write(f"Generated thread_id: {st.session_state.thread_id}")

# Chat history initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input box for user query
user_query = st.chat_input("Ask about an incident...")

if user_query:
    # Add user input to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Prepare payload for the Databricks endpoint
    headers = {
        "Authorization": f"Bearer {databricks_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messages": [
            "user", user_query
        ],
        "config":{"thread_id": st.session_state.thread_id}
    }

    # Send request to Databricks LangGraph serving endpoint
    try:
        response = requests.post(DATABRICKS_ENDPOINT, headers=headers, data=json.dumps(payload))
        response_data = response.json()

        # Extract and display response
        bot_response = response_data[0].get("messages", {})[-1].get("content", "I'm unable to process the request.")
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    except Exception as e:
        bot_response = f"Error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(bot_response)
