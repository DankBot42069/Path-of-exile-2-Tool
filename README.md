# PoE2 Auto-Potion Bot

This tool provides automatic potion usage and other quality-of-life features for Path of Exile 2. With support for steam and ggg versions.

## ⚠️ WARNING ⚠️

Using memory-based tools like this one may violate the game's terms of service and could result in your account being banned. Use at your own risk!

## Features

- **Auto Potion**: Automatically use health and mana potions when stats drop below thresholds
- **Chicken Script**: Emergency logout when health drops dangerously low
- **Game Hacks**: Various game modifications (zoom hack, visibility improvements, atlas fog removal)
- **UI Monitoring**: Real-time display of player stats (HP/MP/ES)
- **Configurable Hotkeys**: Customize keys to control bot functions

## Installation

### Requirements

- Python 3.7 or higher
- Windows Operating System

### Dependencies

Install the required Python packages:

```
pip install pyautogui pymem keyboard win32gui tkinter
```

### Setup

1. Clone or download this repository
2. Navigate to the project directory
3. Run the application:
   ```
   python main.py
   ```

## Usage

### Auto-Potion Tab

1. **Select Target Window**: Choose the Path of Exile 2 game window
2. **Adjust Thresholds**: Set HP/MP/ES thresholds for auto-potions
3. **Configure Hotkeys**: Set custom keys for controlling the bot
4. **Start Monitoring**: Begin monitoring and automatic potion usage

### Game Hacks Tab

Contains various game modifications:

- **Zoom Hack**: Remove camera zoom restrictions
- **Visibility Hack**: Improve visual clarity by modifying rendering
- **Atlas Fog Removal**: Remove fog of war from the Atlas

## Configuration

Settings are automatically saved to `config.json` in the application directory. You can manually edit this file when the application is closed.

## Developing & Extending

The application is modular and designed for easy extension:

- `config/` - Configuration constants and defaults
- `utils/` - Utility functions for memory, configuration, and window management
- `ui/` - User interface components and screens
- `core/` - Core bot and hack functionality

To add new features:
1. Add any new offsets to `config/default_config.py`
2. Implement memory reading in `utils/memory_utils.py`
3. Add UI components as needed
4. Implement core logic in the appropriate module

## License

This project is for educational purposes only. Use responsibly.

## Disclaimer

This software is provided "as is", without warranty of any kind. The authors take no responsibility for any account bans or other negative consequences that may occur from using this software.
