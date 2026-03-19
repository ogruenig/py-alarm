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
