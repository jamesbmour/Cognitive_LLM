import os 
# import chromadb
#
# from chromadb.config import Settings
# CHROMA_SETTINGS = Settings(
#         chroma_db_impl='duckdb+parquet',
#         persist_directory='db',
#         anonymized_telemetry=False
# )

OPENROUTER_REFERRER = "https://github.com/alexanderatallah/openrouter-streamlit"
# OPENROUTER_BASE = "http://localhost:3000"
OPENROUTER_BASE = "https://openrouter.ai"
OPENROUTER_API_BASE = f"{OPENROUTER_BASE}/api/v1"
OPENROUTER_DEFAULT_CHAT_MODEL = "mistralai/mistral-7b-instruct:free"
OPENROUTER_DEFAULT_INSTRUCT_MODEL = "mistralai/mistral-7b-instruct:free"
# Default embedding model
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_MODELS = ['text-embedding-3-small', 'text-embedding-3-large']