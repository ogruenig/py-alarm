"""
Test script for light sensor on GPIO 36 (ADC)
Cover/uncover the sensor and watch the values change.
Typical range: dark ~50-200, bright ~2000-3000+
"""

from machine import Pin, ADC
import time

sensor = ADC(Pin(36))
sensor.atten(ADC.ATTN_11DB)  # Full range 0-3.3V -> 0-4095

print("Light Sensor Test (GPIO 36)")
print("Cover the sensor with your hand to see values drop.")
print("Shine a light on it to see values rise.")
print("Press Ctrl+C to stop.")
print("-" * 40)

try:
    while True:
        value = sensor.read()
        voltage = value / 4095 * 3.3
        bar = "#" * (value // 100)
        print(f"ADC: {value:5d}  ({voltage:.2f}V)  {bar}", end="\r")
        time.sleep(0.2)
except KeyboardInterrupt:
    print("\nLight sensor test stopped.")
    print(f"Last reading: {sensor.read()}")
