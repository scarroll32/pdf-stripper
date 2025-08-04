import os
import json

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Go up one level from app/ folder
VENV_DIR = os.path.join(BASE_DIR, "venv")
MEDIA_DIR = os.path.join(BASE_DIR, "media")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "pdf-stripper.log")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")

# Default settings
DEFAULT_OUTPUT_FORMAT = "txt"
SUPPORTED_FORMATS = ["txt", "md"]

def load_settings():
    """Load settings from settings file, fallback to defaults"""
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                return settings
    except Exception:
        pass
    return {"output_format": DEFAULT_OUTPUT_FORMAT}

def save_settings(settings):
    """Save settings to settings file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False

# Create necessary directories
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True) 