#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import struct
from utils.memory_utils import MemoryReader

# Global position finder to share across all entities
position_finder = None

class Entity:
    """Represents a game entity with its components and attributes."""
    
    def __init__(self, address, memory_reader):
        """
        Initialize an entity.
        
        Args:
            address (int): Memory address of the entity.
            memory_reader (MemoryReader): Memory reader instance.
        """
        global position_finder
        
        self.address = address
        self.memory_reader = memory_reader
        self.components = {}
        self.cached_data = {}
        self.last_refresh = 0
        
        # Initialize position finder if needed
        if position_finder is None:
            from position_finder import PositionFinder
            position_finder = PositionFinder(memory_reader)
        
    def refresh(self):
        """Refresh entity data from memory."""
        self.cached_data = {}
        self.components = {}
        self.last_refresh = time.time()
    
    def is_valid(self):
        """Check if this is a valid entity."""
        try:
            # Basic validation - check if we can read something at this address
            return self.memory_reader.is_valid_address(self.address) and self.get_id() is not None
        except:
            return False
    
    def get_id(self):
        """
        Get entity ID.
        
        Returns:
            int: Entity ID, or None if not available.
        """
        if "id" in self.cached_data:
            return self.cached_data["id"]
            
        try:
            # Try different offsets for entity ID
            for offset in [0x8, 0x10, 0x18]:
                try:
                    entity_id = self.memory_reader.pm.read_longlong(self.address + offset)
                    if entity_id and entity_id > 0:
                        self.cached_data["id"] = entity_id
                        return entity_id
                except:
                    continue
            return None
        except Exception as e:
            print(f"Error reading entity ID: {e}")
            return None
            
    def get_position(self):
        """
        Get entity position using the position finder.
        
        Returns:
            tuple: (x, y) position, or None if not available.
        """
        global position_finder
        
        if "position" in self.cached_data:
            return self.cached_data["position"]
        
        try:
            position = position_finder.find_entity_position(self.address)
            if position:
                self.cached_data["position"] = position
                return position
            return None
        except Exception as e:
            print(f"Error getting position: {e}")
            return None
            
    def get_life(self):
        """
        Get entity life.
        
        Returns:
            dict: Life data (current, max, percent), or empty dict if not available.
        """
        if "life" in self.cached_data:
            return self.cached_data["life"]
            
        try:
            # Try direct offsets first
            for base_offset in [0x30, 0x40, 0x50, 0x60]:
                try:
                    current_hp = self.memory_reader.pm.read_int(self.address + base_offset)
                    max_hp = self.memory_reader.pm.read_int(self.address + base_offset + 4)
                    
                    # Sanity check
                    if 0 <= current_hp <= max_hp and max_hp > 0:
                        percent = (current_hp / max_hp) * 100
                        life_data = {
                            "current": current_hp,
                            "max": max_hp,
                            "percent": percent
                        }
                        self.cached_data["life"] = life_data
                        return life_data
                except:
                    continue
            
            return {}
        except Exception as e:
            print(f"Error reading life: {e}")
            return {}
            
    def get_render_name(self):
        """
        Get entity render name (displayed name).
        
        Returns:
            str: Entity name, or None if not available.
        """
        if "render_name" in self.cached_data:
            return self.cached_data["render_name"]
            
        # Generate a synthetic name based on the entity ID and position
        entity_id = self.get_id()
        if not entity_id:
            return "Unknown"
            
        entity_type = self.get_entity_type()
        position = self.get_position()
        
        if position:
            x, y = position
            name = f"{entity_type or 'Entity'}_{entity_id:X} ({x:.1f}, {y:.1f})"
        else:
            name = f"{entity_type or 'Entity'}_{entity_id:X}"
            
        self.cached_data["render_name"] = name
        return name
            
    def get_entity_type(self):
        """
        Get entity type.
        
        Returns:
            str: Entity type, or None if not available.
        """
        if "entity_type" in self.cached_data:
            return self.cached_data["entity_type"]
            
        try:
            # Check for life data to determine if it's a character
            life = self.get_life()
            if life and life.get("max", 0) > 0:
                # Check if it's the player by position (usually at center)
                pos = self.get_position()
                if pos:
                    # Simple heuristic - player is often near the center of the map
                    # Better detection would involve checking for player component
                    # For now, just classify as a Monster
                    self.cached_data["entity_type"] = "Monster"
                    return "Monster"
            
            # Default to "Unknown"
            self.cached_data["entity_type"] = "Unknown"
            return "Unknown"
        except Exception as e:
            print(f"Error determining entity type: {e}")
            return "Unknown"
    
    def is_monster(self):
        """Check if entity is a monster."""
        return self.get_entity_type() == "Monster"
        
    def is_player(self):
        """Check if entity is a player."""
        return self.get_entity_type() == "Player"


class EntityList:
    """Manager for game entities."""
    
    def __init__(self, memory_reader):
        """
        Initialize the entity list.
        
        Args:
            memory_reader (MemoryReader): Memory reader instance.
        """
        self.memory_reader = memory_reader
        self.entities = {}
        self.last_refresh = 0
        
    def refresh(self, force=False):
        """
        Refresh the entity list from memory.
        
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
                
            # Get entity list pointer from memory
            entity_list_ptr = self.memory_reader.get_entity_list_pointer()
            if not entity_list_ptr:
                print("Entity list pointer not found")
                return False
                
            print(f"Using entity list pointer: {hex(entity_list_ptr)}")
            
            # Read entity list
            entity_addresses = self.read_entity_list(entity_list_ptr)
            
            if not entity_addresses:
                print("No entity addresses found")
                return False
                
            print(f"Found {len(entity_addresses)} entity addresses")
            
            # Create Entity objects for valid addresses
            for addr in entity_addresses:
                try:
                    entity = Entity(addr, self.memory_reader)
                    entity_id = entity.get_id()
                    if entity_id:
                        self.entities[entity_id] = entity
                except Exception as e:
                    continue
            
            print(f"Successfully created {len(self.entities)} valid entities")
            return True
            
        except Exception as e:
            print(f"Error refreshing entity list: {e}")
            return False
            
    def read_entity_list(self, entity_list_ptr):
        """
        Read entity addresses from memory.
        
        Args:
            entity_list_ptr (int): Entity list pointer.
            
        Returns:
            list: List of entity addresses.
        """
        try:
            # Based on diagnostic output, the entity list is at offset 0x0
            # First, try to get the linked list head
            head_ptr = self.memory_reader.pm.read_longlong(entity_list_ptr)
            if not head_ptr or not self.memory_reader.is_valid_address(head_ptr):
                print("Invalid head pointer")
                return []
                
            print(f"Found head pointer: {hex(head_ptr)}")
            
            # Traverse the linked list - diagnostic showed offset 0x8 is next pointer
            entities = []
            current = head_ptr
            visited = set()
            
            while current and current not in visited and len(entities) < 2000:
                if not self.memory_reader.is_valid_address(current):
                    break
                    
                visited.add(current)
                entities.append(current)
                
                # Next entity is at offset 0x8 (confirmed from diagnostic)
                current = self.memory_reader.pm.read_longlong(current + 0x8)
                
            print(f"Found {len(entities)} entities in linked list")
            return entities
            
        except Exception as e:
            print(f"Error reading entity list: {e}")
            return []
        
    def get_entities(self, type_filter=None, max_distance=None, player_pos=None):
        """
        Get entities, optionally filtered.
        
        Args:
            type_filter (str, optional): Filter by entity type.
            max_distance (float, optional): Maximum distance from player.
            player_pos (tuple, optional): Player position (x, y).
            
        Returns:
            list: Filtered entity list.
        """
        results = []
        
        for entity in self.entities.values():
            # Filter by type if specified
            if type_filter and entity.get_entity_type() != type_filter:
                continue
                
            # Filter by distance if specified
            if max_distance and player_pos:
                entity_pos = entity.get_position()
                if entity_pos:
                    dx = entity_pos[0] - player_pos[0]
                    dy = entity_pos[1] - player_pos[1]
                    distance = (dx**2 + dy**2)**0.5
                    if distance > max_distance:
                        continue
                        
            results.append(entity)
            
        return results
        
    def get_player(self):
        """
        Get the player entity.
        
        Returns:
            Entity: Player entity, or None if not found.
        """
        for entity in self.entities.values():
            if entity.is_player():
                return entity
                
        return None
        
    def get_nearby_monsters(self, max_distance=50):
        """
        Get nearby monsters.
        
        Args:
            max_distance (float): Maximum distance from player.
            
        Returns:
            list: Nearby monster entities.
        """
        player = self.get_player()
        if not player:
            return []
            
        player_pos = player.get_position()
        if not player_pos:
            return []
            
        return self.get_entities(type_filter="Monster", max_distance=max_distance, player_pos=player_pos)
        
    def debug_positions(self, limit=10):
        """
        Debug entity positions.
        
        Args:
            limit (int): Maximum number of entities to debug.
            
        Returns:
            dict: Debug information.
        """
        global position_finder
        
        if not position_finder:
            from position_finder import PositionFinder
            position_finder = PositionFinder(self.memory_reader)
            
        # Get entity addresses
        entity_addresses = []
        for entity in list(self.entities.values())[:limit]:
            entity_addresses.append(entity.address)
            
        return position_finder.debug_entity_positions(entity_addresses)
