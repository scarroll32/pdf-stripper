#!/usr/bin/env python3
"""
Setup module for ensuring virtual environment and dependencies
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

from .config import BASE_DIR, VENV_DIR

def ensure_venv_and_dependencies():
    """Ensure virtual environment exists and dependencies are installed"""
    
    # Check if we're already in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Virtual environment is active")
        return
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists(VENV_DIR):
        print("Creating virtual environment...")
        try:
            venv.create(VENV_DIR, with_pip=True)
            print("Virtual environment created successfully")
        except Exception as e:
            print(f"Error creating virtual environment: {e}")
            sys.exit(1)
    
    # Check if we need to activate the virtual environment
    if not os.path.exists(os.path.join(VENV_DIR, 'bin', 'python')):
        print("Virtual environment appears to be corrupted. Please delete the 'venv' folder and try again.")
        sys.exit(1)
    
    # Install dependencies
    requirements_path = os.path.join(BASE_DIR, 'requirements.txt')
    if os.path.exists(requirements_path):
        print("Installing dependencies...")
        try:
            pip_path = os.path.join(VENV_DIR, 'bin', 'pip')
            subprocess.run([pip_path, 'install', '-r', requirements_path], 
                         check=True, capture_output=True, text=True)
            print("Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"Error installing dependencies: {e}")
            print(f"Error output: {e.stderr}")
            sys.exit(1)
    else:
        print("Warning: requirements.txt not found") 