# Changelog

All notable changes to the ESP32 Alarm Clock project will be documented in this file.

## [1.1.0] - 2026-03-18

### Added
- **On-Device Menu**: Full interactive menu on rotary encoder — set alarm time, clock time, sound, and LED toggle without REPL
- **Night Light**: Touch snooze in the dark for 30 seconds of white LEDs, then 10-second fade
- **6 Alarm Sounds**: Birds (BIRD), siren (SIRN), cockerel (COCK), bell (BELL), bird 2 (BRD2), pop (POP)
- **Sound Submenu**: Interactive sound selection — rotate encoder to scroll through 6 sounds with live preview
- **Encoder Button Stop**: Encoder button click stops alarm (fallback for unreliable GPIO0)
- **Snooze Resume**: Snooze pauses alarm and resumes from the same point 5 minutes later
- **LED Toggle Menu**: Independent LED sunrise toggle (LED menu item)
- **RTC Resilience**: RTC reads once per minute (not every loop tick); I2C failures don't crash the app
- **Light Sensor EMA**: Exponential moving average smoothing (alpha=0.05) eliminates display brightness flicker
- **ADC Fix**: Switched light sensor to ATTN_0DB for proper 0-1.1V range

### Changed
- **Menu Items**: Replaced TIME with LED; now 5 items (ALRM, ON-F, SOND, CLOC, LED)
- **Interrupt-Based Encoder**: Switched from polling to GPIO edge-triggered ISR for fast, reliable rotation
- **Touch Snooze**: Relocated night light trigger from GPIO0 (unreliable) to GPIO4 (snooze pad)
- **DS3231 Init**: Removed exception on missing RTC; boots gracefully without it
- **Full ASCII TM1637**: Replaced minimal segment table with 96-char ASCII support
- **Per-Track Volume**: Each sound has configurable vol_start and ramp_dur

### Fixed
- Boot hang on RTC I2C errors (now wrapped in try/except)
- Encoder double-stepping (added accumulator)
- Encoder missing fast rotations (switched to ISR)
- RTC spamming ENODEV exceptions (now reads once per minute with fallback)
- Night light LEDs being cleared by display handler (added _night_light_start check)
- Light sensor always reading 0 (switched from ATTN_11DB to ATTN_0DB)
- GPIO0 touch sensor unreliable when full app running

### Removed
- `TIME` menu item (was placeholder)
- `__name__ == "__main__"` guard that prevented boot
- Strict exception on DS3231 not found

### Known Limitations
- GPIO0 (T1 Stop) unreliable under full app load — use encoder button instead
- Single alarm slot only (future: multiple alarms)
- No WiFi/NTP sync

## [1.0.0] - 2026-03-18

### Initial Release
- Complete MicroPython implementation on ESP32
- 10-minute sunrise simulation with color transition
- 3 MP3 alarm sounds with gradual volume increase
- Menu navigation with rotary encoder
- Touch sensor controls (snooze and stop)
- Auto-brightness display adjustment
- RTC timekeeping with DS3231
- Persistent settings storage (JSON)
