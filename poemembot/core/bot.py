#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import pyautogui
import keyboard

from utils.config_utils import get_config
from config.default_config import MONITOR_SLEEP_TIME, STATS_OFFSETS_MAP
from utils.memory_utils import MemoryReader

class AutoPotionBot:
    """Core bot functionality for auto-potions."""
    
    def __init__(self, memory_reader, ui_callback=None):
        """
        Initialize the bot.
        
        Args:
            memory_reader (MemoryReader): Memory reader instance.
            ui_callback: Callback for UI updates.
        """
        self.memory_reader = memory_reader
        self.ui_callback = ui_callback
        
        self.monitoring = False
        self.paused = False
        self.monitor_thread = None
        self.hotkey_handles = []
        
        # Init hotkeys if UI callback is provided
        if ui_callback:
            self.update_hotkeys()
        
    def update_hotkeys(self, toggle_key=None, pause_key=None, single_screen_key=None):
        """
        Update and register hotkeys.
        
        Args:
            toggle_key (str, optional): Toggle monitoring hotkey.
            pause_key (str, optional): Pause/resume hotkey.
            single_screen_key (str, optional): Single screen mode hotkey.
        """
        # Unregister existing hotkeys
        for h in self.hotkey_handles:
            try:
                keyboard.unhook(h)
            except:
                pass
        self.hotkey_handles = []
        
        # Get from config if not provided
        config = get_config()
        toggle_key = toggle_key or config.get("TOGGLE_KEY")
        pause_key = pause_key or config.get("PAUSE_KEY")
        single_screen_key = single_screen_key or config.get("SINGLE_SCREEN_HOTKEY")
        
        # Register new hotkeys
        success_messages = []
        
        try:
            handle = keyboard.add_hotkey(toggle_key, self.toggle_monitoring)
            self.hotkey_handles.append(handle)
            success_messages.append(f"Registered {toggle_key} for toggle monitoring")
        except Exception as e:
            self.log_message(f"Failed to register {toggle_key}: {e}")
            
        try:
            handle = keyboard.add_hotkey(pause_key, self.toggle_pause)
            self.hotkey_handles.append(handle)
            success_messages.append(f"Registered {pause_key} for pause/resume")
        except Exception as e:
            self.log_message(f"Failed to register {pause_key}: {e}")
            
        try:
            handle = keyboard.add_hotkey(single_screen_key, self.toggle_single_screen)
            self.hotkey_handles.append(handle)
            success_messages.append(f"Registered {single_screen_key} for single screen")
        except Exception as e:
            self.log_message(f"Failed to register {single_screen_key}: {e}")
            
        return success_messages
    
    def log_message(self, message):
        """
        Log a message.
        
        Args:
            message (str): Message to log.
        """
        if self.ui_callback:
            self.ui_callback("log_message", message)
        else:
            print(f"[{time.strftime('%H:%M:%S')}] {message}")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off."""
        if self.monitoring:
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def toggle_pause(self):
        """Toggle pause state."""
        if not self.monitoring:
            return
            
        self.paused = not self.paused
        
        if self.ui_callback:
            self.ui_callback("update_status", self.monitoring, self.paused)
            
        status = "paused" if self.paused else "resumed"
        self.log_message(f"Bot {status}")
    
    def toggle_single_screen(self):
        """Toggle single screen mode."""
        self.log_message("Single screen mode toggled (not implemented)")
    
    def start_monitoring(self):
        """
        Start the monitoring thread.
        
        Returns:
            bool: True if started, False if already running.
        """
        if self.monitoring:
            return False
            
        if not self.memory_reader.is_attached():
            if not self.memory_reader.attach_to_process():
                self.log_message("Failed to attach to game process")
                return False
        
        self.monitoring = True
        self.paused = False
        
        if self.ui_callback:
            self.ui_callback("update_status", True, False)
        
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        return True
    
    def stop_monitoring(self):
        """
        Stop the monitoring thread.
        
        Returns:
            bool: True if stopped, False if not running.
        """
        if not self.monitoring:
            return False
            
        self.monitoring = False
        
        if self.ui_callback:
            self.ui_callback("update_status", False, False)
        
        if self.monitor_thread:
            self.monitor_thread.join(1)
            self.monitor_thread = None
            
        return True
    
    def monitor_loop(self):
        """Main monitoring loop."""
        last_hp_pot = 0
        last_mp_pot = 0
        config = get_config()

        while self.monitoring:
            try:
                if self.paused:
                    time.sleep(MONITOR_SLEEP_TIME)
                    continue

                if not self.memory_reader.is_attached():
                    raise Exception("Process not attached")

                now = time.time()

                # Read stats
                stats = self.memory_reader.read_player_stats(STATS_OFFSETS_MAP)
                
                # Update UI if callback is provided
                if self.ui_callback:
                    self.ui_callback("update_stats", stats)

                hp_pct = stats.get("hp_percent", 0)
                mp_pct = stats.get("mp_percent", 0)
                
                # Chickening
                if (config.get("CHICKEN_ENABLED", False) and 
                    hp_pct <= config.get("CHICKEN_THRESHOLD", 30)):
                    self.log_message(f"EMERGENCY EXIT - HP={hp_pct:.1f}%")
                    self.emergency_exit()

                # Automatic potions
                hp_lower = config.get("THRESHOLD_HP_LOWER", 55)
                mp_lower = config.get("THRESHOLD_MP_LOWER", 55)
                health_delay = config.get("HEALTH_POTION_DELAY", 0.5)
                mana_delay = config.get("MANA_POTION_DELAY", 0.5)
                
                if hp_pct <= hp_lower and (now - last_hp_pot > health_delay):
                    pyautogui.press("1")
                    self.log_message(f"Used health pot @ {hp_pct:.1f}%")
                    last_hp_pot = now

                if mp_pct <= mp_lower and (now - last_mp_pot > mana_delay):
                    pyautogui.press("2")
                    self.log_message(f"Used mana pot @ {mp_pct:.1f}%")
                    last_mp_pot = now

                time.sleep(MONITOR_SLEEP_TIME)

            except Exception as e:
                self.log_message(f"Monitor error: {e}")
                time.sleep(1)
    
    def emergency_exit(self):
        """Perform emergency exit (chicken)."""
        try:
            # Send logout hotkey (default is F7 in Path of Exile)
            pyautogui.press("f7")
            self.log_message("Emergency exit triggered - logout hotkey sent")
            
            # Stop monitoring
            self.stop_monitoring()
        except Exception as e:
            self.log_message(f"Emergency exit error: {e}")