"""Configuration settings for the Whoop Health Data Comparison Application."""
import os
from datetime import datetime

# Try Streamlit secrets first (for cloud deployment), fall back to .env (for local)
try:
    import streamlit as st
    WHOOP_CLIENT_ID = st.secrets["whoop"]["client_id"]
    WHOOP_CLIENT_SECRET = st.secrets["whoop"]["client_secret"]
    WHOOP_REDIRECT_URI = st.secrets["whoop"]["redirect_uri"]
    FLASK_SECRET_KEY = st.secrets["app"]["secret_key"]
    DATA_START_DATE = st.secrets.get("app", {}).get("data_start_date", "2026-01-01")
    DATA_END_DATE = st.secrets.get("app", {}).get("data_end_date", "2026-02-10")
    CARDIAC_ARREST_DATE = st.secrets.get("events", {}).get("cardiac_arrest_date", "2026-01-11")
    TRIPLE_BYPASS_DATE = st.secrets.get("events", {}).get("triple_bypass_date", "2026-01-19")
except (ImportError, FileNotFoundError, KeyError):
    # Fallback to .env for local development
    from dotenv import load_dotenv
    load_dotenv()
    WHOOP_CLIENT_ID = os.getenv('WHOOP_CLIENT_ID')
    WHOOP_CLIENT_SECRET = os.getenv('WHOOP_CLIENT_SECRET')
    WHOOP_REDIRECT_URI = os.getenv('WHOOP_REDIRECT_URI', 'http://localhost:8501')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DATA_START_DATE = os.getenv('DATA_START_DATE', '2026-01-01')
    DATA_END_DATE = os.getenv('DATA_END_DATE', '2026-02-10')
    CARDIAC_ARREST_DATE = os.getenv('CARDIAC_ARREST_DATE', '2026-01-11')
    TRIPLE_BYPASS_DATE = os.getenv('TRIPLE_BYPASS_DATE', '2026-01-19')
    'read:profile',
    'read:body_measurement',
    'offline'  # For refresh token
]

# Application Settings
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Data Date Range
DATA_START_DATE = os.getenv('DATA_START_DATE', '2026-01-01')
DATA_END_DATE = os.getenv('DATA_END_DATE', '2026-02-10')

# Critical Health Events
CARDIAC_ARREST_DATE = os.getenv('CARDIAC_ARREST_DATE', '2026-01-11')
TRIPLE_BYPASS_DATE = os.getenv('TRIPLE_BYPASS_DATE', '2026-01-19')

CRITICAL_EVENTS = [
    {
        'date': CARDIAC_ARREST_DATE,
        'name': 'Cardiac Arrest',
        'description': 'Collapse while playing tennis. Immediate bystander CPR, Vfib for EMS, ROSC with defib x1. Remarkably neurologically intact & conversational immediately after event; Was not intubated.'
    },
    {
        'date': TRIPLE_BYPASS_DATE,
        'name': 'Triple Bypass Surgery',
        'description': 'Triple bypass surgery performed.'
    }
]

# File Paths
HEALTH_DATA_DIR = 'health-data'
DATA_OUTPUT_DIR = 'data'
TOKENS_DIR = 'tokens'

# Ensure directories exist
os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)
os.makedirs(TOKENS_DIR, exist_ok=True)
