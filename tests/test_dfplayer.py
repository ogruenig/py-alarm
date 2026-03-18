"""
Test script for DFPlayer Mini
Tests connection, queries file count, and plays tracks.
UART1: TX=17 (ESP->DFPlayer RX), RX=16 (ESP->DFPlayer TX)
"""

from machine import UART
from dfplayer import DFPlayer
import time

print("DFPlayer Mini Test")
print("-" * 40)

# Init UART and DFPlayer (reset is sent in constructor)
uart = UART(1, baudrate=9600, tx=17, rx=16)
print("Initializing DFPlayer (takes ~1 second)...")
player = DFPlayer(uart)
print("DFPlayer initialized.")

# Query number of files on SD card
# Command 0x48 = query SD card file count
print("\nQuerying SD card file count...")
player._send_command(0x09, 0x00, 0x02)  # Select SD card as source
time.sleep(0.5)

# Try playing each of the first 3 tracks at moderate volume
print("\nTest 1: Volume control")
for vol in [5, 15, 25, 15]:
    player.volume(vol)
    print(f"  Volume set to {vol}")
    time.sleep(0.3)

print("\nTest 2: Play track 1 at volume 20 (5 seconds)")
player.volume(20)
player.play(1)
time.sleep(5)

print("Test 3: Pause")
player.pause()
time.sleep(1)

print("Test 4: Resume")
player.resume()
time.sleep(3)

print("Test 5: Stop")
player.stop()
time.sleep(0.5)

print("\nTest 6: Play track 2 (if it exists, 3 seconds)")
player.play(2)
time.sleep(3)
player.stop()
time.sleep(0.5)

print("\nTest 7: Play track 3 (if it exists, 3 seconds)")
player.play(3)
time.sleep(3)
player.stop()

print("\nDFPlayer test complete!")
print("If you heard audio, the DFPlayer is working correctly.")
print("If silent, check: SD card inserted? Files named 0001.mp3, 0002.mp3?")
