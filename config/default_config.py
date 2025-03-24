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
OFFSETS_POS_Y   = [0x70, 0x28, 0x58, 0x38, 0x2A4]
OFFSETS_INGAME_STATE = [0x38, 0xC0, 0x360, 0x2A0, 0x10]
# The entity list offsets from the Cheat Table
# Note: These are in reverse order compared to how they appear in Cheat Engine
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

# Entity structures for Path of Exile 2
# These values may need adjustment based on game version

# Entity list structure options to try
ENTITY_LIST_STRUCTURES = [
    {
        "name": "Standard Array",
        "count_offset": 0x8,
        "array_offset": 0x10,
        "stride": 0x8
    },
    {
        "name": "Linked List",
        "head_offset": 0x0,
        "next_offset": 0x8,
        "entity_offset": 0x0
    },
    {
        "name": "HashMap",
        "count_offset": 0xC,
        "buckets_offset": 0x10,
        "bucket_stride": 0x8,
        "bucket_head_offset": 0x0,
        "bucket_next_offset": 0x10
    }
]

# Common entity component offsets for PoE2
# Note: These are examples and may need adjustment
ENTITY_COMPONENT_OFFSETS = {
    "Life": [0x30, 0x28, 0x0],
    "Mana": [0x38, 0x30, 0x0],
    "Position": [0x40, 0x28, 0x0],
    "Rendered": [0x48, 0x30, 0x0],
    "Player": [0x50, 0x68, 0x0],
    "Monster": [0x58, 0x28, 0x0],
    "Item": [0x60, 0x38, 0x0],
    "NPC": [0x68, 0x28, 0x0],
}

# Component-specific offsets
LIFE_OFFSETS = {
    "Current": 0x2C,  # Current HP offset within Life component
    "Maximum": 0x30,  # Maximum HP offset within Life component
}

MANA_OFFSETS = {
    "Current": 0x2C,  # Current MP offset within Mana component
    "Maximum": 0x30,  # Maximum MP offset within Mana component
}

POSITION_OFFSETS = {
    "X": 0x2C,  # X coordinate offset within Position component
    "Y": 0x30,  # Y coordinate offset within Position component
    "Z": 0x34,  # Z coordinate offset within Position component
}

# Entity base info
ENTITY_ID_OFFSET = 0x8  # Entity ID offset from entity base address
ENTITY_TYPE_OFFSET = 0x10  # Type identifier offset from entity base
ENTITY_NAME_OFFSET = 0x20  # Name pointer offset from entity base

# Mapping of entity types to their identifying components
ENTITY_TYPE_COMPONENTS = {
    "Player": "Player",
    "Monster": "Monster",
    "Item": "Item",
    "NPC": "NPC",
}
# Entity structure for Path of Exile 2 (Linked List)

# Entity List Structure
ENTITY_LIST_STRUCTURE = {
    "type": "LinkedList",
    "head_offset": 0x0,     # Offset to head node pointer
    "next_offset": 0x8,     # Offset to next node pointer
    "id_offset": 0x8        # Offset to entity ID
}

# Component offsets within an entity
ENTITY_COMPONENTS = {
    "Life": 0x30,
    "Mana": 0x38,
    "Position": 0x40,
    "Rendered": 0x48,
    "Player": 0x50,
    "Monster": 0x58,
    "Item": 0x60
}

# Component structure layouts
LIFE_COMPONENT = {
    "current": 0x2C,   # Current HP
    "maximum": 0x30    # Maximum HP
}

MANA_COMPONENT = {
    "current": 0x2C,   # Current mana
    "maximum": 0x30    # Maximum mana
}

POSITION_COMPONENT = {
    "x": 0x2C,         # X coordinate
    "y": 0x30,         # Y coordinate
    "z": 0x34          # Z coordinate
}

RENDERED_COMPONENT = {
    "name_ptr": 0x10   # Pointer to entity name
}

# String structure
STRING_STRUCTURE = {
    "length": 0x10,    # String length offset
    "data": 0x14       # String data offset (UTF-16)
}
# Entity list traversal
ENTITY_LIST_COUNT_OFFSET = 0x8  # Offset to entity count
ENTITY_LIST_ARRAY_OFFSET = 0x10  # Offset to entity array pointer
ENTITY_ARRAY_STRIDE = 0x8  # Size of each entry in entity array (pointer size)
