"""
Test script for touch sensors
Reads and displays touch values
"""

from machine import Pin, TouchPad
import time

# Initialize touch sensors
touch_snooze = TouchPad(Pin(4))  # T0
touch_stop = TouchPad(Pin(0))    # T1

print("Touch Sensor Test")
print("Touch the sensors to see values...")
print("Typical range: untouched >100, touched <20")
print("-" * 40)

try:
    while True:
        val1 = touch_snooze.read()
        val2 = touch_stop.read()
        
        status1 = "TOUCHED" if 5 < val1 < 20 else "       "
        status2 = "TOUCHED" if 5 < val2 < 20 else "       "
        
        print(f"Snooze (T0): {val1:4d} {status1}  |  Stop (T1): {val2:4d} {status2}", end='\r')
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\nTest stopped")
