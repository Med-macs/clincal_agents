import streamlit as st
import requests
import json
from typing import List, Dict

# Configure the FastAPI endpoint
API_URL = "http://localhost:8000"

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "triage_result" not in st.session_state:
        st.session_state.triage_result = None
    if "chat_active" not in st.session_state:
        st.session_state.chat_active = False
    if "notes" not in st.session_state:
        st.session_state.notes = []

def display_chat_interface():
    st.title("AI Triage Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Start chat button
    if not st.session_state.chat_active:
        if st.button("Start New Triage Assessment"):
            st.session_state.chat_active = True
            st.session_state.messages = []
            st.session_state.notes = []
            
            # Get initial welcome message
            try:
                response = requests.post(
                    f"{API_URL}/chat-to-triage",
                    json={"message": "", "history": []}
                )
                if response.status_code == 200:
                    bot_response = response.json()
                    st.session_state.messages.append({"role": "assistant", "content": bot_response["response"]})
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.chat_active = False
    
    # Chat input
    if st.session_state.chat_active:
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Call the chat-to-triage endpoint
            try:
                with st.spinner("Processing..."):
                    response = requests.post(
                        f"{API_URL}/chat-to-triage",
                        json={"message": prompt, "history": st.session_state.messages}
                    )
                    
                    if response.status_code == 200:
                        bot_response = response.json()
                        
                        # Add bot's response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": bot_response["response"]})

                        # If the chat is finished, reset the chat state
                        if bot_response.get("finished", False):
                            st.session_state.chat_active = False
                            
                        # Show the response from bot
                        st.write(bot_response['response'])
                        
                    else:
                        st.error("Failed to get response from assistant")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.chat_active = False

def main():
    initialize_session_state()
    display_chat_interface()

if __name__ == "__main__":
    main() 