#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import threading

from ui.components import DualThresholdFillSlider, LogTextArea
from utils.config_utils import get_config, update_config
from utils.window_utils import list_windows
from config.default_config import *

class MainTab:
    """Main auto-potion tab UI."""
    
    def __init__(self, parent, bot_controller):
        """
        Initialize the main tab.
        
        Args:
            parent: Parent widget.
            bot_controller: Bot controller instance.
        """
        self.parent = parent
        self.bot = bot_controller
        self.config = get_config()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI elements."""
        main_frame = ttk.Frame(self.parent, padding=10)
        main_frame.grid(sticky="nsew")
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Status information
        self.status_label = ttk.Label(main_frame, text="Status: Not Monitoring")
        self.status_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,5))
        
        self.target_window_label = ttk.Label(
            main_frame, text=f"Target Window: {self.config.get('TARGET_WINDOW_TITLE', WINDOW_TITLE)}"
        )
        self.target_window_label.grid(row=1, column=0, sticky="w", pady=(0,5))
        
        btn_select_window = ttk.Button(main_frame, text="Select Target Window", command=self.select_target_window)
        btn_select_window.grid(row=1, column=1, sticky="w", padx=5, pady=(0,5))
        
        # Position info
        position_frame = ttk.Labelframe(main_frame, text="Player Position", padding=5)
        position_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.pos_x_var = tk.StringVar(value="X: 0.0")
        self.pos_y_var = tk.StringVar(value="Y: 0.0")
        
        self.pos_x_label = ttk.Label(position_frame, textvariable=self.pos_x_var, font=("Arial", 12, "bold"))
        self.pos_x_label.grid(row=0, column=0, padx=10, sticky="w")
        
        self.pos_y_label = ttk.Label(position_frame, textvariable=self.pos_y_var, font=("Arial", 12, "bold"))
        self.pos_y_label.grid(row=0, column=1, padx=10, sticky="w")
        
        # ES
        es_frame = ttk.Labelframe(main_frame, text="ES Fill & Thresholds", padding=5)
        es_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.es_slider = DualThresholdFillSlider(
            es_frame, width=250, height=23, fill_color="cyan",
            label_text="ES",
            lower_initial=self.config.get("THRESHOLD_ES_LOWER", DEFAULT_THRESHOLD_ES_LOWER),
            upper_initial=self.config.get("THRESHOLD_ES_UPPER", DEFAULT_THRESHOLD_ES_UPPER),
            threshold_change_callback=self.update_es_threshold
        )
        self.es_slider.pack(pady=2, fill="x", expand=True)
        
        # HP
        hp_frame = ttk.Labelframe(main_frame, text="HP Fill & Thresholds", padding=5)
        hp_frame.grid(row=4, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.hp_slider = DualThresholdFillSlider(
            hp_frame, width=250, height=30, fill_color="red",
            label_text="HP",
            lower_initial=self.config.get("THRESHOLD_HP_LOWER", DEFAULT_THRESHOLD_HP_LOWER),
            upper_initial=self.config.get("THRESHOLD_HP_UPPER", DEFAULT_THRESHOLD_HP_UPPER),
            threshold_change_callback=self.update_hp_threshold
        )
        self.hp_slider.pack(pady=2, fill="x", expand=True)
        
        # MP
        mp_frame = ttk.Labelframe(main_frame, text="MP Fill & Thresholds", padding=5)
        mp_frame.grid(row=5, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.mp_slider = DualThresholdFillSlider(
            mp_frame, width=250, height=30, fill_color="blue",
            label_text="MP",
            lower_initial=self.config.get("THRESHOLD_MP_LOWER", DEFAULT_THRESHOLD_MP_LOWER),
            upper_initial=self.config.get("THRESHOLD_MP_UPPER", DEFAULT_THRESHOLD_MP_UPPER),
            threshold_change_callback=self.update_mp_threshold
        )
        self.mp_slider.pack(pady=2, fill="x", expand=True)
        
        # Chickening
        chicken_frame = ttk.Labelframe(main_frame, text="Chickening (Emergency Exit)", padding=5)
        chicken_frame.grid(row=6, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.chicken_enabled_var = tk.BooleanVar(value=self.config.get("CHICKEN_ENABLED", DEFAULT_CHICKEN_ENABLED))
        self.chicken_threshold_var = tk.DoubleVar(value=self.config.get("CHICKEN_THRESHOLD", DEFAULT_CHICKEN_THRESHOLD))
        
        chicken_check = ttk.Checkbutton(
            chicken_frame,
            text="Enable Chickening",
            variable=self.chicken_enabled_var,
            command=self.update_chicken_enabled
        )
        chicken_check.grid(row=0, column=0, sticky="w")
        
        ttk.Label(chicken_frame, text="HP Threshold:").grid(row=0, column=1, padx=(20,0))
        chicken_threshold_entry = ttk.Entry(chicken_frame, width=5, textvariable=self.chicken_threshold_var)
        chicken_threshold_entry.grid(row=0, column=2, padx=5)
        chicken_threshold_entry.bind("<Return>", lambda e: self.update_chicken_threshold())
        ttk.Label(chicken_frame, text="%").grid(row=0, column=3)
        
        # Potion Delay
        delay_frame = ttk.Labelframe(main_frame, text="Potion Delay Settings", padding=5)
        delay_frame.grid(row=7, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.health_pot_delay_var = tk.DoubleVar(value=self.config.get("HEALTH_POTION_DELAY", DEFAULT_HEALTH_POTION_DELAY))
        self.mana_pot_delay_var = tk.DoubleVar(value=self.config.get("MANA_POTION_DELAY", DEFAULT_MANA_POTION_DELAY))
        
        ttk.Label(delay_frame, text="Health Potion Delay:").grid(row=0, column=0, sticky="w")
        health_delay_entry = ttk.Entry(delay_frame, width=5, textvariable=self.health_pot_delay_var)
        health_delay_entry.grid(row=0, column=1, padx=5)
        health_delay_entry.bind("<Return>", lambda e: self.update_potion_delays())
        ttk.Label(delay_frame, text="seconds").grid(row=0, column=2, sticky="w")
        
        ttk.Label(delay_frame, text="Mana Potion Delay:").grid(row=0, column=3, sticky="w", padx=(20,0))
        mana_delay_entry = ttk.Entry(delay_frame, width=5, textvariable=self.mana_pot_delay_var)
        mana_delay_entry.grid(row=0, column=4, padx=5)
        mana_delay_entry.bind("<Return>", lambda e: self.update_potion_delays())
        ttk.Label(delay_frame, text="seconds").grid(row=0, column=5, sticky="w")
        
        # Hotkeys
        hotkey_frame = ttk.Labelframe(main_frame, text="Hotkey Settings", padding=5)
        hotkey_frame.grid(row=8, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.toggle_key_var = tk.StringVar(value=self.config.get("TOGGLE_KEY", DEFAULT_TOGGLE_KEY))
        self.pause_key_var = tk.StringVar(value=self.config.get("PAUSE_KEY", DEFAULT_PAUSE_KEY))
        self.single_screen_var = tk.StringVar(value=self.config.get("SINGLE_SCREEN_HOTKEY", DEFAULT_SINGLE_SCREEN_HOTKEY))
        
        ttk.Label(hotkey_frame, text="Toggle Monitoring:").grid(row=0, column=0, sticky="w")
        toggle_key_entry = ttk.Entry(hotkey_frame, width=5, textvariable=self.toggle_key_var)
        toggle_key_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(hotkey_frame, text="Pause/Resume:").grid(row=0, column=2, sticky="w", padx=(20,0))
        pause_key_entry = ttk.Entry(hotkey_frame, width=5, textvariable=self.pause_key_var)
        pause_key_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(hotkey_frame, text="Single Screen Mode:").grid(row=0, column=4, sticky="w", padx=(20,0))
        single_screen_entry = ttk.Entry(hotkey_frame, width=5, textvariable=self.single_screen_var)
        single_screen_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(hotkey_frame, text="Update Hotkeys", command=self.update_hotkeys).grid(row=0, column=6, padx=(20,0))
        
        # Bottom buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=9, column=1, columnspan=2, pady=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="Start Monitoring", command=self.start_monitoring).grid(row=0, column=0, padx=5, sticky="ew")
        ttk.Button(button_frame, text="Stop Monitoring", command=self.stop_monitoring).grid(row=0, column=1, padx=5, sticky="ew")
        
        # Action Log
        log_frame = ttk.Labelframe(main_frame, text="Action Log", padding=5)
        log_frame.grid(row=10, column=0, columnspan=3, pady=5, sticky="nsew")
        main_frame.rowconfigure(10, weight=1)
        
        self.log_text = LogTextArea(log_frame, height=8, bg="#1e1e1e", fg="#cccccc")
        self.log_text.pack(fill="both", expand=True)
        
    def update_status(self, is_monitoring, is_paused):
        """
        Update the status display.
        
        Args:
            is_monitoring (bool): Whether monitoring is active.
            is_paused (bool): Whether monitoring is paused.
        """
        if not is_monitoring:
            status = "Not Monitoring"
        elif is_paused:
            status = "Paused"
        else:
            status = "Monitoring"
            
        self.status_label.config(text=f"Status: {status}")
        
    def update_position(self, x, y):
        """
        Update the position display.
        
        Args:
            x (float): X-coordinate.
            y (float): Y-coordinate.
        """
        self.pos_x_var.set(f"X: {x:.2f}")
        self.pos_y_var.set(f"Y: {y:.2f}")
        
    def update_stats(self, stats):
        """
        Update all stat displays.
        
        Args:
            stats (dict): Player statistics.
        """
        # Update sliders
        self.hp_slider.set_fill(stats.get("hp_percent", 0))
        self.mp_slider.set_fill(stats.get("mp_percent", 0))
        self.es_slider.set_fill(stats.get("es_percent", 0))
        
        # Update position
        self.update_position(stats.get("pos_x", 0.0), stats.get("pos_y", 0.0))
        
    def log_message(self, message):
        """
        Log a message to the action log.
        
        Args:
            message (str): Message to log.
        """
        self.log_text.log(message)
        
    def select_target_window(self):
        """Open window selection dialog."""
        wins = list_windows()
        if not wins:
            messagebox.showinfo("No Windows", "No visible windows found.")
            return

        dialog = tk.Toplevel(self.parent)
        dialog.title("Select Target Window")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="Select the window to target:").pack(pady=5)
        lb = tk.Listbox(dialog, width=50, height=15)
        lb.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)

        for w in wins:
            lb.insert(tk.END, w)

        def on_select():
            sel = lb.curselection()
            if sel:
                idx = sel[0]
                win_t = lb.get(idx)
                update_config("TARGET_WINDOW_TITLE", win_t)
                self.target_window_label.config(text=f"Target Window: {win_t}")
                self.log_message(f"Target window set => {win_t}")
            dialog.destroy()

        tk.Button(dialog, text="Select", command=on_select).pack(pady=5)
        
    def update_hp_threshold(self, lower, upper):
        """Update HP threshold configuration."""
        update_config("THRESHOLD_HP_LOWER", lower)
        update_config("THRESHOLD_HP_UPPER", upper)
        
    def update_mp_threshold(self, lower, upper):
        """Update MP threshold configuration."""
        update_config("THRESHOLD_MP_LOWER", lower)
        update_config("THRESHOLD_MP_UPPER", upper)
        
    def update_es_threshold(self, lower, upper):
        """Update ES threshold configuration."""
        update_config("THRESHOLD_ES_LOWER", lower)
        update_config("THRESHOLD_ES_UPPER", upper)
        
    def update_chicken_threshold(self):
        """Update chicken threshold configuration."""
        threshold = self.chicken_threshold_var.get()
        update_config("CHICKEN_THRESHOLD", threshold)
        self.log_message(f"Chicken threshold updated => {threshold}%")
        
    def update_chicken_enabled(self):
        """Update chicken enabled configuration."""
        enabled = self.chicken_enabled_var.get()
        update_config("CHICKEN_ENABLED", enabled)
        if enabled:
            threshold = self.chicken_threshold_var.get()
            self.log_message(f"Chickening enabled at {threshold}% HP")
        else:
            self.log_message("Chickening disabled")
            
    def update_potion_delays(self):
        """Update potion delay configuration."""
        health_delay = self.health_pot_delay_var.get()
        mana_delay = self.mana_pot_delay_var.get()
        update_config("HEALTH_POTION_DELAY", health_delay)
        update_config("MANA_POTION_DELAY", mana_delay)
        self.log_message(f"Potion delays updated - Health: {health_delay}s, Mana: {mana_delay}s")
        
    def update_hotkeys(self):
        """Update hotkey configuration and register new hotkeys."""
        toggle_key = self.toggle_key_var.get()
        pause_key = self.pause_key_var.get()
        single_screen_key = self.single_screen_var.get()
        
        update_config("TOGGLE_KEY", toggle_key)
        update_config("PAUSE_KEY", pause_key)
        update_config("SINGLE_SCREEN_HOTKEY", single_screen_key)
        
        self.bot.update_hotkeys(toggle_key, pause_key, single_screen_key)
        self.log_message(f"Hotkeys updated and registered")
        
    def start_monitoring(self):
        """Start the bot monitoring."""
        if self.bot.start_monitoring():
            self.update_status(True, False)
            self.log_message("Bot started")
        
    def stop_monitoring(self):
        """Stop the bot monitoring."""
        if self.bot.stop_monitoring():
            self.update_status(False, False)
            self.log_message("Bot stopped")