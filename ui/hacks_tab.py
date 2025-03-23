#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox

from ui.components import LogTextArea
from core.hacks import GameHacks

class HacksTab:
    """Game hacks tab UI."""
    
    def __init__(self, parent, memory_reader):
        """
        Initialize the hacks tab.
        
        Args:
            parent: Parent widget.
            memory_reader: Memory reader instance.
        """
        self.parent = parent
        self.memory_reader = memory_reader
        self.hacks = GameHacks(memory_reader)
        
        # Default NOP count for zoom hack
        self.zoom_nop_count_var = tk.IntVar(value=8)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI elements."""
        hacks_frame = ttk.Frame(self.parent, padding=10)
        hacks_frame.grid(sticky="nsew")
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        warning_label = ttk.Label(
            hacks_frame,
            text="WARNING: Use these hacks at your own risk. May result in game ban!",
            foreground="red",
            font=("Arial", 12, "bold")
        )
        warning_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        buttons_frame = ttk.Frame(hacks_frame)
        buttons_frame.grid(row=1, column=0, sticky="nsew")
        hacks_frame.rowconfigure(1, weight=1)
        
        # --- Camera Zoom Hack ---
        zoom_frame = ttk.LabelFrame(buttons_frame, text="Camera Zoom Hack (NOP)", padding=10)
        zoom_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        
        ttk.Label(
            zoom_frame,
            text="Specify how many NOP bytes to write to remove the zoom restriction."
        ).grid(row=0, column=0, columnspan=2, sticky="w", pady=5)
        
        # Entry for how many bytes of 0x90 we want to patch
        ttk.Label(zoom_frame, text="NOP Byte Count:").grid(row=1, column=0, sticky="w", pady=2)
        zoom_nop_count_entry = ttk.Entry(zoom_frame, textvariable=self.zoom_nop_count_var, width=8)
        zoom_nop_count_entry.grid(row=1, column=1, sticky="w", padx=5)
        
        ttk.Button(zoom_frame, text="Apply Zoom Hack", command=self.enable_zoom).grid(row=2, column=0, columnspan=2, pady=5)
        
        # --- Visibility Hack ---
        visibility_frame = ttk.LabelFrame(buttons_frame, text="Visibility Hack", padding=10)
        visibility_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(visibility_frame, text="Improves visibility by modifying\nrender distance and fog effects.").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Button(visibility_frame, text="Enable Visibility Hack", command=self.enable_visibility).grid(row=1, column=0, pady=5)
        
        # --- Atlas Fog Removal ---
        atlas_frame = ttk.LabelFrame(buttons_frame, text="Atlas Fog Removal", padding=10)
        atlas_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        ttk.Label(atlas_frame, text="Removes fog of war on the Atlas,\nrevealing the entire map.").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Button(atlas_frame, text="Remove Atlas Fog", command=self.remove_atlas_fog).grid(row=1, column=0, pady=5)
        
        # Status area
        status_frame = ttk.LabelFrame(hacks_frame, text="Hack Status", padding=10)
        status_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        
        self.hack_status_text = LogTextArea(status_frame, height=20, width=40, bg="#1e1e1e", fg="#cccccc")
        self.hack_status_text.pack(fill="both", expand=True)
        
        # Initial text
        self.hack_status_text.config(state="normal")
        self.hack_status_text.insert("1.0", "No hacks enabled.\n\n")
        self.hack_status_text.insert("end", "Please note that using these hacks may be against\n")
        self.hack_status_text.insert("end", "the game's Terms of Service and could result in\n")
        self.hack_status_text.insert("end", "your account being banned.\n\n")
        self.hack_status_text.insert("end", "Use at your own risk!\n\n")
        self.hack_status_text.insert("end", "Hack activity will be shown here.")
        self.hack_status_text.config(state="disabled")
        
    def log_message(self, message):
        """
        Log a message to the hack status log.
        
        Args:
            message (str): Message to log.
        """
        self.hack_status_text.log(message)
        
    def enable_zoom(self):
        """Enable the zoom hack."""
        if not self.memory_reader.is_attached():
            messagebox.showerror("Error", "Process not attached")
            return
            
        nop_count = self.zoom_nop_count_var.get()
        if nop_count <= 0:
            messagebox.showerror("Error", "NOP byte count must be > 0")
            return
            
        success, message = self.hacks.enable_zoom_hack(nop_count)
        
        if success:
            self.log_message(message)
        else:
            messagebox.showerror("Error", message)
            
    def enable_visibility(self):
        """Enable the visibility hack."""
        if not self.memory_reader.is_attached():
            messagebox.showerror("Error", "Process not attached")
            return
            
        success, message = self.hacks.enable_visibility_hack()
        
        if success:
            self.log_message(message)
        else:
            messagebox.showerror("Error", message)
            
    def remove_atlas_fog(self):
        """Remove atlas fog."""
        if not self.memory_reader.is_attached():
            messagebox.showerror("Error", "Process not attached")
            return
            
        success, message = self.hacks.remove_atlas_fog()
        
        if success:
            self.log_message(message)
        else:
            messagebox.showerror("Error", message)
