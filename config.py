import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

SUPERVISOR_MODEL = os.getenv("SUPERVISOR_MODEL", "gemini-2.5-flash")
RAG_MODEL = os.getenv("RAG_MODEL", "gemini-2.5-flash")
ACTION_MODEL = os.getenv("ACTION_MODEL", "gemini-2.5-flash")
POLICY_MODEL = os.getenv("POLICY_MODEL", "gemini-2.5-pro")

AGENT_SEARCH_ENGINE_ID = os.getenv("AGENT_SEARCH_ENGINE_ID", "")
RAG_CORPUS_NAME = os.getenv("RAG_CORPUS_NAME", "")

APP_NAME = os.getenv("APP_NAME", "enterprise-multi-agent")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
