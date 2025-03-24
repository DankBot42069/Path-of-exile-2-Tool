#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys
import os
import struct
from tkinter import Tk, Text, Button, Frame, Label, Scrollbar, END, WORD, VERTICAL, HORIZONTAL, RIGHT, LEFT, BOTTOM, X, Y, BOTH

# Add the project directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.memory_utils import MemoryReader
from utils.config_utils import load_config, get_config

class EntityDiagnostic:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE2 Entity Diagnostic Tool")
        self.root.geometry("800x600")
        
        # Set up memory reader
        self.memory_reader = MemoryReader()
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        # Top frame with controls
        control_frame = Frame(self.root)
        control_frame.pack(fill=X, padx=10, pady=5)
        
        # Buttons
        Button(control_frame, text="Attach to Process", command=self.attach_process).pack(side=LEFT, padx=5)
        Button(control_frame, text="Find Entity List", command=self.find_entity_list).pack(side=LEFT, padx=5)
        Button(control_frame, text="Analyze Structure", command=self.analyze_structure).pack(side=LEFT, padx=5)
        Button(control_frame, text="Read Entities", command=self.read_entities).pack(side=LEFT, padx=5)
        Button(control_frame, text="Clear Log", command=self.clear_log).pack(side=LEFT, padx=5)
        
        # Status label
        self.status_var = Label(control_frame, text="Status: Not attached")
        self.status_var.pack(side=RIGHT, padx=5)
        
        # Log text area
        log_frame = Frame(self.root)
        log_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Create scrollbars
        y_scrollbar = Scrollbar(log_frame, orient=VERTICAL)
        y_scrollbar.pack(side=RIGHT, fill=Y)
        
        x_scrollbar = Scrollbar(log_frame, orient=HORIZONTAL)
        x_scrollbar.pack(side=BOTTOM, fill=X)
        
        # Create text widget
        self.log_text = Text(log_frame, wrap=WORD, yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.log_text.pack(fill=BOTH, expand=True)
        
        # Configure scrollbars
        y_scrollbar.config(command=self.log_text.yview)
        x_scrollbar.config(command=self.log_text.xview)
        
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        self.log_text.see(END)
        
    def clear_log(self):
        self.log_text.delete(1.0, END)
        
    def attach_process(self):
        try:
            # Load configuration
            load_config()
            
            # Attach to the game process
            if self.memory_reader.attach_to_process():
                self.status_var.config(text="Status: Attached")
                self.log("Successfully attached to process")
                
                # Display process information
                config = get_config()
                game_version = config.get("GAME_VERSION")
                self.log(f"Game version: {game_version}")
                self.log(f"Module base: {hex(self.memory_reader.module_base)}")
                self.log(f"Stats base pointer: {hex(self.memory_reader.stats_base_pointer)}")
            else:
                self.status_var.config(text="Status: Not attached")
                self.log("Failed to attach to process")
        except Exception as e:
            self.log(f"Error: {e}")
            
    def find_entity_list(self):
        if not self.memory_reader.is_attached():
            self.log("Not attached to process")
            return
            
        self.log("Searching for entity list pointer...")
        
        # Try to find entity list pointer
        stats_base = self.memory_reader.stats_base_pointer
        
        # Display the current stats base pointer
        self.log(f"Stats base pointer: {hex(stats_base)}")
        
        # Try to resolve the entity list pointer
        from config.default_config import STATS_OFFSETS_MAP
        entity_list_offsets = STATS_OFFSETS_MAP["EntityList"]
        
        # Display offsets
        self.log(f"Entity list offsets: {[hex(x) for x in entity_list_offsets]}")
        
        try:
            # Try to follow the pointer chain with detailed logging
            current_addr = stats_base
            self.log(f"Starting address: {hex(current_addr)}")
            
            for i, offset in enumerate(entity_list_offsets[:-1]):
                old_addr = current_addr
                current_addr = self.memory_reader.pm.read_longlong(current_addr)
                self.log(f"Step {i}: Read pointer at {hex(old_addr)} -> {hex(current_addr)}")
                
                if not current_addr:
                    self.log(f"Warning: Null pointer at step {i}")
                    break
                    
                current_addr += offset
                self.log(f"Step {i}: Add offset {hex(offset)} -> {hex(current_addr)}")
            
            if current_addr:
                final_addr = current_addr + entity_list_offsets[-1]
                self.log(f"Final entity list address: {hex(final_addr)}")
                
                # Try to examine this address
                self.examine_potential_entity_list(final_addr)
            else:
                self.log("Failed to resolve entity list pointer")
            
        except Exception as e:
            self.log(f"Error resolving entity list pointer: {e}")
            
    def examine_potential_entity_list(self, address):
        """Examine a potential entity list address."""
        try:
            self.log(f"Examining potential entity list at {hex(address)}")
            
            # Read values at various offsets
            self.log("Values at offsets:")
            
            # Read 64-bit values
            for offset in range(0, 0x40, 8):
                try:
                    value = self.memory_reader.pm.read_longlong(address + offset)
                    self.log(f"  +{hex(offset)}: {hex(value)}")
                except:
                    self.log(f"  +{hex(offset)}: [Error reading]")
            
            # Read 32-bit values
            self.log("32-bit values at offsets:")
            for offset in range(0, 0x40, 4):
                try:
                    value = self.memory_reader.pm.read_int(address + offset)
                    self.log(f"  +{hex(offset)}: {value} (0x{value:X})")
                except:
                    pass
                    
            # Check if any value looks like a count
            self.log("Potential entity counts:")
            for offset in range(0, 0x40, 4):
                try:
                    value = self.memory_reader.pm.read_int(address + offset)
                    if 0 < value < 1000:
                        self.log(f"  +{hex(offset)}: {value} (possible entity count)")
                except:
                    pass
                
            # Check if any value looks like a valid pointer
            self.log("Potential entity arrays:")
            for offset in range(0, 0x40, 8):
                try:
                    value = self.memory_reader.pm.read_longlong(address + offset)
                    if value and value > 0x10000:
                        self.log(f"  +{hex(offset)}: {hex(value)} (possible array/list)")
                        
                        # Try to read the first few values from this potential array
                        self.log(f"  Reading first 3 entries from {hex(value)}")
                        for i in range(3):
                            try:
                                entry = self.memory_reader.pm.read_longlong(value + i * 8)
                                self.log(f"    Entry {i}: {hex(entry)}")
                            except:
                                self.log(f"    Entry {i}: [Error reading]")
                except:
                    pass
                    
        except Exception as e:
            self.log(f"Error examining entity list: {e}")
            
    def analyze_structure(self):
        if not self.memory_reader.is_attached():
            self.log("Not attached to process")
            return
            
        self.log("Analyzing entity list structure...")
        
        # Try to find the entity list
        entity_list_ptr = self.memory_reader.get_entity_list_pointer()
        if not entity_list_ptr:
            self.log("Entity list pointer not found")
            return
            
        self.log(f"Entity list pointer: {hex(entity_list_ptr)}")
        
        # Try different structure patterns
        from config.default_config import ENTITY_LIST_STRUCTURES
        
        for structure in ENTITY_LIST_STRUCTURES:
            self.log(f"\nTrying structure: {structure['name']}")
            
            if 'count_offset' in structure and 'array_offset' in structure:
                # This is an array-based structure
                try:
                    count_offset = structure['count_offset']
                    array_offset = structure['array_offset']
                    stride = structure.get('stride', 8)
                    
                    # Read count
                    count = self.memory_reader.pm.read_int(entity_list_ptr + count_offset)
                    self.log(f"  Entity count at +{hex(count_offset)}: {count}")
                    
                    if count <= 0 or count > 10000:
                        self.log(f"  Invalid count: {count}")
                        continue
                        
                    # Read array pointer
                    array_ptr = self.memory_reader.pm.read_longlong(entity_list_ptr + array_offset)
                    self.log(f"  Array pointer at +{hex(array_offset)}: {hex(array_ptr)}")
                    
                    if not array_ptr:
                        self.log("  Invalid array pointer")
                        continue
                        
                    # Try to read the first few entities
                    self.log("  First 5 entities:")
                    valid_entities = 0
                    
                    for i in range(min(5, count)):
                        entity_addr = self.memory_reader.pm.read_longlong(array_ptr + i * stride)
                        self.log(f"    Entity {i}: {hex(entity_addr)}")
                        
                        if entity_addr and entity_addr > 0x10000:
                            valid_entities += 1
                            
                            # Try to read some basic entity data
                            try:
                                id_value = self.memory_reader.pm.read_longlong(entity_addr + 0x8)
                                self.log(f"      ID: {hex(id_value)}")
                                
                                # Try to find a life component
                                for component_offset in [0x30, 0x38, 0x40, 0x48, 0x50]:
                                    component_ptr = self.memory_reader.pm.read_longlong(entity_addr + component_offset)
                                    if component_ptr:
                                        hp_value = self.memory_reader.pm.read_int(component_ptr + 0x2C)
                                        max_hp = self.memory_reader.pm.read_int(component_ptr + 0x30)
                                        
                                        if 0 <= hp_value <= max_hp and max_hp > 0:
                                            self.log(f"      Found life at +{hex(component_offset)}: {hp_value}/{max_hp}")
                                            break
                            except:
                                pass
                    
                    self.log(f"  Found {valid_entities} valid entities out of 5 checked")
                    
                    if valid_entities > 0:
                        self.log(f"  *** Structure '{structure['name']}' appears to be valid! ***")
                        
                except Exception as e:
                    self.log(f"  Error analyzing structure: {e}")
                    
            elif 'head_offset' in structure and 'next_offset' in structure:
                # This is a linked list structure
                try:
                    head_offset = structure['head_offset']
                    next_offset = structure['next_offset']
                    entity_offset = structure.get('entity_offset', 0)
                    
                    # Read head pointer
                    head_ptr = self.memory_reader.pm.read_longlong(entity_list_ptr + head_offset)
                    self.log(f"  Head pointer at +{hex(head_offset)}: {hex(head_ptr)}")
                    
                    if not head_ptr:
                        self.log("  Invalid head pointer")
                        continue
                        
                    # Try to follow the list
                    self.log("  Following linked list:")
                    current = head_ptr
                    valid_entities = 0
                    
                    for i in range(5):  # Just check the first 5
                        if not current:
                            break
                            
                        self.log(f"    Node {i}: {hex(current)}")
                        
                        # Try to get entity from this node
                        entity_addr = current + entity_offset
                        
                        # Try to read basic entity data
                        try:
                            id_value = self.memory_reader.pm.read_longlong(entity_addr + 0x8)
                            self.log(f"      ID: {hex(id_value)}")
                            valid_entities += 1
                        except:
                            pass
                            
                        # Follow the next pointer
                        current = self.memory_reader.pm.read_longlong(current + next_offset)
                        
                    self.log(f"  Found {valid_entities} valid entities")
                    
                    if valid_entities > 0:
                        self.log(f"  *** Structure '{structure['name']}' appears to be valid! ***")
                        
                except Exception as e:
                    self.log(f"  Error analyzing linked list: {e}")
        
    def read_entities(self):
        if not self.memory_reader.is_attached():
            self.log("Not attached to process")
            return
            
        self.log("Reading entities...")
        
        # Use our entity list reading implementation
        entities = self.memory_reader.read_entity_list(max_entities=100)
        
        if not entities:
            self.log("No entities found")
            return
            
        self.log(f"Found {len(entities)} entities")
        
        # Analyze the first few entities
        self.log("First 5 entities:")
        
        for i, entity_addr in enumerate(entities[:5]):
            self.log(f"Entity {i}: {hex(entity_addr)}")
            
            # Try to read entity ID
            try:
                entity_id = self.memory_reader.pm.read_longlong(entity_addr + 0x8)
                self.log(f"  ID: {hex(entity_id)}")
            except:
                self.log("  Error reading ID")
                
            # Try to extract position
            try:
                for offset in [0x30, 0x38, 0x40, 0x48]:
                    try:
                        component_ptr = self.memory_reader.pm.read_longlong(entity_addr + offset)
                        if component_ptr:
                            x_bytes = self.memory_reader.pm.read_bytes(component_ptr + 0x2C, 4)
                            y_bytes = self.memory_reader.pm.read_bytes(component_ptr + 0x30, 4)
                            
                            x = struct.unpack("<f", x_bytes)[0]
                            y = struct.unpack("<f", y_bytes)[0]
                            
                            if -100000 < x < 100000 and -100000 < y < 100000:
                                self.log(f"  Position component at +{hex(offset)}: ({x:.2f}, {y:.2f})")
                                break
                    except:
                        continue
            except Exception as e:
                self.log(f"  Error reading position: {e}")
                
            # Try to find life component
            try:
                for offset in [0x30, 0x38, 0x40, 0x48]:
                    try:
                        component_ptr = self.memory_reader.pm.read_longlong(entity_addr + offset)
                        if component_ptr:
                            current = self.memory_reader.pm.read_int(component_ptr + 0x2C)
                            maximum = self.memory_reader.pm.read_int(component_ptr + 0x30)
                            
                            if 0 <= current <= maximum and maximum > 0:
                                self.log(f"  Life component at +{hex(offset)}: {current}/{maximum}")
                                break
                    except:
                        continue
            except Exception as e:
                self.log(f"  Error reading life: {e}")

def main():
    root = Tk()
    app = EntityDiagnostic(root)
    root.mainloop()

if __name__ == "__main__":
    main()
