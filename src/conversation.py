from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .intent_router import IntentRouter
from .nlp.pipeline import NLPPipeline
from .response_generator import ResponseGenerator
from .services.tmdb import TMDbClient
from .store.memory import MemoryStore


class ConversationState:
    """
    Holds the state of a single conversation session, including history.
    This object is what gets saved to and loaded from disk.
    """

    def __init__(self):
        self.last_mentioned_movie: Dict[str, Any] | None = None
        self.last_intent: str | None = None
        # A list to store tuples of (user_message, bot_response)
        self.history: list[tuple[str, str]] = []

    def update(self, user_message: str, bot_response: str, intent: str, movie: Dict[str, Any] | None):
        """Updates the state after a turn."""
        self.history.append((user_message, bot_response))
        self.last_intent = intent
        if movie:
            self.last_mentioned_movie = movie

    @classmethod
    def from_dict(cls, data: dict) -> ConversationState:
        """Creates a ConversationState object from a dictionary (loaded from JSON)."""
        state = cls()
        state.last_mentioned_movie = data.get("last_mentioned_movie")
        state.last_intent = data.get("last_intent")
        state.history = [tuple(item) for item in data.get("history", [])]
        return state

    def to_dict(self) -> dict:
        """Converts the ConversationState object to a dictionary for JSON serialization."""
        return {
            "last_mentioned_movie": self.last_mentioned_movie,
            "last_intent": self.last_intent,
            "history": self.history,
        }


class ConversationManager:
    """
    The main orchestrator, now with persistent, file-based session management.
    """

    def __init__(self, tmdb_client: TMDbClient, store: MemoryStore):
        print("Initializing Conversation Manager...")
        self.nlp_pipeline = NLPPipeline()
        self.intent_router = IntentRouter(tmdb_client, store)
        self.response_generator = ResponseGenerator()

        # Define and create the directory for session files
        self.sessions_dir = Path(__file__).parent.parent / "data" / "sessions"
        self.sessions_dir.mkdir(exist_ok=True)

        print(f"Session data will be stored in: {self.sessions_dir}")
        print("Conversation Manager initialized successfully.")

    def _get_session_filepath(self, session_id: str) -> Path:
        """Generates a valid and safe filepath for a session ID."""
        # Sanitize session_id to prevent directory traversal attacks
        safe_filename = "".join(c for c in session_id if c.isalnum() or c in ("-", "_"))
        return self.sessions_dir / f"session_{safe_filename}.json"

    def _load_session(self, session_id: str) -> ConversationState:
        """Loads a session from its JSON file, or returns a new one if not found."""
        filepath = self._get_session_filepath(session_id)
        if filepath.exists():
            print(f"Loading existing session: {session_id}")
            with open(filepath) as f:
                data = json.load(f)
                return ConversationState.from_dict(data)

        print(f"Creating new session: {session_id}")
        return ConversationState()

    def _save_session(self, session_id: str, state: ConversationState):
        """Saves the current session state to its JSON file."""
        filepath = self._get_session_filepath(session_id)
        with open(filepath, "w") as f:
            json.dump(state.to_dict(), f, indent=2)

    def _contextual_preprocessing(self, text: str, state: ConversationState) -> str:
        """Uses conversation state to enrich the user's message."""
        processed_text = text.lower()

        # If the user says "it", "that one", etc., and we have a movie in memory,
        # substitute the pronoun with the actual movie title.
        if state.last_mentioned_movie:
            movie_title = state.last_mentioned_movie.get("title", "")
            pronouns = ["it", "that one", "that movie", "its"]
            # Check if the user's message is short and contains a pronoun
            if any(p == processed_text.strip() for p in pronouns) or any(p in processed_text.split() for p in pronouns):
                if movie_title:
                    print(f"Contextual substitution: Replacing pronoun with '{movie_title}'")
                    # Replace all instances of the pronouns
                    for p in pronouns:
                        processed_text = processed_text.replace(p, movie_title)

        return processed_text

    def handle_message(self, session_id: str, user_message: str) -> str:
        """
        Main entry point with full load/process/save cycle.
        """
        # 1. Load the user's complete conversation history and state
        state = self._load_session(session_id)

        # 2. Pre-process the message using the loaded context
        processed_message = self._contextual_preprocessing(user_message, state)

        # 3. Run NLP and Intent Routing
        nlp_result = self.nlp_pipeline.run(processed_message)
        intent_data = self.intent_router.route(nlp_result)

        # 4. Generate a response
        bot_response = self.response_generator.generate(nlp_result.get("intent"), intent_data)

        # 5. Update the state with the latest turn
        last_movie = None
        if isinstance(intent_data, dict) and "movie" in intent_data:
            last_movie = intent_data["movie"]
        elif isinstance(intent_data, list) and intent_data:
            # For recommendations, we don't set a single "last movie" to avoid ambiguity
            pass

        state.update(user_message, bot_response, nlp_result.get("intent"), last_movie)

        # 6. Save the updated state back to the disk
        self._save_session(session_id, state)

        return bot_response
