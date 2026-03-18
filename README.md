# ESP32 Alarm Clock - MicroPython Implementation

A feature-rich alarm clock using ESP32 D1 Mini with sunrise simulation and MP3 playback.

## Features

- ✅ **Sunrise Alarm**: 10-minute gradual LED brightening with color transition (red → orange → yellow → white)
- ✅ **6 Sound Options**: Birds, siren, cockerel, bell, bird 2, pop — with 5-second preview and gradual volume increase
- ✅ **User-Friendly Menu**: Navigate and configure everything on-device with rotary encoder
- ✅ **Snooze Function**: Touch sensor pauses alarm, resumes from where it left off
- ✅ **Night Light**: Touch snooze in the dark for 30 s of full-white LEDs, then a 10 s fade
- ✅ **Auto-Brightness**: Display brightness adjusts to ambient light via EMA-smoothed sensor
- ✅ **Persistent Settings**: Alarm time, on/off, sound choice, and LED toggle saved to flash
- ✅ **RTC Timekeeping**: Accurate DS3231 real-time clock (I2C-resilient, reads once per minute)
- ✅ **Sunrise LED Toggle**: Enable or disable the LED sunrise effect independently of the alarm sound

## Hardware Components

| Component | Model | GPIO Pins |
|-----------|-------|-----------|
| Microcontroller | ESP32 D1 Mini | - |
| Display | TM1637 7-Segment | CLK: 18, DIO: 19 |
| RTC | DS3231 | SDA: 21, SCL: 22 |
| MP3 Player | DFPlayer Mini | TX: 17, RX: 16 |
| LED Strip | WS2812B (5 LEDs) | DATA: 27 |
| Input | KY-040 Rotary Encoder | CLK: 32, DT: 25, SW: 15 |
| Touch Snooze | ESP32 Touch | GPIO4 (T0) |
| Touch Stop | ESP32 Touch | GPIO0 (T1) |
| Light Sensor | Analog | GPIO36 (ATTN_0DB) |

## Installation

### 1. Install MicroPython on ESP32

Download the latest MicroPython firmware for ESP32 from [micropython.org](https://micropython.org/download/esp32/)

Flash the firmware:
```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

### 2. Upload Files to ESP32

Use `mpremote` (recommended) or `ampy`/`rshell`:

**Required files:**
- `main.py` - Main program
- `config.py` - Configuration and pin assignments
- `tm1637.py` - Display driver
- `ds3231.py` - RTC driver
- `dfplayer.py` - MP3 player driver
- `rotary_encoder.py` - Rotary encoder driver

**Example using mpremote:**
```bash
cd src/
mpremote connect /dev/ttyUSB0 cp config.py :config.py
mpremote connect /dev/ttyUSB0 cp tm1637.py :tm1637.py
mpremote connect /dev/ttyUSB0 cp ds3231.py :ds3231.py
mpremote connect /dev/ttyUSB0 cp dfplayer.py :dfplayer.py
mpremote connect /dev/ttyUSB0 cp rotary_encoder.py :rotary_encoder.py
mpremote connect /dev/ttyUSB0 cp main.py :main.py
```

### 3. Prepare SD Card for DFPlayer

Format as FAT32 and place MP3 files directly in the root or `/mp3/` folder:
```
SD Card/
└── mp3/
    ├── 0001.mp3  (Birds)
    ├── 0002.mp3  (Siren)
    ├── 0003.mp3  (Cockerel)
    ├── 0004.mp3  (Bell)
    ├── 0005.mp3  (Bird 2)
    └── 0006.mp3  (Pop)
```

⚠️ **Important**:
- Files must be named `0001.mp3`, `0002.mp3`, etc.
- Use FAT32 format for SD card
- MP3 files should be 8-48kHz, mono or stereo

## Usage

### Menu Navigation

The alarm clock has 5 menu items, navigated with the rotary encoder:

| Position | Display | Function | Action |
|----------|---------|----------|--------|
| 0 | `ALRM` | Set alarm time | Click → rotate hours → click → rotate minutes → click to save |
| 1 | `ON-F` | Toggle alarm on/off | Click to toggle; display shows ` ON ` or `OFF `, LEDs flash green/red |
| 2 | `SOND` | Change sound type | Click to cycle: BIRD → SIRN → COCK → BELL → BRD2 → POP; plays 5 s preview |
| 3 | `CLOC` | Set current time | Click → rotate hours → click → rotate minutes → click to save to RTC |
| 4 | `LED ` | Toggle sunrise LEDs | Click to enable/disable LED sunrise effect independently of sound |

**Controls:**
- **Rotate encoder**: Navigate menu / adjust value when editing
- **Click encoder**: Enter menu / confirm / advance to next field
- **Touch Snooze** (GPIO4): Snooze alarm for 5 min; or trigger night light when alarm is off and it's dark
- **Touch Stop** (GPIO0): Stop alarm completely
- **Menu timeout**: Returns to time display after 5 seconds of inactivity

### Setting the Alarm (Current Version)

In this version, you need to edit the alarm time in code or via the REPL:

### Setting the Alarm

Use the `ALRM` menu item with the rotary encoder — no REPL needed.

If you need to set it via REPL:
```python
>>> from main import alarm_clock
>>> alarm_clock.alarm_hour = 7
>>> alarm_clock.alarm_minute = 30
>>> alarm_clock.alarm_enabled = True
>>> alarm_clock.save_settings()
```

### Setting Current Time

Use the `CLOC` menu item with the rotary encoder — no REPL needed.

First-time setup via REPL (if RTC has never been set):
```python
>>> from machine import I2C, Pin
>>> from ds3231 import DS3231
>>> i2c = I2C(0, scl=Pin(22), sda=Pin(21))
>>> rtc = DS3231(i2c)
>>> rtc.set_time(2026, 3, 18, 3, 7, 30, 0)  # year, month, day, weekday, hour, min, sec
```

## Alarm Sequence

When the alarm triggers:

1. **Start** (00:00): LEDs begin at dark red, sound starts at low volume (configurable per track)
2. **Progress** (00:00-10:00):
   - LEDs gradually brighten: red → orange → yellow → white (if LED sunrise enabled)
   - Sound volume gradually increases up to `DFPLAYER_VOLUME_MAX`
3. **Peak** (10:00+): Full brightness and volume maintained; sound loops automatically
4. **Snooze**: Pauses sound and LEDs; resumes from the same point in the sunrise after 5 min
5. **Max duration**: Alarm auto-stops after 30 minutes if not manually stopped

## Night Light

Touch the **snooze pad (GPIO4)** when the alarm is not active and the room is dark:
- LEDs light up full white for 30 seconds
- Then fade out over 10 seconds
- Only activates below the configured light threshold (default EMA < 80)

## Troubleshooting

### Display shows INIT and hangs
- The RTC I2C bus may be stuck — **unplug and replug USB** for a full power cycle

### Display shows 00:00 after boot
- RTC not found or time not yet set — use `CLOC` menu to set the time

### RTC not keeping time
- Check I2C connections (SDA=21, SCL=22)
- Verify coin cell battery is installed in DS3231 module

### DFPlayer not playing
- Check UART connections (TX→RX, RX→TX cross-wired)
- Verify SD card is FAT32 formatted
- Ensure MP3 files are named `0001.mp3` through `0006.mp3`

### Touch sensors not responding
- Touch thresholds are in `config.py` (`TOUCH_THRESHOLD_MIN/MAX`)
- Test touch values with `tests/test_touch.py`

### Night light not triggering
- Room may be too bright — cover the light sensor or adjust `NIGHT_LIGHT_THRESHOLD` in `config.py`

### LEDs not lighting
- Verify WS2812B data pin (GPIO27)
- Check 5V power supply (WS2812B requires 5V, not 3.3V)

## Future Enhancements

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
