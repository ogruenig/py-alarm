"""
Test script for TM1637 display
Tests all segments and time display
"""

from machine import Pin
from tm1637 import TM1637
import time

# Initialize display
clk = Pin(18)
dio = Pin(19)
display = TM1637(clk, dio)

print("Testing TM1637 Display...")

# Test 1: Show INIT
print("Test 1: Showing 'INIT'")
display.show("INIT")
time.sleep(2)

# Test 2: Count 0-9
print("Test 2: Counting 0-9")
for i in range(10):
    display.show(f"{i:04d}")
    time.sleep(0.5)

# Test 3: Show time with colon
print("Test 3: Time display 12:34")
display.show_time(12, 34, colon=True)
time.sleep(2)

# Test 4: Brightness levels
print("Test 4: Brightness test")
for brightness in range(8):
    display.brightness(brightness)
    display.show(f"BR{brightness:02d}")
    time.sleep(0.5)

# Test 5: Scroll text
print("Test 5: Scrolling text")
display.brightness(5)
display.scroll("HELLO WORLD")

print("Display test complete!")
