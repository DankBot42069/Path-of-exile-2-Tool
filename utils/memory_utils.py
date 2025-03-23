#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import pymem
import pymem.process
from config.default_config import *
from utils.config_utils import get_config
class MemoryReader:
    """Class for reading memory from the game process."""
    
    def __init__(self):
        self.pm = None
        self.module_base = None
        self.stats_base_pointer = None
        self.process_attached = False
    
    def attach_to_process(self):
        """
        Attempt to attach to the game process.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Get the process name from config
            config = get_config()
            game_version = config.get("GAME_VERSION")
            process_name = PROCESS_NAMES.get(game_version)
            
            if not process_name:
                print(f"Invalid game version: {game_version}")
                return False
                
            print(f"Attaching to process: {process_name}")
            self.pm = pymem.Pymem(process_name)
            module = pymem.process.module_from_name(self.pm.process_handle, process_name)
            self.module_base = module.lpBaseOfDll
            self.stats_base_pointer = self.module_base + STATS_BASE_ADDRESS_OFFSET
            self.process_attached = True
            return True
        except Exception as e:
            self.pm = None
            self.module_base = None
            self.stats_base_pointer = None
            self.process_attached = False
            print(f"Failed to attach to process: {e}")
            return False
    
    def is_attached(self):
        """Check if we're attached to the process."""
        return self.process_attached
    
    def resolve_pointer(self, base, offsets):
        """
        Follow a chain of pointers starting from 'base' with the given offsets.
        
        Args:
            base (int): Base address to start from.
            offsets (list): List of offsets to follow.
            
        Returns:
            int: Final memory address, or None if invalid.
        """
        if not self.is_attached():
            return None
            
        try:
            addr = self.pm.read_longlong(base)
            for off in offsets[:-1]:
                if not addr:
                    return None
                addr = self.pm.read_longlong(addr + off)
            return addr + offsets[-1]
        except Exception:
            return None
    
    def read_player_stats(self, offsets_map):
        """
        Read player statistics from memory.
        
        Args:
            offsets_map (dict): Dictionary mapping stat names to offset chains.
            
        Returns:
            dict: Dictionary of player statistics.
        """
        if not self.is_attached():
            return {}
            
        stats = {}
        try:
            # HP
            hp_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["LiveHP"])
            if hp_addr:
                stats["current_hp"] = self.pm.read_int(hp_addr)

            max_hp_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["MaxHP"])
            if max_hp_addr:
                stats["max_hp"] = self.pm.read_int(max_hp_addr)

            # MP
            mp_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["CurMP"])
            if mp_addr:
                stats["current_mp"] = self.pm.read_int(mp_addr)

            max_mp_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["MaxMP"])
            if max_mp_addr:
                stats["max_mp"] = self.pm.read_int(max_mp_addr)

            # ES
            es_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["LiveES"])
            if es_addr:
                stats["current_es"] = self.pm.read_int(es_addr)

            max_es_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["MaxES"])
            if max_es_addr:
                stats["max_es"] = self.pm.read_int(max_es_addr)

            # X/Y
            pos_x_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["PosX"])
            if pos_x_addr:
                x_bytes = self.pm.read_bytes(pos_x_addr, 4)
                stats["pos_x"] = struct.unpack("<f", x_bytes)[0]

            pos_y_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["PosY"])
            if pos_y_addr:
                y_bytes = self.pm.read_bytes(pos_y_addr, 4)
                stats["pos_y"] = struct.unpack("<f", y_bytes)[0]

            # IngameState
            if "IngameState" in offsets_map:
                ig_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["IngameState"])
                if ig_addr:
                    stats["ingame_state"] = self.pm.read_int(ig_addr)

            # EntityList
            if "EntityList" in offsets_map:
                en_addr = self.resolve_pointer(self.stats_base_pointer, offsets_map["EntityList"])
                if en_addr:
                    stats["entity_list"] = self.pm.read_int(en_addr)

            # Compute HP/MP/ES percents
            stats["hp_percent"] = 0.0
            if stats.get("max_hp", 0) > 0:
                stats["hp_percent"] = (stats["current_hp"] / float(stats["max_hp"])) * 100

            stats["mp_percent"] = 0.0
            if stats.get("max_mp", 0) > 0:
                stats["mp_percent"] = (stats["current_mp"] / float(stats["max_mp"])) * 100

            if stats.get("max_es", 0) == 0:
                stats["es_percent"] = 0
            else:
                stats["es_percent"] = (stats["current_es"] / float(stats["max_es"])) * 100

        except Exception as e:
            print(f"Error reading stats: {e}")
        
        return stats
        
    def pattern_scan(self, module, pattern):
        """
        Scan memory for a pattern.
        
        Args:
            module: Module to scan.
            pattern (str): Byte pattern to search for.
            
        Returns:
            int: Address of the pattern if found, 0 otherwise.
        """
        if not self.is_attached():
            return 0
            
        def pattern_to_bytes_mask(pat):
            parts = pat.split()
            ba = []
            mask = []
            for p in parts:
                if p == "??":
                    ba.append(0)
                    mask.append("?")
                else:
                    ba.append(int(p, 16))
                    mask.append("x")
            return ba, mask

        pat_bytes, pat_mask = pattern_to_bytes_mask(pattern)
        start = module.lpBaseOfDll
        size = module.SizeOfImage
        end = start + size - len(pat_bytes)
        chunk_size = 0x10000
        address = start

        while address < end:
            read_size = min(chunk_size, end - address)
            data = self.pm.read_bytes(address, read_size)
            for i in range(read_size - len(pat_bytes) + 1):
                match_found = True
                for j, b in enumerate(pat_bytes):
                    if pat_mask[j] == 'x' and data[i+j] != b:
                        match_found = False
                        break
                if match_found:
                    return address + i
            address += (read_size - len(pat_bytes) + 1)
        return 0
        
    def patch_memory(self, address, bytes_to_write):
        """
        Write bytes to memory.
        
        Args:
            address (int): Address to write to.
            bytes_to_write (bytes): Bytes to write.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.is_attached():
            return False
            
        try:
            self.pm.write_bytes(address, bytes_to_write, len(bytes_to_write))
            return True
        except Exception as e:
            print(f"Error patching memory: {e}")
            return False
            
    def aob_scan(self, module_name, signature):
        """
        Scan memory for a pattern in a specific module.
        
        Args:
            module_name (str): Name of the module to scan.
            signature (str): Byte pattern to search for.
            
        Returns:
            int: Address of the pattern if found, None otherwise.
        """
        if not self.is_attached():
            return None
            
        try:
            module = None
            for m in self.pm.list_modules():
                if m.name.lower() == module_name.lower():
                    module = m
                    break
                    
            if not module:
                raise ValueError(f"Module {module_name} not found")

            pattern = signature.split()
            pattern_bytes = []
            mask = []
            for byte in pattern:
                if byte == "??":
                    pattern_bytes.append(0x00)
                    mask.append("?")
                else:
                    pattern_bytes.append(int(byte, 16))
                    mask.append("x")

            memory = self.pm.read_bytes(module.lpBaseOfDll, module.SizeOfImage)
            for i in range(len(memory) - len(pattern_bytes)):
                match = True
                for j in range(len(pattern_bytes)):
                    if mask[j] == "x" and memory[i+j] != pattern_bytes[j]:
                        match = False
                        break
                if match:
                    return module.lpBaseOfDll + i
            return None
        except Exception as e:
            print(f"Error in AOB scan: {e}")
            return None
