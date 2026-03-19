# 🌅 ESP32 Sunrise Alarm Clock

A sunrise alarm clock built with ESP32 and MicroPython. Simulates a natural sunrise with gradual LED color transitions and MP3 audio — fully configurable on-device via rotary encoder.

![MicroPython](https://img.shields.io/badge/MicroPython-1.24.1-blue)
![ESP32](https://img.shields.io/badge/ESP32-D1%20Mini-green)
![License](https://img.shields.io/badge/license-MIT-blue)

**Setup:** see [INSTALLATION.md](INSTALLATION.md) · **Technical design:** see [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)

---

## Features

- **Sunrise simulation** — 10-minute LED transition: dark red → orange → yellow → white
- **6 MP3 alarm sounds** — with 5-second in-menu preview and gradual volume increase
- **On-device menu** — set alarm time, on/off, sound, clock, and LED toggle with the rotary encoder
- **Snooze** — resumes from the same LED/volume point after 5 minutes
- **Night light** — touch snooze pad in the dark for 30 s of white LEDs, then 10 s fade
- **Auto-brightness** — display adjusts to ambient light (EMA-smoothed)
- **Persistent settings** — saved to flash; survive power cuts
- **Accurate timekeeping** — DS3231 RTC (battery-backed); time extrapolated between reads
- **Power-loss detection** — shows `bAt?` on boot if the RTC backup battery is flat

---

## Hardware

| Component | Model | GPIO |
|-----------|-------|------|
| Microcontroller | ESP32 D1 Mini | — |
| Display | TM1637 7-segment | CLK: 18, DIO: 19 |
| RTC | DS3231 | SDA: 21, SCL: 22 |
| MP3 Player | DFPlayer Mini | TX: 17, RX: 16 |
| LED Strip | WS2812B (5 LEDs) | DATA: 27 |
| Encoder | KY-040 | CLK: 32, DT: 25, SW: 15 |
| Touch Snooze | ESP32 Touch | GPIO 4 |
| Touch Stop | ESP32 Touch | GPIO 0 |
| Light Sensor | Analog | GPIO 36 |

> WS2812B requires **5 V** — do not power from the ESP32's 3.3 V pin.

---

## Files

```
src/                    Upload all to ESP32
  main.py               Main program
  config.py             Pin assignments and constants
  tm1637.py             Display driver
  ds3231.py             RTC driver
  dfplayer.py           DFPlayer Mini driver
  rotary_encoder.py     Rotary encoder driver

tests/                  Optional hardware verification scripts
  test_display.py
  test_dfplayer.py
  test_encoder.py
  test_leds.py
  test_light_sensor.py
  test_rtc.py
  test_touch.py

docs/
  SYSTEM_ARCHITECTURE.md

CHANGELOG.md
INSTALLATION.md
LICENSE
requirements.txt        Host tools: esptool, mpremote
```

---

## Usage

### Controls

| Input | Alarm inactive | Alarm active |
|-------|---------------|--------------|
| Rotate encoder | Navigate menu / adjust value | Ignored |
| Click encoder | Enter / confirm / next field | **Stop alarm** |
| Touch GPIO 4 | Night light (if dark) | Snooze 5 min |
| Touch GPIO 0 | — | Stop alarm |

The menu returns to the time display after **5 seconds** of inactivity.

### Menu

| # | Display | Function | Interaction |
|---|---------|----------|-------------|
| 0 | `ALRM` | Set alarm time | Click → rotate hours → click → rotate minutes → click to save |
| 1 | `ON-F` | Alarm on/off | Click → rotate to toggle (LEDs: green = ON, red = OFF) → click to save |
| 2 | `SOND` | Alarm sound | Click → rotate to scroll sounds (plays 5 s preview) → click to save |
| 3 | `CLOC` | Set clock time | Click → rotate hours → click → rotate minutes → click to save |
| 4 | `LED ` | Sunrise LEDs on/off | Click → rotate to toggle → click to save |

### Alarm sequence

1. LEDs start at dark red; sound plays at low volume
2. Over 10 minutes: LEDs fade to white; volume ramps to maximum
3. After 10 min: full brightness and volume; track loops
4. **Snooze** (touch GPIO 4): pauses for 5 min, then resumes from the same point
5. **Stop** (click encoder): stops immediately
6. Auto-stop after 30 minutes

### Persistent settings

Saved to `alarm_settings.json` on the ESP32 flash:

| Setting | Menu | Default |
|---------|------|---------|
| Alarm hour & minute | `ALRM` | 07:00 |
| Alarm enabled | `ON-F` | off |
| Sound type (0–5) | `SOND` | 0 (BIRD) |
| Sunrise LEDs enabled | `LED ` | on |

The clock time is held by the DS3231 RTC with its own CR2032 battery backup.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `bAt?` on boot | Replace CR2032 on DS3231; set time via CLOC |
| `00:00` on boot | RTC not set — use CLOC menu |
| Clock wrong after power loss | RTC battery dead — replace CR2032 |
| Stuck on `INIT` | Unplug and replug USB (I2C bus locked) |
| No sound | Check SD card: FAT32, files must be `0001.mp3`–`0006.mp3` |
| Night light not triggering | Room too bright — lower `NIGHT_LIGHT_THRESHOLD` in `config.py` |
| LEDs not lighting | Check 5 V supply to WS2812B |
| Touch snooze unresponsive | Run `test_touch.py`; adjust `TOUCH_THRESHOLD_MIN/MAX` in `config.py` |

---

## Configuration

Key constants in `src/config.py`:

| Constant | Default | Purpose |
|----------|---------|----------|
| `SUNRISE_DURATION` | 600 s | Alarm ramp-up duration |
| `SNOOZE_DURATION` | 300 s | Snooze length |
| `ALARM_MAX_DURATION` | 1800 s | Auto-stop after this time |
| `MENU_TIMEOUT` | 5000 ms | Menu idle timeout |
| `NIGHT_LIGHT_ON_DURATION` | 30 s | Night light full-on time |
| `NIGHT_LIGHT_DIM_DURATION` | 10 s | Night light fade duration |
| `NIGHT_LIGHT_THRESHOLD` | 80 | EMA below which night light activates |
| `DFPLAYER_VOLUME_MAX` | 25 | Maximum alarm volume (0–30) |

---

## License

MIT — see [LICENSE](LICENSE).


## Features

- **Sunrise Simulation** — 10-minute gradual LED transition: dark red → orange → yellow → white
- **6 MP3 Alarm Sounds** — Birds, siren, cockerel, bell, bird 2, pop; with 5-second in-menu preview
- **Gradual Volume Increase** — Synchronized with LED brightness
- **On-Device Menu** — Configure everything with the rotary encoder; no computer needed
- **Snooze** — Touch pad pauses alarm and resumes from the same point 5 minutes later
- **Stop** — Encoder button click stops alarm immediately
- **Night Light** — Touch the snooze pad in the dark for 30 s of white LEDs, then a 10 s fade
- **Auto-Brightness** — Display brightness adjusts to ambient light (EMA-smoothed)
- **Persistent Settings** — Alarm time, on/off, sound, and LED toggle saved to flash
- **Accurate Timekeeping** — DS3231 RTC with battery backup; time extrapolated between reads using `ticks_ms` for smooth second-by-second display
- **Power-loss Detection** — Shows `bAt?` on boot if the RTC backup battery is flat

---

## Hardware

| Component | Model | GPIO |
|-----------|-------|------|
| Microcontroller | ESP32 D1 Mini | — |
| Display | TM1637 7-segment | CLK: 18, DIO: 19 |
| RTC | DS3231 | SDA: 21, SCL: 22 |
| MP3 Player | DFPlayer Mini | TX: 17, RX: 16 |
| LED Strip | WS2812B (5 LEDs) | DATA: 27 |
| Encoder | KY-040 Rotary Encoder | CLK: 32, DT: 25, SW: 15 |
| Touch Snooze | ESP32 Touch Pad | GPIO 4 |
| Touch Stop | ESP32 Touch Pad | GPIO 0 (unreliable — use encoder button instead) |
| Light Sensor | Analog | GPIO 36 (ATTN_0DB) |

> **WS2812B power**: The LED strip requires 5 V. Do not power it from the ESP32's 3.3 V pin.

---

## File Structure

```
py-alarm/
├── src/                        Upload all of these to the ESP32
│   ├── main.py                 Main program (AlarmClock class + run loop)
│   ├── config.py               Pin assignments, constants, sound list
│   ├── tm1637.py               TM1637 display driver
│   ├── ds3231.py               DS3231 RTC driver
│   ├── dfplayer.py             DFPlayer Mini MP3 driver
│   └── rotary_encoder.py       Interrupt-based rotary encoder driver
│
├── tests/                      Optional hardware test scripts
│   ├── test_display.py
│   ├── test_rtc.py
│   ├── test_touch.py
│   ├── test_encoder.py
│   └── test_leds.py
│
├── docs/
│   └── SYSTEM_ARCHITECTURE.md  Technical design and data flow
│
├── CHANGELOG.md
├── INSTALLATION.md
├── LICENSE
└── requirements.txt            Host tools: esptool, mpremote

Generated on the device:
    alarm_settings.json         Saved settings (auto-created)
    error.log                   Exception log (if errors occur)
```

---

## Installation

### 1. Flash MicroPython

```bash
# Install tools (once)
pip install esptool mpremote

# Erase and flash (use the .bin from micropython.org/download/esp32/)
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

### 2. Upload Source Files

```bash
cd /path/to/py-alarm

# Fix serial port permissions if needed (Linux)
sudo chmod a+rw /dev/ttyUSB0

source ~/venv/alarm/bin/activate

mpremote connect /dev/ttyUSB0 cp src/config.py         :config.py
mpremote connect /dev/ttyUSB0 cp src/tm1637.py          :tm1637.py
mpremote connect /dev/ttyUSB0 cp src/ds3231.py          :ds3231.py
mpremote connect /dev/ttyUSB0 cp src/dfplayer.py        :dfplayer.py
mpremote connect /dev/ttyUSB0 cp src/rotary_encoder.py  :rotary_encoder.py
mpremote connect /dev/ttyUSB0 cp src/main.py            :main.py
mpremote connect /dev/ttyUSB0 reset
```

### 3. Prepare the SD Card

Format as FAT32 and place MP3 files in the `/mp3/` folder:

```
/mp3/0001.mp3   Birds (default)
/mp3/0002.mp3   Siren
/mp3/0003.mp3   Cockerel
/mp3/0004.mp3   Bell
/mp3/0005.mp3   Bird 2
/mp3/0006.mp3   Pop
```

Files **must** be named exactly `0001.mp3`, `0002.mp3`, etc. Insert the card into the DFPlayer Mini before powering on.

### 4. First Boot

On first boot the display shows `bAt?` for 3 seconds if the RTC has never been set (or the backup battery was flat). Use the **CLOC** menu item to set the current time — no REPL needed.

---

## Usage

### Controls

| Input | Alarm inactive | Alarm active |
|-------|---------------|-------------|
| Rotate encoder | Navigate menu / adjust value | Ignored |
| Click encoder | Enter / confirm / next field | **Stop alarm** |
| Touch Snooze (GPIO 4) | Night light (if dark) | Snooze 5 min |
| Touch Stop (GPIO 0) | — | Stop alarm (unreliable — prefer encoder click) |

The menu returns to the time display automatically after **5 seconds** of inactivity.

### Menu

Navigate with the encoder wheel. Click to select.

| # | Display | Function | How to use |
|---|---------|----------|-----------|
| 0 | `ALRM` | Set alarm time | Click → rotate hours → click → rotate minutes → click to save |
| 1 | `ON-F` | Alarm on/off | Click → rotate to toggle ON/OFF (LEDs show green/red) → click to save |
| 2 | `SOND` | Alarm sound | Click → rotate to scroll through 6 sounds (plays 5 s preview) → click to save |
| 3 | `CLOC` | Set clock time | Click → rotate hours → click → rotate minutes → click to save |
| 4 | `LED ` | Sunrise LEDs on/off | Click → rotate to toggle ON/OFF → click to save |

All settings are saved to flash immediately on confirm and survive power loss.

### Alarm Sequence

1. **Starts** — LEDs begin at dark red; sound plays at low volume
2. **0–10 min** — LEDs fade red → orange → yellow → white (if LED enabled); volume rises to maximum
3. **10 min+** — Full brightness and volume; track loops automatically
4. **Snooze** — Touch GPIO 4 to pause for 5 minutes; alarm resumes from the same LED/volume point
5. **Stop** — Click encoder button (or touch GPIO 0) to stop completely
6. **Auto-stop** — Alarm stops automatically after 30 minutes

### Night Light

When the alarm is inactive, touch the snooze pad (GPIO 4) in a dark room:
- All LEDs light up full white for 30 seconds
- Then fade out over 10 seconds
- Only activates when ambient EMA light reading is below `NIGHT_LIGHT_THRESHOLD` (default 80)

### Persistent Settings

These are saved to `alarm_settings.json` on the ESP32 flash and survive power outages:

| Setting | Menu item | Default |
|---------|-----------|---------|
| Alarm hour | `ALRM` | 7 |
| Alarm minute | `ALRM` | 0 |
| Alarm enabled | `ON-F` | off |
| Sound type (0–5) | `SOND` | 0 (BIRD) |
| LED sunrise enabled | `LED ` | on |

The **clock time** is stored in the DS3231 RTC chip with its own battery backup — independent of the flash settings.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Display shows `bAt?` on boot | RTC backup battery flat | Replace CR2032 on DS3231 module; set time via CLOC |
| Display shows `00:00` | RTC not set or not found | Use CLOC menu to set time |
| Clock resets to wrong time after power loss | RTC battery dead | Replace CR2032 |
| Display stuck on `INIT` | I2C bus locked | Unplug and replug USB (full power cycle) |
| No sound | SD card or wiring issue | Check FAT32 format, file names `0001–0006.mp3`, TX/RX cross-wired |
| Touch snooze not responding | Threshold needs calibration | Run `test_touch.py`; adjust `TOUCH_THRESHOLD_MIN/MAX` in `config.py` |
| Night light not triggering | Room too bright | Cover sensor or lower `NIGHT_LIGHT_THRESHOLD` in `config.py` |
| LEDs not lighting | 5 V power missing | WS2812B requires 5 V — not 3.3 V |
| Alarm won't stop via GPIO 0 | GPIO 0 is unreliable under I2C load | Use encoder button click instead |

### Component tests

```bash
mpremote connect /dev/ttyUSB0 run tests/test_display.py
mpremote connect /dev/ttyUSB0 run tests/test_rtc.py
mpremote connect /dev/ttyUSB0 run tests/test_touch.py
mpremote connect /dev/ttyUSB0 run tests/test_encoder.py
mpremote connect /dev/ttyUSB0 run tests/test_leds.py
```

---

## Configuration

All tunable constants are in `src/config.py`:

| Constant | Default | Purpose |
|----------|---------|---------|
| `SUNRISE_DURATION` | 600 s | Alarm ramp-up duration |
| `SNOOZE_DURATION` | 300 s | Snooze length |
| `ALARM_MAX_DURATION` | 1800 s | Auto-stop time |
| `MENU_TIMEOUT` | 5000 ms | Menu idle timeout |
| `NIGHT_LIGHT_ON_DURATION` | 30 s | Night light full-on time |
| `NIGHT_LIGHT_DIM_DURATION` | 10 s | Night light fade time |
| `NIGHT_LIGHT_THRESHOLD` | 80 | EMA value below which night light activates |
| `DFPLAYER_VOLUME_MAX` | 25 | Maximum alarm volume |
| `TOUCH_THRESHOLD_MIN/MAX` | 20/200 | Touch detection window |

---

## License

MIT — see [LICENSE](LICENSE).

## Credits

- TM1637 driver inspired by mcauser/micropython-tm1637
- DFPlayer protocol based on DFRobot specifications


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
| 2 | `SOND` | Change sound type | Click to enter submenu → rotate wheel to scroll sounds → click to confirm |
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
