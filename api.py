from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
import os
from typing_extensions import TypedDict

# Add the src directory to the path to import ChatBot
# current_path = os.getcwd()
# src_path = os.path.join(current_path, "src")
# sys.path.append(src_path)

# Import the ChatBot class
from chatbot import ChatBot

# Initialize FastAPI app
app = FastAPI()

# Initialize ChatBot instance
chatbot = ChatBot()

# Define request and response models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(TypedDict):
    response: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Endpoint to interact with the chatbot."""
    try:
        # Process the query using the chatbot
        output = chatbot.process_query(request.query)
        print("Chatbot is using:", output['query_type'])
        print("Chatbot:", output['response'])
        return ChatResponse(response=output['response'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
