# ESP32 Alarm Clock - Installation Guide

## Prerequisites

1. **Hardware**: ESP32 D1 Mini with all components soldered
2. **USB Cable**: USB to micro-USB cable for programming
3. **Python**: Python 3.7+ installed on your computer
4. **Tools**: esptool and ampy (or alternative like Thonny IDE)

## Step-by-Step Installation

### 1. Install Required Tools

Install tools needed for flashing and uploading files.

**Alternative**: Use [Thonny IDE](https://thonny.org/) which includes MicroPython support.

### 2. Download MicroPython Firmware

Get the latest ESP32 firmware from: https://micropython.org/download/esp32/

For ESP32 D1 Mini, download the generic ESP32 firmware.

### 3. Flash MicroPython to ESP32

**Find your serial port:**
- Linux: /dev/ttyUSB0 or /dev/ttyACM0
- macOS: /dev/tty.usbserial-* or /dev/cu.usbserial-*
- Windows: COM3, COM4, etc.

**Erase flash and install firmware using esptool**

### 4. Upload Alarm Clock Files

**Upload all Python files to your ESP32:**
- config.py
- tm1637.py
- ds3231.py
- dfplayer.py
- rotary_encoder.py
- main.py

**Optional test scripts:**
- test_display.py
- test_rtc.py
- test_touch.py
- test_encoder.py
- test_leds.py

### 5. Prepare DFPlayer SD Card

1. **Format SD card** as FAT32
2. **Create folder structure:**
   ```
   SD Card/
   └── mp3/
       ├── 0001.mp3
       ├── 0002.mp3
       └── 0003.mp3
   ```
3. **Copy your MP3 files** with exact naming: 0001.mp3, 0002.mp3, etc.
4. **Insert SD card** into DFPlayer Mini module

**MP3 Requirements:**
- Format: MP3
- Sample rate: 8kHz - 48kHz
- Channels: Mono or Stereo
- Max file size: ~4GB

### 6. Set Initial Time on RTC

Connect via serial terminal and run:

```python
from machine import I2C, Pin
from ds3231 import DS3231

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
rtc = DS3231(i2c)

# Set time: (year, month, day, weekday, hour, minute, second)
# weekday: 1=Monday, 2=Tuesday, ..., 7=Sunday
rtc.set_time(2026, 3, 18, 3, 7, 30, 0)

# Verify
print(rtc.format_time())
```

### 7. Test Hardware Components

Run individual test scripts to verify each component works.

### 8. Run the Alarm Clock

The main program will start automatically if named main.py or boot.py.

## Troubleshooting

### Can't connect to ESP32
- Press the RESET button on ESP32
- Try a different USB cable (some are charge-only)
- Check driver installation (CP2102, CH340)
- Try a different USB port

### Display shows nothing
- Check wiring: CLK=18, DIO=19
- Verify 3.3V power
- Run test_display.py

### RTC not found
- Check I2C wiring: SDA=21, SCL=22
- Verify I2C address with i2c.scan() should show [104] (0x68)
- Check DS3231 power and battery

### DFPlayer not playing
- Verify SD card is FAT32
- Check MP3 file naming (must be 0001.mp3, not 001.mp3 or 1.mp3)
- Verify UART connections: ESP TX(17)→DFPlayer RX, ESP RX(16)→DFPlayer TX
- Check speaker connection

### Touch sensors always triggered
- Adjust thresholds in config.py
- Run test_touch.py to see actual values

### LEDs not working
- Check data pin: GPIO27
- WS2812B requires 5V power (not 3.3V)
- Verify common ground between ESP32 and LED strip

## Default Settings

- Alarm time: 07:00
- Alarm enabled: False
- Sound type: 1 (Birds)
- Sunrise duration: 10 minutes
- Snooze duration: 5 minutes
- Menu timeout: 5 seconds

Good luck with your alarm clock! 🕐☀️
