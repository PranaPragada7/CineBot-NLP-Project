from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .conversation import ConversationManager
from .services.tmdb import TMDbClient
from .store.memory import MemoryStore

# Load environment variables from the root .env file
dotenv_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

# --- App Setup ---
app = FastAPI(title="CineBot API", description="API for the CineBot conversational AI.", version="1.0.0")


# --- Pydantic Models ---
class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


# --- Global Singleton Instances ---
tmdb_api_key = os.getenv("TMDB_API_KEY")
if not tmdb_api_key:
    raise ValueError("TMDB_API_KEY environment variable not set.")

tmdb_client = TMDbClient(api_key=tmdb_api_key)
vector_store = MemoryStore(tmdb_client=tmdb_client)
# Build the vector store on startup
vector_store.build()

# The single, powerful ConversationManager instance
conversation_manager = ConversationManager(tmdb_client=tmdb_client, store=vector_store)


# --- API Endpoints ---
@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Main endpoint to interact with the chatbot.
    Manages conversation state via session_id.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if not request.session_id:
        raise HTTPException(status_code=400, detail="Session ID cannot be empty.")

    try:
        bot_response = conversation_manager.handle_message(session_id=request.session_id, user_message=request.message)
        return ChatResponse(response=bot_response)
    except Exception as e:
        print(f"An error occurred: {e}")
        # In a real app, you'd have more specific error handling
        raise HTTPException(status_code=500, detail="An internal error occurred.")


@app.get("/health")
def health_check():
    return {"status": "ok"}
