#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sys
from pathlib import Path
from config.default_config import *


# Configuration file path
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

# Global configuration variable
CONFIG = {}

def get_config():
    """
    Get the current configuration.
    
    Returns:
        dict: The current configuration dictionary.
    """
    global CONFIG
    return CONFIG

def load_config():
    """
    Load configuration from the config file, or create default if not exists.
    
    Returns:
        dict: The loaded configuration.
    """
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                CONFIG = json.load(f)
        except json.JSONDecodeError:
            # If the config file is corrupted, use defaults
            create_default_config()
    else:
        create_default_config()
    
    return CONFIG

def create_default_config():
    """Create a default configuration."""
    global CONFIG
    CONFIG = {
        "GAME_VERSION": DEFAULT_GAME_VERSION,  # Add this line
        "THRESHOLD_HP_LOWER": DEFAULT_THRESHOLD_HP_LOWER,
        "THRESHOLD_HP_UPPER": DEFAULT_THRESHOLD_HP_UPPER,
        "THRESHOLD_MP_LOWER": DEFAULT_THRESHOLD_MP_LOWER,
        "THRESHOLD_MP_UPPER": DEFAULT_THRESHOLD_MP_UPPER,
        "THRESHOLD_ES_LOWER": DEFAULT_THRESHOLD_ES_LOWER,
        "THRESHOLD_ES_UPPER": DEFAULT_THRESHOLD_ES_UPPER,
        "COLOR_TIGHTENING": 0,
        "HEALTH_POTION_DELAY": DEFAULT_HEALTH_POTION_DELAY,
        "MANA_POTION_DELAY": DEFAULT_MANA_POTION_DELAY,
        "TOGGLE_KEY": DEFAULT_TOGGLE_KEY,
        "PAUSE_KEY": DEFAULT_PAUSE_KEY,
        "SINGLE_SCREEN_HOTKEY": DEFAULT_SINGLE_SCREEN_HOTKEY,
        "TARGET_WINDOW_TITLE": WINDOW_TITLE,
        "CHICKEN_ENABLED": DEFAULT_CHICKEN_ENABLED,
        "CHICKEN_THRESHOLD": DEFAULT_CHICKEN_THRESHOLD
    }
    save_config()

def save_config():
    """Save the current configuration to the config file."""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(CONFIG, f, indent=4)
    except Exception as e:
        print(f"Error saving configuration: {e}")

def update_config(key, value):
    """
    Update a configuration value.
    
    Args:
        key (str): Configuration key to update.
        value: New value for the configuration.
    """
    global CONFIG
    CONFIG[key] = value
    save_config()
