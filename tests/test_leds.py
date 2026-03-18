"""
Test script for WS2812B LEDs
Demonstrates rainbow and sunrise effects
"""

from machine import Pin
import neopixel
import time

NUM_LEDS = 5
DATA_PIN = 27

# Initialize LEDs
leds = neopixel.NeoPixel(Pin(DATA_PIN), NUM_LEDS)

def clear():
    for i in range(NUM_LEDS):
        leds[i] = (0, 0, 0)
    leds.write()

def set_all(r, g, b):
    for i in range(NUM_LEDS):
        leds[i] = (r, g, b)
    leds.write()

print("WS2812B LED Test")

# Test 1: Individual colors
print("Test 1: Red")
set_all(255, 0, 0)
time.sleep(1)

print("Test 2: Green")
set_all(0, 255, 0)
time.sleep(1)

print("Test 3: Blue")
set_all(0, 0, 255)
time.sleep(1)

# Test 4: Sunrise simulation
print("Test 4: Sunrise effect (10 seconds)")
for i in range(100):
    progress = i / 100.0
    
    if progress < 0.25:
        brightness = int(progress * 4 * 255)
        r, g, b = brightness // 2, 0, 0
    elif progress < 0.5:
        stage = (progress - 0.25) * 4
        r = 128 + int(stage * 127)
        g = int(stage * 100)
        b = 0
    elif progress < 0.75:
        stage = (progress - 0.5) * 4
        r = 255
        g = 100 + int(stage * 155)
        b = 0
    else:
        stage = (progress - 0.75) * 4
        r = 255
        g = 255
        b = int(stage * 255)
    
    set_all(r, g, b)
    time.sleep(0.1)

time.sleep(1)
clear()
print("LED test complete!")
