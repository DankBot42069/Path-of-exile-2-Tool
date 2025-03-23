#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Add these lines at the top with other constants
GAME_VERSION_GGG = "GGG"
GAME_VERSION_STEAM = "Steam"

# Modify the process name to include both options
PROCESS_NAMES = {
    GAME_VERSION_GGG: "PathOfExile.exe",
    GAME_VERSION_STEAM: "PathOfExileSteam.exe"
}
# Default to Steam version as in original code
DEFAULT_GAME_VERSION = GAME_VERSION_STEAM
PROCESS_NAME = PROCESS_NAMES[DEFAULT_GAME_VERSION]
WINDOW_TITLE = PROCESS_NAME
# Memory offsets configuration
STATS_BASE_ADDRESS_OFFSET = 0x03BB2158  # "PathOfExileSteam.exe" + 0x03BB2158

# Offsets for player stats
OFFSETS_MAX_HP  = [0x70, 0x0, 0x80, 0x2B0, 0x1DC]
OFFSETS_LIVE_HP = [0x70, 0x0, 0x80, 0x2B0, 0x1E0]
OFFSETS_MAX_MP  = [0x70, 0x0, 0x80, 0x2B0, 0x22C]
OFFSETS_CUR_MP  = [0x70, 0x0, 0x80, 0x2B0, 0x230]
OFFSETS_LIVE_ES = [0x60, 0x68, 0x50, 0x40, 0x334]
OFFSETS_MAX_ES  = [0x60, 0x68, 0x50, 0x40, 0x338]
OFFSETS_POS_X   = [0x70, 0x28, 0x58, 0x38, 0x2A0]
OFFSETS_POS_Y   = [0x38, 0x150, 0x80, 0x3E8, 0x324]
OFFSETS_INGAME_STATE = [0x38, 0xC0, 0x360, 0x2A0, 0x10]
OFFSETS_ENTITY_LIST   = [0x2D8, 0x298, 0xA30, 0xB4, 0x0]

# Default thresholds
DEFAULT_THRESHOLD_HP_LOWER = 55
DEFAULT_THRESHOLD_HP_UPPER = 65
DEFAULT_THRESHOLD_MP_LOWER = 55
DEFAULT_THRESHOLD_MP_UPPER = 65
DEFAULT_THRESHOLD_ES_LOWER = 55
DEFAULT_THRESHOLD_ES_UPPER = 65

# Default timing configuration
DEFAULT_HEALTH_POTION_DELAY = 0.5
DEFAULT_MANA_POTION_DELAY = 0.5
MONITOR_SLEEP_TIME = 0.2

# Default hotkeys
DEFAULT_TOGGLE_KEY = "F8"
DEFAULT_PAUSE_KEY = "F9"
DEFAULT_SINGLE_SCREEN_HOTKEY = "F10"

# Default chicken configuration
DEFAULT_CHICKEN_ENABLED = False
DEFAULT_CHICKEN_THRESHOLD = 30

# Offsets map for easy reference
STATS_OFFSETS_MAP = {
    "LiveHP": OFFSETS_LIVE_HP,
    "MaxHP": OFFSETS_MAX_HP,
    "CurMP": OFFSETS_CUR_MP,
    "MaxMP": OFFSETS_MAX_MP,
    "LiveES": OFFSETS_LIVE_ES,
    "MaxES": OFFSETS_MAX_ES,
    "PosX": OFFSETS_POS_X,
    "PosY": OFFSETS_POS_Y,
    "IngameState": OFFSETS_INGAME_STATE,
    "EntityList": OFFSETS_ENTITY_LIST,
}
