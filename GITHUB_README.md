# 🌅 ESP32 Sunrise Alarm Clock

A feature-rich sunrise alarm clock built with ESP32 and MicroPython, featuring gradual LED color transitions, MP3 audio playback, and a user-friendly menu system.

![MicroPython](https://img.shields.io/badge/MicroPython-1.20+-blue)
![ESP32](https://img.shields.io/badge/ESP32-D1%20Mini-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- 🌄 **10-minute Sunrise Simulation** - Gradual LED color transition (red → orange → yellow → white)
- 🎵 **MP3 Audio Playback** - DFPlayer Mini with customizable alarm sounds
- 🔊 **Gradual Volume Increase** - Synchronized with LED brightness
- 🎛️ **Rotary Encoder Menu** - Easy navigation and settings
- 👆 **Touch Controls** - Snooze and stop functions
- 💡 **Auto-Brightness** - Display adjusts to ambient light
- 💾 **Persistent Settings** - Alarm configuration saved to flash
- ⏰ **Accurate Timekeeping** - DS3231 RTC with battery backup

## 📦 Hardware Requirements

- ESP32 D1 Mini
- TM1637 7-segment display
- DS3231 Real-Time Clock module
- DFPlayer Mini MP3 player
- WS2812B LED strip (5 LEDs)
- KY-040 Rotary encoder
- Touch sensors (or use ESP32 built-in touch)
- Light sensor (analog)
- Speaker (for DFPlayer)
- MicroSD card (for MP3 files)

See [hardware pinout](QUICK_REFERENCE.txt) for complete wiring diagram.

## 🚀 Quick Start

### 1. Flash MicroPython

```bash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 esp32-*.bin
```

### 2. Upload Files

Upload all files from `src/` to your ESP32:

```bash
ampy --port /dev/ttyUSB0 put src/config.py
ampy --port /dev/ttyUSB0 put src/tm1637.py
ampy --port /dev/ttyUSB0 put src/ds3231.py
ampy --port /dev/ttyUSB0 put src/dfplayer.py
ampy --port /dev/ttyUSB0 put src/rotary_encoder.py
ampy --port /dev/ttyUSB0 put src/main.py
```

### 3. Prepare SD Card

Format as FAT32 and add MP3 files:
```
/mp3/0001.mp3  (Birds)
/mp3/0002.mp3  (Ringing)
/mp3/0003.mp3  (Beeping)
```

### 4. Set Time & Alarm

Connect via serial and run:

```python
from machine import I2C, Pin
from ds3231 import DS3231

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
rtc = DS3231(i2c)
rtc.set_time(2026, 3, 18, 3, 7, 30, 0)  # year, month, day, weekday, hour, min, sec

import main
main.alarm_clock.alarm_hour = 7
main.alarm_clock.alarm_minute = 30
main.alarm_clock.alarm_enabled = True
main.alarm_clock.save_settings()
```

### 5. Run

```python
import main
```

## 📖 Documentation

- **[README.md](README.md)** - Complete project documentation
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed setup guide
- **[QUICK_REFERENCE.txt](QUICK_REFERENCE.txt)** - Pin configuration & commands
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Implementation details
- **[docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md)** - System design

## 🧪 Testing

Test individual components before running the main program:

```python
import test_display  # Test TM1637 display
import test_rtc      # Test RTC
import test_touch    # Test touch sensors
import test_encoder  # Test rotary encoder
import test_leds     # Test LED sunrise effect
```

## 🎮 Controls

- **Rotate encoder**: Navigate menu
- **Click encoder**: Select menu item
- **Touch snooze (GPIO4)**: Snooze for 5 minutes
- **Touch stop (GPIO0)**: Stop alarm

## 📋 Menu Items

| Menu | Function | Status |
|------|----------|--------|
| TIME | Show current time | ✅ Working |
| ALRM | Set alarm time | 🔨 Use REPL |
| ON-F | Toggle alarm on/off | ✅ Working |
| SOND | Change sound type | ✅ Working |
| CLOC | Set current time | 🔨 Use REPL |

## 🛠️ Troubleshooting

See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting steps.

Common issues:
- **Display blank**: Check wiring (CLK=18, DIO=19), run `test_display.py`
- **RTC not found**: Verify I2C connections and battery
- **No sound**: Check SD card format (FAT32) and file naming
- **LEDs not working**: Verify 5V power supply

## 🗺️ Roadmap

- [ ] Interactive alarm/time setting via rotary encoder
- [ ] Multiple alarm slots
- [ ] Weekday-specific alarms
- [ ] WiFi/NTP time sync
- [ ] Web interface for configuration
- [ ] Alarm fade-out option

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
