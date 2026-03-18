"""
Test script for DS3231 RTC
Reads and displays current time
"""

from machine import I2C, Pin
from ds3231 import DS3231
import time

# Initialize I2C and RTC
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
print("I2C devices found:", [hex(addr) for addr in i2c.scan()])

rtc = DS3231(i2c)

print("DS3231 RTC Test")
print("-" * 40)

try:
    while True:
        # Get time
        dt = rtc.get_time()
        year, month, day, weekday, hour, minute, second = dt
        
        # Get temperature
        temp = rtc.get_temperature()
        
        # Format and display
        date_str = f"{year:04d}-{month:02d}-{day:02d}"
        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
        weekdays = ['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        print(f"{date_str} {weekdays[weekday]} {time_str}  Temp: {temp:.2f}°C", end='\r')
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nTest stopped")
    
print("\nTo set time, use:")
print("rtc.set_time(2026, 3, 18, 3, 7, 30, 0)")
print("           (year, month, day, weekday, hour, min, sec)")
