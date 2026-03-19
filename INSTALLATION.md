# Installation Guide

## Prerequisites

- ESP32 D1 Mini with all components connected
- USB–micro-USB cable
- Python 3.7+ on your computer
- `esptool` and `mpremote` (install via pip):

```bash
pip install esptool mpremote
```

---

## 1. Flash MicroPython

Download the latest generic ESP32 firmware from [micropython.org/download/esp32](https://micropython.org/download/esp32/).

```bash
# Erase flash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

# Flash firmware
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

**Serial port by OS:**
- Linux: `/dev/ttyUSB0` (run `sudo chmod a+rw /dev/ttyUSB0` if permission denied)
- macOS: `/dev/cu.usbserial-*`
- Windows: `COM3`, `COM4`, etc.

---

## 2. Upload Source Files

From the `py-alarm/` project root:

```bash
source ~/venv/alarm/bin/activate   # if using a venv

mpremote connect /dev/ttyUSB0 cp src/config.py         :config.py
mpremote connect /dev/ttyUSB0 cp src/tm1637.py          :tm1637.py
mpremote connect /dev/ttyUSB0 cp src/ds3231.py          :ds3231.py
mpremote connect /dev/ttyUSB0 cp src/dfplayer.py        :dfplayer.py
mpremote connect /dev/ttyUSB0 cp src/rotary_encoder.py  :rotary_encoder.py
mpremote connect /dev/ttyUSB0 cp src/main.py            :main.py
mpremote connect /dev/ttyUSB0 reset
```

---

## 3. Prepare the SD Card

Format as **FAT32** and create an `mp3/` folder with these files:

```
/mp3/0001.mp3   Birds (default)
/mp3/0002.mp3   Siren
/mp3/0003.mp3   Cockerel
/mp3/0004.mp3   Bell
/mp3/0005.mp3   Bird 2
/mp3/0006.mp3   Pop
```

Files **must** be named exactly `0001.mp3`, `0002.mp3`, etc. Insert the card into the DFPlayer Mini before powering on.

**MP3 requirements:** 8–48 kHz, mono or stereo, 128–320 kbps recommended.

---

## 4. First Boot

On the first power-on, the display may show `bAt?` for 3 seconds if the RTC has never been set (or if the DS3231 backup battery is flat). This is normal — use the **CLOC** menu item to set the correct time directly on the device.

If you prefer to set the time via REPL (e.g. on first-ever boot before any menu interaction):

```python
from machine import I2C, Pin
from ds3231 import DS3231
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
rtc = DS3231(i2c)
rtc.set_time(2026, 3, 19, 4, 8, 0, 0)  # year, month, day, weekday, hour, min, sec
print(rtc.format_time())  # verify
```

---

## 5. Test Individual Components

Optional but recommended before first run:

```bash
mpremote connect /dev/ttyUSB0 run tests/test_display.py
mpremote connect /dev/ttyUSB0 run tests/test_rtc.py
mpremote connect /dev/ttyUSB0 run tests/test_dfplayer.py
mpremote connect /dev/ttyUSB0 run tests/test_encoder.py
mpremote connect /dev/ttyUSB0 run tests/test_leds.py
mpremote connect /dev/ttyUSB0 run tests/test_light_sensor.py
mpremote connect /dev/ttyUSB0 run tests/test_touch.py
```

---

## Troubleshooting

### Can't connect / permission denied
- Run `sudo chmod a+rw /dev/ttyUSB0` (Linux)
- Try a different USB cable — some are charge-only
- Check USB driver: CP2102 or CH340 depending on your board variant

### Display blank
- Check wiring: CLK = GPIO 18, DIO = GPIO 19
- Run `test_display.py` to verify

### RTC not found (`ERR` in CLOC menu)
- Verify I2C wiring: SDA = GPIO 21, SCL = GPIO 22
- Run `i2c.scan()` in REPL — should return `[104]` (0x68)
- Check DS3231 power supply

### No sound
- Verify SD card is FAT32 formatted
- File names must be exactly `0001.mp3`, not `1.mp3` or `001.mp3`
- UART wiring is cross-connected: ESP TX (17) → DFPlayer RX; ESP RX (16) → DFPlayer TX
- Run `test_dfplayer.py` to verify

### LEDs not lighting
- WS2812B requires **5 V** — GPIO 27 for data is fine, but power must be 5 V
- Check common ground between ESP32 and LED strip

### Touch sensors not responding
- Run `test_touch.py` to see raw values
- Adjust `TOUCH_THRESHOLD_MIN` / `TOUCH_THRESHOLD_MAX` in `config.py` to match
- GPIO 0 (stop pad) is known to be unreliable when I2C is active — use encoder button click to stop the alarm instead

### Night light not triggering
- Run `test_light_sensor.py` to see the current EMA reading
- Lower `NIGHT_LIGHT_THRESHOLD` in `config.py` if the room is borderline bright


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
