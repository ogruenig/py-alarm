# ESP32 Alarm Clock - MicroPython Implementation

A feature-rich alarm clock using ESP32 D1 Mini with sunrise simulation and MP3 playback.

## Features

- ✅ **Sunrise Alarm**: 10-minute gradual LED brightening with color transition (red → orange → yellow → white)
- ✅ **Sound Options**: Multiple alarm sounds (birds, ringing, etc.) with gradual volume increase
- ✅ **User-Friendly Menu**: Navigate with rotary encoder
- ✅ **Snooze Function**: Touch sensor for 5-minute snooze
- ✅ **Auto-Brightness**: Display brightness adjusts based on ambient light
- ✅ **Persistent Settings**: Alarm settings saved to flash memory
- ✅ **RTC Timekeeping**: Accurate DS3231 real-time clock

## Hardware Components

| Component | Model | GPIO Pins |
|-----------|-------|-----------|
| Microcontroller | ESP32 D1 Mini | - |
| Display | TM1637 7-Segment | CLK: 18, DIO: 19 |
| RTC | DS3231 | SDA: 21, SCL: 22 |
| MP3 Player | DFPlayer Mini | TX: 17, RX: 16 |
| LED Strip | WS2812B (5 LEDs) | DATA: 27 |
| Input | KY-040 Rotary Encoder | CLK: 32, DT: 25, SW: 15 |
| Touch Sensors | ESP32 Touch | Snooze: GPIO4 (T0), Stop: GPIO0 (T1) |
| Light Sensor | Analog | GPIO36 |

## Installation

### 1. Install MicroPython on ESP32

Download the latest MicroPython firmware for ESP32 from [micropython.org](https://micropython.org/download/esp32/)

Flash the firmware:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

### 2. Upload Files to ESP32

Use `ampy`, `rshell`, or Thonny IDE to upload the following files:

**Required files:**
- `main.py` - Main program
- `config.py` - Configuration and pin assignments
- `tm1637.py` - Display driver
- `ds3231.py` - RTC driver
- `dfplayer.py` - MP3 player driver
- `rotary_encoder.py` - Rotary encoder driver

**Example using ampy:**
```bash
ampy --port /dev/ttyUSB0 put config.py
ampy --port /dev/ttyUSB0 put tm1637.py
ampy --port /dev/ttyUSB0 put ds3231.py
ampy --port /dev/ttyUSB0 put dfplayer.py
ampy --port /dev/ttyUSB0 put rotary_encoder.py
ampy --port /dev/ttyUSB0 put main.py
```

### 3. Prepare SD Card for DFPlayer

Create folders on the SD card:
```
SD Card/
└── mp3/
    ├── 0001.mp3  (Birds singing)
    ├── 0002.mp3  (Ringing alarm)
    └── 0003.mp3  (Beeping sound)
```

⚠️ **Important**: 
- Files must be named `0001.mp3`, `0002.mp3`, etc.
- Use FAT32 format for SD card
- MP3 files should be 8-48kHz, mono or stereo

## Usage

### Menu Navigation

The alarm clock has 5 menu items, navigated with the rotary encoder:

| Menu | Display | Function | Action |
|------|---------|----------|--------|
| 0 | `TIME` | Show current time | Default view |
| 1 | `ALRM` | Set alarm time | Click to enter (not yet implemented) |
| 2 | `ON-F` | Toggle alarm on/off | Click to toggle |
| 3 | `SOND` | Change sound type | Click to cycle sounds |
| 4 | `CLOC` | Set current time | Click to enter (not yet implemented) |

**Controls:**
- **Rotate encoder**: Navigate menu items
- **Click encoder**: Select/confirm menu item
- **Touch Snooze** (GPIO4): Snooze alarm for 5 minutes
- **Touch Stop** (GPIO0): Stop alarm completely
- **Menu timeout**: Returns to time display after 5 seconds of inactivity

### Setting the Alarm (Current Version)

In this version, you need to edit the alarm time in code or via the REPL:

```python
# Connect via serial terminal
>>> from main import alarm_clock
>>> alarm_clock.alarm_hour = 7
>>> alarm_clock.alarm_minute = 30
>>> alarm_clock.alarm_enabled = True
>>> alarm_clock.save_settings()
```

📝 **Note**: Interactive alarm setting via rotary encoder is planned for future implementation.

### Setting Current Time

Set the RTC time via REPL:

```python
>>> from machine import I2C, Pin
>>> from ds3231 import DS3231
>>> i2c = I2C(0, scl=Pin(22), sda=Pin(21))
>>> rtc = DS3231(i2c)
>>> rtc.set_time(2026, 3, 18, 3, 7, 30, 0)  # year, month, day, weekday, hour, min, sec
```

## Alarm Sequence

When the alarm triggers:

1. **Start** (00:00): LEDs begin at dark red, sound starts at minimum volume
2. **Progress** (00:00-10:00): 
   - LEDs gradually brighten: red → orange → yellow → white
   - Sound volume gradually increases from 0 to 30
3. **Peak** (10:00+): Full brightness and volume maintained
4. **Max duration**: Alarm auto-stops after 30 minutes if not manually stopped

## Troubleshooting

### Display not working
- Check I2C connections (CLK=18, DIO=19)
- Verify 3.3V power supply
- Test with: `test_display.py`

### RTC not keeping time
- Check I2C address (should be 0x68)
- Verify battery is installed on DS3231
- Set time manually via REPL

### DFPlayer not playing
- Check UART connections (TX→RX, RX→TX)
- Verify SD card is FAT32 formatted
- Ensure MP3 files are correctly named (0001.mp3, etc.)
- Check speaker/audio output

### Touch sensors not responding
- Touch thresholds may need adjustment in `config.py`
- Test touch values with: `test_touch.py`

### LEDs not lighting
- Verify WS2812B data pin (GPIO27)
- Check 5V power supply (WS2812B requires 5V)
- Ensure proper ground connection

## Future Enhancements

- [ ] Interactive alarm time setting via rotary encoder
- [ ] Interactive clock time setting
- [ ] Multiple alarm slots
- [ ] Weekday-specific alarms
- [ ] WiFi/NTP time synchronization
- [ ] Fade-out alarm sound option
- [ ] Customizable sunrise duration
- [ ] Display date in menu
- [ ] Temperature display (from DS3231 sensor)

## File Structure

```
ESP32 Alarm Clock/
├── main.py                 # Main program loop
├── config.py              # Pin assignments and constants
├── tm1637.py              # TM1637 display driver
├── ds3231.py              # DS3231 RTC driver
├── dfplayer.py            # DFPlayer Mini driver
├── rotary_encoder.py      # Rotary encoder handler
├── test_display.py        # Display test script
├── test_touch.py          # Touch sensor test script
└── alarm_settings.json    # Saved settings (auto-generated)
```

## License

This project is open source. Feel free to modify and adapt for your needs.

## Credits

- TM1637 driver inspired by mcauser/micropython-tm1637
- DS3231 RTC implementation
- DFPlayer protocol based on DFRobot specifications

---

**Project Date**: March 2026  
**MicroPython Version**: 1.20+  
**Hardware**: ESP32 D1 Mini
