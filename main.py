import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
from config.default_config import PROCESS_NAMES
from utils.config_utils import get_config
# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from utils.config_utils import load_config
from utils.memory_utils import MemoryReader
from ui.main_tab import MainTab
from ui.hacks_tab import HacksTab
from core.bot import AutoPotionBot

class PoE2AutoBot(tk.Tk):
    """Main application class."""
    
    def __init__(self):
        super().__init__()
        
        self.title("PoE2 Auto-Potion Bot")
        self.geometry("700x800")
        self.configure_style()
        
        load_config()
        config = get_config()

        # Get the selected game version
        game_version = config.get("GAME_VERSION")
        
        # Initialize memory reader
        self.memory_reader = MemoryReader()
        if not self.memory_reader.attach_to_process():
            messagebox.showwarning(
                "Memory Warning", 
                f"Could not attach to game process ({PROCESS_NAMES[game_version]}). Some features may not work."
            )
        
        # Initialize bot controller
        self.bot = AutoPotionBot(self.memory_reader, self.ui_callback)
        
        # Create notebook with tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # Create tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.hacks_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="Auto Potion")
        self.notebook.add(self.hacks_tab, text="Game Hacks")
        
        # Initialize tab contents
        self.main_tab_ui = MainTab(self.main_tab, self.bot)
        self.hacks_tab_ui = HacksTab(self.hacks_tab, self.memory_reader)
        
        # Set up protocol for window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def configure_style(self):
        """Configure the visual style of the application."""
        style = ttk.Style()
        style.theme_use("clam")
        
        # Set up dark theme
        dark_bg = "#2e2e2e"
        dark_fg = "#ffffff"
        button_bg = "#3e3e3e"
        
        style.configure("TFrame", background=dark_bg)
        style.configure("TLabel", background=dark_bg, foreground=dark_fg, font=("Arial", 10))
        style.configure("TButton", background=button_bg, foreground=dark_fg, font=("Arial", 10))
        style.configure("TLabelframe", background=dark_bg, foreground=dark_fg, font=("Arial", 10, "bold"))
        style.configure("TLabelframe.Label", background=dark_bg, foreground=dark_fg)
        style.configure("TEntry", fieldbackground=button_bg, foreground=dark_fg)
        style.configure("TNotebook", background=dark_bg)
        style.configure("TNotebook.Tab", background=button_bg, foreground=dark_fg, padding=[10, 2])
        
        # Configure the tab appearance
        style.map("TNotebook.Tab",
            background=[("selected", dark_bg)],
            foreground=[("selected", dark_fg)]
        )
        
        self.configure(background=dark_bg)
        
    def ui_callback(self, action, *args, **kwargs):
        """
        Callback function for UI updates from the bot.
        
        Args:
            action (str): Action to perform.
            *args: Variable arguments.
            **kwargs: Keyword arguments.
        """
        if action == "log_message":
            message = args[0]
            self.main_tab_ui.log_message(message)
            
        elif action == "update_status":
            is_monitoring, is_paused = args
            self.main_tab_ui.update_status(is_monitoring, is_paused)
            
        elif action == "update_stats":
            stats = args[0]
            self.main_tab_ui.update_stats(stats)
            
    def on_close(self):
        """Handle application close."""
        # Stop monitoring if active
        if self.bot.monitoring:
            self.bot.stop_monitoring()
            
        # Unregister all hotkeys
        self.bot.update_hotkeys("", "", "")
        
        # Clean up other resources if needed
        
        # Close the application
        self.destroy()

if __name__ == "__main__":
    app = PoE2AutoBot()
    app.mainloop()
