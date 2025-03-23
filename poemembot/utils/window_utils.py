#!/usr/bin/env python
# -*- coding: utf-8 -*-

import win32gui
from utils.config_utils import get_config
from config.default_config import WINDOW_TITLE

def list_windows():
    """
    List all visible windows.
    
    Returns:
        list: List of window titles.
    """
    results = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                results.append(title)
        return True
    win32gui.EnumWindows(cb, None)
    return results

def get_game_window_rect():
    """
    Get the rectangle coordinates of the game window.
    
    Returns:
        tuple: (left, top, width, height) or None if not found.
    """
    config = get_config()
    window_title = config.get("TARGET_WINDOW_TITLE", WINDOW_TITLE)
    
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd == 0:
        return None
        
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    return (left, top, right-left, bottom-top)

def find_window_handle(window_title):
    """
    Find window handle by title.
    
    Args:
        window_title (str): Window title to search for.
        
    Returns:
        int: Window handle or 0 if not found.
    """
    return win32gui.FindWindow(None, window_title)

def get_window_rect(hwnd):
    """
    Get window rectangle from handle.
    
    Args:
        hwnd (int): Window handle.
        
    Returns:
        tuple: (left, top, right, bottom) or None if invalid.
    """
    if hwnd == 0:
        return None
    return win32gui.GetWindowRect(hwnd)