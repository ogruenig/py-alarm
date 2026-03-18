# Changelog

All notable changes to the ESP32 Alarm Clock project will be documented in this file.

## [1.0.0] - 2026-03-18

### Added
- Initial release of MicroPython implementation
- Complete sunrise alarm with 10-minute LED color transition
- Sound alarm with gradual volume increase
- Menu navigation system with rotary encoder
- Touch sensor controls (snooze and stop)
- Auto-brightness display adjustment
- Persistent settings storage (JSON)
- RTC timekeeping with DS3231
- Full hardware driver suite (TM1637, DS3231, DFPlayer, WS2812B)
- Comprehensive test suite for all components
- Complete documentation and installation guide

### Features
- 10-minute sunrise simulation (red → orange → yellow → white)
- MP3 playback with 3 sound options (birds, ringing, beeping)
- 5-minute snooze function
- 30-minute auto-stop
- Light sensor auto-brightness
- Menu timeout (5 seconds)

### Known Limitations
- Interactive alarm time setting not yet implemented (use REPL)
- Interactive clock time setting not yet implemented (use REPL)
- Single alarm slot only
- No WiFi/NTP sync
- Basic error handling

### Future Plans
- Interactive time/alarm setting via rotary encoder
- Multiple alarm slots
- Weekday-specific alarms
- WiFi/NTP time synchronization
- Improved error recovery
