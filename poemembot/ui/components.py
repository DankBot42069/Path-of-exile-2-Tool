#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

class DualThresholdFillSlider(tk.Canvas):
    """
    Custom UI widget for visualizing a value with dual thresholds.
    Used for displaying HP/MP/ES values with lower and upper thresholds for potion use.
    """
    def __init__(self, master, width=250, height=30, fill_color="red",
                 label_text="HP", lower_initial=55, upper_initial=65,
                 threshold_change_callback=None, **kwargs):
        super().__init__(master, width=width, height=height, **kwargs)
        self.fill_color = fill_color
        self.label_text = label_text
        self.current_fill = 0
        self.lower_threshold = lower_initial
        self.upper_threshold = upper_initial
        self.threshold_change_callback = threshold_change_callback
        self.random_threshold = None
        self.active_marker = None

        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Configure>", lambda e: self.draw())
        self.draw()

    def draw(self):
        """Draw the slider with current values."""
        self.delete("all")
        cw = max(self.winfo_width(), 1)
        ch = max(self.winfo_height(), 1)

        # Background
        self.create_rectangle(0, 0, cw, ch, fill="lightgray", outline="")

        # Current fill
        fill_w = (self.current_fill / 100) * cw
        self.create_rectangle(0, 0, fill_w, ch, fill=self.fill_color, outline="")

        # Threshold lines
        l_x = (self.lower_threshold / 100) * cw
        u_x = (self.upper_threshold / 100) * cw
        self.create_line(l_x, 0, l_x, ch, fill="black", width=2)
        self.create_line(u_x, 0, u_x, ch, fill="black", width=2)

        # Text in the center
        self.create_text(
            cw/2, ch/2,
            text=f"{self.label_text}: {self.current_fill:.0f}%",
            fill="white",
            font=("Arial", 10, "bold")
        )

        # Threshold labels
        self.create_text(l_x, -5, text=f"{self.lower_threshold:.0f}%", fill="black", font=("Arial", 8))
        self.create_text(u_x, -5, text=f"{self.upper_threshold:.0f}%", fill="black", font=("Arial", 8))

        # Optional "random threshold" line
        if self.random_threshold is not None:
            rx = (self.random_threshold / 100) * cw
            self.create_line(rx, 0, rx, ch, fill="lime", width=2, dash=(3,2))

        if self.threshold_change_callback:
            self.threshold_change_callback(self.lower_threshold, self.upper_threshold)

    def set_fill(self, val):
        """
        Set the current fill value.
        
        Args:
            val (float): Fill value (0-100).
        """
        self.current_fill = max(0, min(100, val))
        self.draw()

    def on_click(self, e):
        """Handle mouse click event."""
        click_val = (e.x / max(self.winfo_width(),1)) * 100
        d_lower = abs(click_val - self.lower_threshold)
        d_upper = abs(click_val - self.upper_threshold)
        self.active_marker = "lower" if d_lower < d_upper else "upper"
        self.update_marker(e.x)

    def on_drag(self, e):
        """Handle mouse drag event."""
        self.update_marker(e.x)

    def on_release(self, e):
        """Handle mouse release event."""
        self.active_marker = None

    def update_marker(self, x):
        """
        Update threshold marker position.
        
        Args:
            x (int): X-coordinate of the mouse.
        """
        new_val = (x / max(self.winfo_width(),1)) * 100
        new_val = max(0, min(100, new_val))
        if self.active_marker == "lower":
            self.lower_threshold = min(new_val, self.upper_threshold)
        elif self.active_marker == "upper":
            self.upper_threshold = max(new_val, self.lower_threshold)
        self.draw()

class ScrollableFrame(ttk.Frame):
    """A scrollable frame widget."""
    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        
        # Create a canvas and scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Layout
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        """Handle mouse wheel events."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

class LogTextArea(tk.Text):
    """A text area for logging with auto-scroll."""
    def __init__(self, parent, *args, **kwargs):
        kwargs.setdefault("state", "disabled")
        tk.Text.__init__(self, parent, *args, **kwargs)
        
    def log(self, message):
        """
        Add a message to the log.
        
        Args:
            message (str): Message to log.
        """
        import time
        
        self.config(state="normal")
        self.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.see("end")
        self.config(state="disabled")
        
    def clear(self):
        """Clear the log."""
        self.config(state="normal")
        self.delete("1.0", "end")
        self.config(state="disabled")