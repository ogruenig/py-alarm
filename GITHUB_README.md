# 🌅 ESP32 Sunrise Alarm Clock

A feature-rich sunrise alarm clock built with ESP32 and MicroPython, featuring gradual LED color transitions, MP3 audio playback, and a fully on-device menu system.

![MicroPython](https://img.shields.io/badge/MicroPython-1.24.1-blue)
![ESP32](https://img.shields.io/badge/ESP32-D1%20Mini-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- 🌄 **10-minute Sunrise Simulation** — Gradual LED color transition (red → orange → yellow → white)
- 🎵 **6 MP3 Alarm Sounds** — Birds, siren, cockerel, bell, bird 2, pop; with 5 s in-menu preview
- 🔊 **Gradual Volume Increase** — Synchronized with LED brightness; configurable per track
- 🎛️ **Fully On-Device Menu** — Set alarm time, clock, sound, and LED toggle with rotary encoder
- 👆 **Touch Controls** — Snooze (resumes from same point) and stop
- 🌙 **Night Light** — Touch snooze in the dark for 30 s of white LEDs then a 10 s fade
- 💡 **Auto-Brightness** — Display adjusts to ambient light with EMA smoothing
- 💾 **Persistent Settings** — All settings saved to flash (alarm time, on/off, sound, LED toggle)
- ⏰ **Accurate Timekeeping** — DS3231 RTC with battery backup; I2C-resilient

## 📦 Hardware Requirements

- ESP32 D1 Mini
- TM1637 7-segment display
- DS3231 Real-Time Clock module
- DFPlayer Mini MP3 player
- WS2812B LED strip (5 LEDs)
- KY-040 Rotary encoder
- Analog light sensor (GPIO36)
- Speaker (for DFPlayer)
- MicroSD card (for MP3 files)

See [QUICK_REFERENCE.txt](QUICK_REFERENCE.txt) for complete wiring diagram.

## 🚀 Quick Start

### 1. Flash MicroPython

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

### 2. Upload Files

Upload all files from `src/` to your ESP32:

```bash
cd src/
for f in config.py tm1637.py ds3231.py dfplayer.py rotary_encoder.py main.py; do
    mpremote connect /dev/ttyUSB0 cp $f :$f
done
```

### 3. Prepare SD Card

Format as FAT32 and add MP3 files:
```
/mp3/0001.mp3  (Birds)
/mp3/0002.mp3  (Siren)
/mp3/0003.mp3  (Cockerel)
/mp3/0004.mp3  (Bell)
/mp3/0005.mp3  (Bird 2)
/mp3/0006.mp3  (Pop)
```

### 4. First-Time Clock Setup

Only needed if the RTC has never been set:
```python
from machine import I2C, Pin
from ds3231 import DS3231
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
rtc = DS3231(i2c)
rtc.set_time(2026, 3, 18, 3, 7, 30, 0)  # year, month, day, weekday, hour, min, sec
```

After that, use the **CLOC** menu item on the device to set/adjust the time.

## 📖 Documentation

- **[README.md](README.md)** — Complete project documentation
- **[INSTALLATION.md](INSTALLATION.md)** — Detailed setup guide
- **[QUICK_REFERENCE.txt](QUICK_REFERENCE.txt)** — Pin configuration & commands
- **[docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)** — System design

## 🧪 Testing

Test individual components before running the main program:

```bash
mpremote connect /dev/ttyUSB0 run tests/test_display.py
mpremote connect /dev/ttyUSB0 run tests/test_rtc.py
mpremote connect /dev/ttyUSB0 run tests/test_touch.py
mpremote connect /dev/ttyUSB0 run tests/test_encoder.py
mpremote connect /dev/ttyUSB0 run tests/test_leds.py
```

## 🎮 Controls

| Control | Alarm active | Alarm inactive |
|---------|-------------|----------------|
| Rotate encoder | — | Navigate menu / adjust value |
| Click encoder | — | Enter / confirm / next field |
| Touch snooze (GPIO4) | Snooze 5 min (resumes from same point) | Night light (if dark) |
| Touch stop (GPIO0) | Stop alarm | — |

## 📋 Menu Items

| Display | Function | Notes |
|---------|----------|-------|
| `ALRM` | Set alarm time | Rotate hours → click → rotate minutes → click |
| `ON-F` | Toggle alarm on/off | LEDs flash green/red; display shows ` ON `/`OFF ` |
| `SOND` | Cycle alarm sound | Plays 5 s preview of each track |
| `CLOC` | Set current time | Same flow as ALRM; saves to RTC |
| `LED ` | Toggle sunrise LEDs | Enable/disable LED effect independently of sound |

## 🛠️ Troubleshooting

- **Stuck on INIT**: I2C bus locked — unplug and replug USB (full power cycle)
- **Shows 00:00**: RTC not found or not yet set — use CLOC menu
- **No sound**: Check SD card (FAT32, files named 0001.mp3–0006.mp3)
- **Night light not triggering**: Room too bright — cover sensor or lower `NIGHT_LIGHT_THRESHOLD` in config

## 🗺️ Roadmap

- [ ] Multiple alarm slots
- [ ] Weekday-specific alarms
- [ ] WiFi/NTP time sync
- [ ] Web interface for configuration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 👏 Acknowledgments

- TM1637 driver inspired by mcauser/micropython-tm1637
- DFPlayer protocol based on DFRobot specifications
- Sunrise color palette concept

## 📞 Support

For questions or issues:
1. Check the documentation in this repository
2. Review test scripts for hardware verification
3. Open an issue on GitHub

---

**Made with ❤️ for peaceful mornings** 🌅
