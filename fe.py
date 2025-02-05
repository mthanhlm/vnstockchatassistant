import streamlit as st
import requests
from datetime import datetime
import random

# FastAPI endpoint URL
API_URL = "http://localhost:8000/chat"




def initialize_session_state():
    if "threads" not in st.session_state:
        first_thread_name = ""
        st.session_state.threads = {
            first_thread_name: {
                "messages": [],
                "created_at": "",
                "description": ""
            }
        }
        st.session_state.current_thread = first_thread_name



def display_messages():
    messages = st.session_state.threads[st.session_state.current_thread]["messages"]
    for message in messages:
        if message["type"] == "user":
            st.chat_message("user").write(message["message"])
        else:
            st.chat_message("assistant").write(message["message"])

def handle_query(query: str):
    if query.strip():
        # Show user message immediately
        st.chat_message("user").write(query)
        
        # Prepare the request payload
        payload = {
            "query": query,
        }
        
        try:
            # Send POST request to the FastAPI endpoint
            response = requests.post(API_URL, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                bot_response = data.get("response", "No response received.")
                
                # Display bot response immediately
                st.chat_message("assistant").write(bot_response)
                
                # Update session state with messages
                st.session_state.threads[st.session_state.current_thread]["messages"].extend([
                    {"type": "user", "message": query},
                    {"type": "bot", "message": bot_response}
                ])
                
                # Update query parameters
                st.query_params.update(thread=st.session_state.current_thread)
                
                return True
            else:
                st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
                return False
                
        except Exception as e:
            st.error(f"Failed to connect to API: {str(e)}")
            return False
    return False



def main():
    st.title("AI tài chính của bạn")
    
    # Initialize session state
    initialize_session_state()


    # # Display current thread info
    # thread_data = st.session_state.threads[st.session_state.current_thread]
    # st.subheader(f"📜 {st.session_state.current_thread}")
    # if thread_data["description"]:
    #     st.caption(f"ℹ️ {thread_data['description']}")

    # Display messages
    display_messages()

    # Chat input
    if query := st.chat_input("Nhập tin nhắn của bạn..."):
        if handle_query(query):
            st.rerun()

if __name__ == "__main__":
    main()