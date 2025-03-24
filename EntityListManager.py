#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import struct
from utils.memory_utils import MemoryReader
from utils.config_utils import get_config

class EntityListManager:
    """Manager class for PoE2's entity list."""
    
    def __init__(self, memory_reader):
        """
        Initialize the entity list manager.
        
        Args:
            memory_reader (MemoryReader): Memory reader instance.
        """
        self.memory_reader = memory_reader
        self.entities = {}
        self.last_refresh = 0
        
        # Offsets for linked list traversal
        self.HEAD_OFFSET = 0x0  # Offset to head node from entity list pointer
        self.NEXT_OFFSET = 0x8  # Offset to next node from node address
        self.ID_OFFSET = 0x8    # Offset to entity ID from node address
        
        # Component offsets
        self.COMPONENT_OFFSETS = {
            "Life": 0x30,
            "Mana": 0x38,
            "Position": 0x40,
            "Rendered": 0x48,
            "Player": 0x50,
            "Monster": 0x58,
            "Item": 0x60
        }
        
        # Component field offsets
        self.LIFE_OFFSETS = {
            "current": 0x2C,
            "maximum": 0x30
        }
        
        self.POSITION_OFFSETS = {
            "x": 0x2C,
            "y": 0x30,
            "z": 0x34
        }
        
    def refresh_entities(self, force=False):
        """
        Refresh the entity list.
        
        Args:
            force (bool): Force refresh even if recently refreshed.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        now = time.time()
        
        # Don't refresh too often unless forced
        if not force and now - self.last_refresh < 1.0:
            return True
            
        try:
            self.entities = {}
            self.last_refresh = now
            
            if not self.memory_reader.is_attached():
                print("Cannot refresh entities: Memory reader not attached")
                return False
                
            # Get entity list pointer
            entity_list_ptr = self.memory_reader.get_entity_list_pointer()
            if not entity_list_ptr:
                print("Entity list pointer not found")
                return False
                
            # Get head node of linked list
            head_node = self.memory_reader.pm.read_longlong(entity_list_ptr + self.HEAD_OFFSET)
            if not head_node or not self.is_valid_address(head_node):
                print(f"Invalid head node: {hex(head_node) if head_node else 'NULL'}")
                return False
                
            # Traverse the linked list
            current_node = head_node
            count = 0
            visited = set()  # To prevent infinite loops
            
            while (current_node and self.is_valid_address(current_node) and 
                   count < 1000 and current_node not in visited):
                   
                visited.add(current_node)
                
                # Read entity ID
                entity_id = self.memory_reader.pm.read_longlong(current_node + self.ID_OFFSET)
                if entity_id:
                    # Create entity object
                    entity = self.create_entity(current_node)
                    if entity:
                        self.entities[entity_id] = entity
                        count += 1
                
                # Follow next pointer
                current_node = self.memory_reader.pm.read_longlong(current_node + self.NEXT_OFFSET)
            
            print(f"Found {count} entities")
            return True
            
        except Exception as e:
            print(f"Error refreshing entities: {e}")
            return False
            
    def is_valid_address(self, address):
        """
        Check if an address is valid.
        
        Args:
            address (int): Memory address.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        if address is None:
            return False
            
        if address < 0x10000:
            return False
            
        if address > 0x7FFFFFFFFFFF:
            return False
            
        # More specific check for PoE2 addresses
        high_bits = address >> 32
        if high_bits < 0x1E0 or high_bits > 0x1F0:  # Based on observed addresses
            return False
            
        return True
        
    def create_entity(self, address):
        """
        Create an entity object from a memory address.
        
        Args:
            address (int): Entity memory address.
            
        Returns:
            dict: Entity data, or None if invalid.
        """
        try:
            # Basic entity data
            entity = {
                "address": address,
                "id": self.memory_reader.pm.read_longlong(address + self.ID_OFFSET),
                "components": {}
            }
            
            # Read components
            for component_name, offset in self.COMPONENT_OFFSETS.items():
                component_ptr = self.memory_reader.pm.read_longlong(address + offset)
                if component_ptr and self.is_valid_address(component_ptr):
                    entity["components"][component_name] = component_ptr
            
            # Read life data if available
            if "Life" in entity["components"]:
                life_ptr = entity["components"]["Life"]
                current_hp = self.memory_reader.pm.read_int(life_ptr + self.LIFE_OFFSETS["current"])
                max_hp = self.memory_reader.pm.read_int(life_ptr + self.LIFE_OFFSETS["maximum"])
                
                if max_hp > 0:
                    entity["hp_percent"] = (current_hp / max_hp) * 100
                    entity["current_hp"] = current_hp
                    entity["max_hp"] = max_hp
            
            # Read position if available
            if "Position" in entity["components"]:
                pos_ptr = entity["components"]["Position"]
                
                x_bytes = self.memory_reader.pm.read_bytes(pos_ptr + self.POSITION_OFFSETS["x"], 4)
                y_bytes = self.memory_reader.pm.read_bytes(pos_ptr + self.POSITION_OFFSETS["y"], 4)
                
                x = struct.unpack("<f", x_bytes)[0]
                y = struct.unpack("<f", y_bytes)[0]
                
                entity["position"] = (x, y)
                
            # Determine entity type
            if "Player" in entity["components"]:
                entity["type"] = "Player"
            elif "Monster" in entity["components"]:
                entity["type"] = "Monster"
            elif "Item" in entity["components"]:
                entity["type"] = "Item"
            else:
                entity["type"] = "Unknown"
                
            return entity
            
        except Exception as e:
            print(f"Error creating entity: {e}")
            return None
            
    def get_nearby_monsters(self, max_distance=50):
        """
        Get nearby monsters.
        
        Args:
            max_distance (float): Maximum distance from player.
            
        Returns:
            list: Nearby monster entities.
        """
        result = []
        
        # Find player
        player = None
        for entity in self.entities.values():
            if entity.get("type") == "Player":
                player = entity
                break
                
        if not player or "position" not in player:
            return result
            
        player_pos = player["position"]
        
        # Find nearby monsters
        for entity in self.entities.values():
            if entity.get("type") == "Monster" and "position" in entity:
                monster_pos = entity["position"]
                
                # Calculate distance
                dx = monster_pos[0] - player_pos[0]
                dy = monster_pos[1] - player_pos[1]
                distance = (dx**2 + dy**2)**0.5
                
                if distance <= max_distance:
                    entity["distance"] = distance
                    result.append(entity)
                    
        # Sort by distance
        result.sort(key=lambda e: e.get("distance", 0))
        return result
        
    def get_player(self):
        """
        Get player entity.
        
        Returns:
            dict: Player entity, or None if not found.
        """
        for entity in self.entities.values():
            if entity.get("type") == "Player":
                return entity
                
        return None
