#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

from config.default_config import ENTITY_COMPONENT_OFFSETS
from ui.components import LogTextArea, ScrollableFrame
from core.entity import EntityList

class EntityTab:
    """Entity manager tab UI."""
    
    def __init__(self, parent, memory_reader):
        """
        Initialize the entity tab.
        
        Args:
            parent: Parent widget.
            memory_reader: Memory reader instance.
        """
        self.parent = parent
        self.memory_reader = memory_reader
        self.entity_list = EntityList(memory_reader)
        
        self.monitoring = False
        self.monitor_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI elements."""
        entity_frame = ttk.Frame(self.parent, padding=10)
        entity_frame.grid(sticky="nsew")
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        
        # Status information
        self.status_label = ttk.Label(entity_frame, text="Status: Not Monitoring")
        self.status_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0,5))
        
        # Buttons
        button_frame = ttk.Frame(entity_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=5, sticky="ew")
        
        ttk.Button(button_frame, text="Start Entity Monitoring", command=self.start_monitoring).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Stop Entity Monitoring", command=self.stop_monitoring).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Refresh Now", command=self.refresh_now).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Clear Log", command=self.clear_log).grid(row=0, column=3, padx=5)
        
        # Entity Count frame
        count_frame = ttk.LabelFrame(entity_frame, text="Entity Counts", padding=5)
        count_frame.grid(row=2, column=0, columnspan=3, pady=5, sticky="ew")
        
        ttk.Label(count_frame, text="Total Entities:").grid(row=0, column=0, sticky="w", padx=5)
        self.total_count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, textvariable=self.total_count_var).grid(row=0, column=1, sticky="w", padx=5)
        
        ttk.Label(count_frame, text="Monsters:").grid(row=0, column=2, sticky="w", padx=5)
        self.monster_count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, textvariable=self.monster_count_var).grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(count_frame, text="Players:").grid(row=0, column=4, sticky="w", padx=5)
        self.player_count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, textvariable=self.player_count_var).grid(row=0, column=5, sticky="w", padx=5)
        
        ttk.Label(count_frame, text="Items:").grid(row=0, column=6, sticky="w", padx=5)
        self.item_count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, textvariable=self.item_count_var).grid(row=0, column=7, sticky="w", padx=5)
        
        ttk.Label(count_frame, text="NPCs:").grid(row=0, column=8, sticky="w", padx=5)
        self.npc_count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, textvariable=self.npc_count_var).grid(row=0, column=9, sticky="w", padx=5)
        
        # Filter options
        filter_frame = ttk.LabelFrame(entity_frame, text="Display Filters", padding=5)
        filter_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")
        
        self.show_monsters_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="Show Monsters", variable=self.show_monsters_var).grid(row=0, column=0, padx=5)
        
        self.show_players_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="Show Players", variable=self.show_players_var).grid(row=0, column=1, padx=5)
        
        self.show_items_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Show Items", variable=self.show_items_var).grid(row=0, column=2, padx=5)
        
        self.show_npcs_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(filter_frame, text="Show NPCs", variable=self.show_npcs_var).grid(row=0, column=3, padx=5)
        
        ttk.Label(filter_frame, text="Max Distance:").grid(row=0, column=4, padx=(15,5))
        self.max_distance_var = tk.IntVar(value=100)
        ttk.Entry(filter_frame, textvariable=self.max_distance_var, width=5).grid(row=0, column=5, padx=5)
        
        ttk.Button(filter_frame, text="Apply Filters", command=self.apply_filters).grid(row=0, column=6, padx=15)
        
        # Create a splitter with entity list on top and log on bottom
        paned_window = ttk.PanedWindow(entity_frame, orient=tk.VERTICAL)
        paned_window.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=5)
        entity_frame.rowconfigure(4, weight=1)
        
        # Entity list frame (top pane)
        entity_list_frame = ttk.LabelFrame(paned_window, text="Entity List")
        paned_window.add(entity_list_frame, weight=2)
        
        # Set up scrollable entity list with columns
        self.entity_tree = ttk.Treeview(entity_list_frame, columns=("Type", "ID", "Name", "HP", "Pos"))
        self.entity_tree.heading("#0", text="")
        self.entity_tree.heading("Type", text="Type")
        self.entity_tree.heading("ID", text="ID")
        self.entity_tree.heading("Name", text="Name")
        self.entity_tree.heading("HP", text="HP")
        self.entity_tree.heading("Pos", text="Position")
        
        self.entity_tree.column("#0", width=0, stretch=tk.NO)
        self.entity_tree.column("Type", width=100)
        self.entity_tree.column("ID", width=80)
        self.entity_tree.column("Name", width=150)
        self.entity_tree.column("HP", width=100)
        self.entity_tree.column("Pos", width=150)
        
        # Add scrollbar to entity list
        scrollbar = ttk.Scrollbar(entity_list_frame, orient="vertical", command=self.entity_tree.yview)
        self.entity_tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        self.entity_tree.pack(side="left", fill="both", expand=True)
        
        # Add right-click menu to entity tree
        self.context_menu = tk.Menu(self.entity_tree, tearoff=0)
        self.context_menu.add_command(label="Copy ID", command=self.copy_entity_id)
        self.context_menu.add_command(label="Target", command=self.target_entity)
        self.context_menu.add_command(label="Inspect", command=self.inspect_entity)
        
        self.entity_tree.bind("<Button-3>", self.show_context_menu)
        
        # Log frame (bottom pane)
        log_frame = ttk.LabelFrame(paned_window, text="Entity Log")
        paned_window.add(log_frame, weight=1)
        
        self.log_text = LogTextArea(log_frame, height=8, bg="#1e1e1e", fg="#cccccc")
        self.log_text.pack(fill="both", expand=True)
        
    def start_monitoring(self):
        """Start entity monitoring thread."""
        if self.monitoring:
            return
            
        if not self.memory_reader.is_attached():
            if not self.memory_reader.attach_to_process():
                messagebox.showerror("Error", "Failed to attach to game process")
                return
                
        self.monitoring = True
        self.status_label.config(text="Status: Monitoring Entities")
        
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.log_message("Entity monitoring started")
        
    def stop_monitoring(self):
        """Stop entity monitoring thread."""
        if not self.monitoring:
            return
            
        self.monitoring = False
        
        if self.monitor_thread:
            self.monitor_thread.join(1)
            self.monitor_thread = None
            
        self.status_label.config(text="Status: Not Monitoring")
        self.log_message("Entity monitoring stopped")
        
    def refresh_now(self):
        """Force refresh of entity list."""
        if not self.memory_reader.is_attached():
            if not self.memory_reader.attach_to_process():
                messagebox.showerror("Error", "Failed to attach to game process")
                return
                
        self.log_message("Refreshing entity list...")
        success = self.entity_list.refresh(force=True)
        
        if success:
            self.update_entity_display()
            self.log_message(f"Entity list refreshed - {len(self.entity_list.entities)} entities found")
        else:
            self.log_message("Failed to refresh entity list")
            
    def clear_log(self):
        """Clear the log text area."""
        self.log_text.clear()
        
    def apply_filters(self):
        """Apply display filters to entity list."""
        self.update_entity_display()
        
    def update_entity_display(self):
        """Update the entity treeview with filtered entities."""
        # Clear current items
        for item in self.entity_tree.get_children():
            self.entity_tree.delete(item)
            
        # Get filters
        show_monsters = self.show_monsters_var.get()
        show_players = self.show_players_var.get()
        show_items = self.show_items_var.get()
        show_npcs = self.show_npcs_var.get()
        max_distance = self.max_distance_var.get()
        
        # Get player position for distance calculation
        player_pos = None
        player = self.entity_list.get_player()
        if player:
            player_pos = player.get_position()
            
        # Count entities by type
        total_count = 0
        monster_count = 0
        player_count = 0
        item_count = 0
        npc_count = 0
        
        # Add filtered entities to tree
        for entity_id, entity in self.entity_list.entities.items():
            entity_type = entity.get_entity_type()
            total_count += 1
            
            # Update type counts
            if entity_type == "Monster":
                monster_count += 1
            elif entity_type == "Player":
                player_count += 1
            elif entity_type == "Item":
                item_count += 1
            elif entity_type == "NPC":
                npc_count += 1
                
            # Apply type filters
            if (entity_type == "Monster" and not show_monsters or
                entity_type == "Player" and not show_players or
                entity_type == "Item" and not show_items or
                entity_type == "NPC" and not show_npcs):
                continue
                
            # Apply distance filter if player position is known
            if max_distance > 0 and player_pos:
                entity_pos = entity.get_position()
                if entity_pos:
                    dx = entity_pos[0] - player_pos[0]
                    dy = entity_pos[1] - player_pos[1]
                    distance = (dx**2 + dy**2)**0.5
                    if distance > max_distance:
                        continue
                        
            # Get entity data for display
            name = entity.get_render_name() or f"{entity_type}_{entity_id}"
            
            # Get HP data
            hp_text = "N/A"
            life_data = entity.get_life()
            if life_data:
                current_hp = life_data.get("current", 0)
                max_hp = life_data.get("max", 0)
                percent = life_data.get("percent", 0)
                hp_text = f"{current_hp}/{max_hp} ({percent:.1f}%)"
                
            # Get position data
            pos_text = "N/A"
            pos = entity.get_position()
            if pos:
                pos_text = f"X: {pos[0]:.1f}, Y: {pos[1]:.1f}"
                
            # Add to tree
            self.entity_tree.insert("", "end", values=(entity_type, entity_id, name, hp_text, pos_text))
            
        # Update count labels
        self.total_count_var.set(str(total_count))
        self.monster_count_var.set(str(monster_count))
        self.player_count_var.set(str(player_count))
        self.item_count_var.set(str(item_count))
        self.npc_count_var.set(str(npc_count))
        
    def monitor_loop(self):
        """Entity monitoring loop."""
        while self.monitoring:
            try:
                if not self.memory_reader.is_attached():
                    self.log_message("Process not attached, stopping monitoring")
                    self.stop_monitoring()
                    break
                    
                start_time = time.time()
                success = self.entity_list.refresh()
                
                if success:
                    # Only update UI from the main thread
                    self.parent.after(0, self.update_entity_display)
                    
                # Sleep to avoid hammering the CPU
                time.sleep(0.5)
                
            except Exception as e:
                self.log_message(f"Error in entity monitor: {e}")
                time.sleep(1)
                
    def log_message(self, message):
        """
        Log a message to the entity log.
        
        Args:
            message (str): Message to log.
        """
        self.log_text.log(message)
        
    def show_context_menu(self, event):
        """Show context menu on right-click."""
        iid = self.entity_tree.identify_row(event.y)
        if iid:
            self.entity_tree.selection_set(iid)
            self.context_menu.post(event.x_root, event.y_root)
            
    def copy_entity_id(self):
        """Copy selected entity ID to clipboard."""
        selection = self.entity_tree.selection()
        if not selection:
            return
            
        entity_id = self.entity_tree.item(selection[0], "values")[1]
        self.parent.clipboard_clear()
        self.parent.clipboard_append(entity_id)
        self.log_message(f"Copied entity ID: {entity_id}")
        
    def target_entity(self):
        """Target selected entity."""
        selection = self.entity_tree.selection()
        if not selection:
            return
            
        entity_id = self.entity_tree.item(selection[0], "values")[1]
        self.log_message(f"Targeting entity: {entity_id}")
        # Implement targeting functionality here
        
    def inspect_entity(self):
        """Show detailed information about selected entity."""
        selection = self.entity_tree.selection()
        if not selection:
            return
            
        entity_id = self.entity_tree.item(selection[0], "values")[1]
        try:
            entity_id = int(entity_id)
            if entity_id in self.entity_list.entities:
                entity = self.entity_list.entities[entity_id]
                
                # Create a new window with detailed entity information
                inspect_window = tk.Toplevel(self.parent)
                inspect_window.title(f"Entity Inspection - ID: {entity_id}")
                inspect_window.geometry("500x400")
                inspect_window.transient(self.parent)
                
                # Create a scrollable frame for entity details
                frame = ScrollableFrame(inspect_window)
                frame.pack(fill="both", expand=True, padx=10, pady=10)
                
                # Basic info
                ttk.Label(frame.scrollable_frame, text="Entity Type:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=2)
                ttk.Label(frame.scrollable_frame, text=entity.get_entity_type()).grid(row=0, column=1, sticky="w", pady=2)
                
                ttk.Label(frame.scrollable_frame, text="Entity ID:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=2)
                ttk.Label(frame.scrollable_frame, text=str(entity_id)).grid(row=1, column=1, sticky="w", pady=2)
                
                ttk.Label(frame.scrollable_frame, text="Name:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky="w", pady=2)
                ttk.Label(frame.scrollable_frame, text=entity.get_render_name() or "N/A").grid(row=2, column=1, sticky="w", pady=2)
                
                # Position
                ttk.Label(frame.scrollable_frame, text="Position:", font=("Arial", 10, "bold")).grid(row=3, column=0, sticky="w", pady=2)
                pos = entity.get_position()
                pos_text = f"X: {pos[0]:.2f}, Y: {pos[1]:.2f}" if pos else "N/A"
                ttk.Label(frame.scrollable_frame, text=pos_text).grid(row=3, column=1, sticky="w", pady=2)
                
                # Life data
                ttk.Label(frame.scrollable_frame, text="Life:", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky="w", pady=2)
                life_data = entity.get_life()
                if life_data:
                    current_hp = life_data.get("current", 0)
                    max_hp = life_data.get("max", 0)
                    percent = life_data.get("percent", 0)
                    life_text = f"{current_hp}/{max_hp} ({percent:.1f}%)"
                else:
                    life_text = "N/A"
                ttk.Label(frame.scrollable_frame, text=life_text).grid(row=4, column=1, sticky="w", pady=2)
                
                # Components
                ttk.Label(frame.scrollable_frame, text="Components:", font=("Arial", 10, "bold")).grid(row=5, column=0, sticky="w", pady=2)
                components_text = ", ".join([c for c in ENTITY_COMPONENT_OFFSETS.keys() if entity.get_component(c)])
                ttk.Label(frame.scrollable_frame, text=components_text).grid(row=5, column=1, sticky="w", pady=2)
                
                # Memory address
                ttk.Label(frame.scrollable_frame, text="Memory Address:", font=("Arial", 10, "bold")).grid(row=6, column=0, sticky="w", pady=2)
                ttk.Label(frame.scrollable_frame, text=hex(entity.address)).grid(row=6, column=1, sticky="w", pady=2)
                
                # Add more entity details as needed
                
                ttk.Button(
                    inspect_window, 
                    text="Close", 
                    command=inspect_window.destroy
                ).pack(pady=10)
                
            else:
                self.log_message(f"Entity {entity_id} not found")
        except Exception as e:
            self.log_message(f"Error inspecting entity: {e}")
