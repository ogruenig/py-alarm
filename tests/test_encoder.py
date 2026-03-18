"""
Test script for rotary encoder
Displays rotation and button clicks
"""

from rotary_encoder import RotaryEncoder
import time

# Initialize encoder
encoder = RotaryEncoder(
    clk_pin=32,
    dt_pin=25,
    sw_pin=15
)

print("Rotary Encoder Test")
print("Rotate encoder and press button...")
print("-" * 40)

position = 0

try:
    while True:
        rotation = encoder.get_rotation()
        clicked = encoder.get_click()
        
        if rotation != 0:
            position += rotation
            direction = "CW " if rotation > 0 else "CCW"
            print(f"Rotation: {direction}  Position: {position:4d}")
        
        if clicked:
            print("Button CLICKED!")
        
        time.sleep(0.01)
        
except KeyboardInterrupt:
    print("\nTest stopped")
