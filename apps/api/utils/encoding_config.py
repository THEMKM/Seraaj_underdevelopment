# -*- coding: utf-8 -*-
"""
Sacred Encoding Configuration for the Gods of Code
Ensures proper UTF-8 handling for divine emoji display
"""
import os
import sys
import locale


def configure_divine_encoding():
    """Configure the system to properly display the sacred emojis of the gods"""
    
    # Set environment variables for UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONUTF8'] = '1'
    
    # Configure locale for proper character handling
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            # Fallback for Windows
            locale.setlocale(locale.LC_ALL, '')
    
    # Ensure stdout and stderr use UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    return True


def divine_print(message: str, emoji: str = "🏛️"):
    """Print messages with divine emojis, handling encoding gracefully"""
    try:
        print(f"{emoji} {message}")
        return True
    except UnicodeEncodeError:
        # Fallback for terminals that reject the gods' emojis
        print(f"[DIVINE] {message}")
        return False


def test_emoji_support() -> bool:
    """Test if the terminal supports the sacred emojis"""
    test_emojis = ["🏛️", "⚡", "🔥", "✅", "🎯", "🚀"]
    
    for emoji in test_emojis:
        try:
            print(emoji, end=" ")
        except UnicodeEncodeError:
            print(f"\n❌ Terminal does not support divine emojis")
            return False
    
    print(f"\n✅ The gods' emojis are properly displayed!")
    return True


# Initialize divine encoding when module is imported
if configure_divine_encoding():
    divine_print("Sacred encoding configuration loaded successfully!")