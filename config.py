"""
config.py — Centralized configuration and API key management.

Works both locally (reads from .env file) and on Streamlit Cloud
(reads from st.secrets). This dual approach means the same code
runs everywhere without changes.
"""

import os
import streamlit as st
from dotenv import load_dotenv


def get_api_key():
    """
    Retrieve the Google Gemini API key.

    Priority:
      1. Streamlit secrets (for cloud deployment)
      2. .env file (for local development)

    Returns:
        str: The API key

    Raises:
        Stops the Streamlit app with an error if no key is found.
    """
    # Try Streamlit Cloud secrets first
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass

    # Fall back to .env file for local development
    load_dotenv()
    key = os.getenv("GOOGLE_API_KEY")

    if not key:
        st.error("🔑 API key not found! Please set up your API key.")
        st.info(
            "**Local setup:** Create a `.env` file with:\n\n"
            "`GOOGLE_API_KEY=your_key_here`\n\n"
            "Get a free key at: https://aistudio.google.com/apikey"
        )
        st.stop()

    return key
