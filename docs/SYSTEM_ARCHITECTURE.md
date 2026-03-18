# ESP32 Alarm Clock - System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         ESP32 D1 Mini                               │
│                         (MicroPython)                               │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │                      main.py                                │   │
│  │              AlarmClock Class (Main Loop)                   │   │
│  │                                                             │   │
│  │  • Update time from RTC                                     │   │
│  │  • Handle user inputs (encoder, touch)                      │   │
│  │  • Check alarm conditions                                   │   │
│  │  • Update display & LEDs                                    │   │
│  │  • Control MP3 playback                                     │   │
│  │  • Save/load settings                                       │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│              ┌───────────────┼───────────────┐                     │
│              │               │               │                     │
│  ┌───────────▼──┐  ┌────────▼─────┐  ┌─────▼────────┐           │
│  │ rotary_      │  │  tm1637.py   │  │  ds3231.py   │           │
│  │ encoder.py   │  │  Display     │  │  RTC         │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ dfplayer.py  │  │ neopixel     │  │ config.py    │           │
│  │ MP3 Player   │  │ LED Control  │  │ Settings     │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌────────────────┐    ┌──────────────┐
│   TM1637      │    │   DS3231       │    │  DFPlayer    │
│   Display     │    │   RTC          │    │  Mini        │
│   (GPIO 18,19)│    │   (I2C 21,22)  │    │  (UART 16,17)│
└───────────────┘    └────────────────┘    └──────────────┘
                                                    │
        ┌─────────────────────┬─────────────┐     ▼
        ▼                     ▼             ▼   ┌──────────┐
┌───────────────┐    ┌────────────┐  ┌──────────────┐  │ Speaker  │
│   WS2812B     │    │  Rotary    │  │  Touch Pads  │  └──────────┘
│   5 LEDs      │    │  Encoder   │  │  (GPIO 4,0)  │
│   (GPIO 27)   │    │  (32,25,15)│  └──────────────┘
└───────────────┘    └────────────┘
        │                     │
        ▼                     ▼
    ┌─────────┐       ┌──────────────┐
    │ Sunrise │       │ User Control │
    │ Effect  │       │ Menu Nav     │
    └─────────┘       └──────────────┘
```

## Data Flow Diagram

### Normal Operation (Time Display)

```
┌─────────────┐
│   RTC       │──────┐
│  DS3231     │      │ Read Time
└─────────────┘      │ Every Loop
                     ▼
              ┌──────────────┐
              │ AlarmClock   │
              │   .update    │
              │   _time()    │
              └──────────────┘
                     │
                     ▼
              ┌──────────────┐      ┌──────────────┐
              │ Format Time  │─────>│   TM1637     │
              │  HH:MM       │      │   Display    │
              └──────────────┘      └──────────────┘
```

### Alarm Triggering

```
┌──────────────┐
│ Check Alarm  │
│ current ==   │───── No ────> Continue
│ alarm time?  │
└──────────────┘
       │ Yes
       ▼
┌──────────────────────────────┐
│  start_alarm()               │
│  • Set alarm_active = True   │
│  • Start sunrise sequence    │
│  • Start MP3 playback        │
└──────────────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│  update_alarm() (every loop) │
│  • Calculate progress 0-1.0  │
│  • Update LED colors         │
│  • Increase volume           │
└──────────────────────────────┘
       │
       ├──── Touch Snooze ────> snooze_alarm()
       │                         5 min delay
       │
       ├──── Touch Stop ──────> stop_alarm()
       │                         Clear LEDs
       │                         Stop sound
       │
       └──── 30 min passed ───> Auto stop
```

### Sunrise LED Color Progression

```
Time        Progress    Color Calculation           RGB Output
─────────────────────────────────────────────────────────────────
0:00        0.0         Dark red start              (0, 0, 0)
0:30        0.05        Gradual red brightening     (13, 0, 0)
2:30        0.25        Red peak                    (128, 0, 0)
─────────────────────────────────────────────────────────────────
2:31        0.251       Red → Orange transition     (129, 1, 0)
3:45        0.375       Orange mid-point            (191, 50, 0)
5:00        0.50        Orange peak                 (255, 100, 0)
─────────────────────────────────────────────────────────────────
5:01        0.501       Orange → Yellow transition  (255, 101, 0)
6:15        0.625       Yellow mid-point            (255, 177, 0)
7:30        0.75        Yellow peak                 (255, 255, 0)
─────────────────────────────────────────────────────────────────
7:31        0.751       Yellow → White transition   (255, 255, 1)
8:45        0.875       Nearly white                (255, 255, 127)
10:00       1.0         Pure white                  (255, 255, 255)
─────────────────────────────────────────────────────────────────
```

## Menu State Machine

```
                    ┌──────────────┐
                    │    Boot      │
                    │  Initialize  │
                    └──────┬───────┘
                           │
                           ▼
              ┌────────────────────────┐
         ┌───>│  menu_pos = 0          │<────┐
         │    │  Display: TIME         │     │
         │    │  Show HH:MM            │     │
         │    └────────┬───────────────┘     │
         │             │                     │
         │       Rotate Encoder              │
         │             │                     │
         │             ▼                     │
         │    ┌────────────────┐        Timeout
         │    │  in_menu=True  │        5 sec
         │    │  menu_pos++    │            │
         │    └────────┬───────┘            │
         │             │                     │
         │             ▼                     │
         │    ┌────────────────────┐        │
         │    │  menu_pos = 1      │        │
         │    │  Display: ALRM     │────────┘
         │    │  (Set alarm time)  │
         │    └────────┬───────────┘
         │             │ Click
         │             ▼
         │    [ Enter alarm setting ]
         │    [ Not yet implemented ]
         │             │
         └─────────────┴─> Continue rotating...
                           menu_pos = 2 (ON-F)
                           menu_pos = 3 (SOND)
                           menu_pos = 4 (CLOC)
                           Wraps to 0
```

## Storage Architecture

```
┌─────────────────────────────────────┐
│  ESP32 Flash Memory                 │
│                                     │
│  ┌───────────────────────────────┐ │
│  │  alarm_settings.json          │ │
│  │  {                            │ │
│  │    "alarm_hour": 7,           │ │
│  │    "alarm_minute": 30,        │ │
│  │    "alarm_enabled": true,     │ │
│  │    "sound_type": 1            │ │
│  │  }                            │ │
│  └───────────────────────────────┘ │
│                                     │
│  Read on boot                       │
│  Write on settings change           │
└─────────────────────────────────────┘
```

## Hardware Interface Summary

| Hardware      | Protocol | Pins      | Driver           | Purpose           |
|---------------|----------|-----------|------------------|-------------------|
| TM1637        | Custom   | 18, 19    | tm1637.py        | Time display      |
| DS3231        | I2C      | 21, 22    | ds3231.py        | Timekeeping       |
| DFPlayer      | UART     | 16, 17    | dfplayer.py      | MP3 playback      |
| WS2812B       | Custom   | 27        | neopixel (built) | Sunrise LEDs      |
| KY-040        | GPIO     | 32, 25, 15| rotary_encoder   | User input        |
| Touch Pads    | Touch    | 4, 0      | machine.TouchPad | Snooze/stop       |
| Light Sensor  | ADC      | 36        | machine.ADC      | Auto-brightness   |

## Class Structure

```python
class AlarmClock:
    # Hardware objects
    - display: TM1637
    - rtc: DS3231
    - dfplayer: DFPlayer
    - leds: NeoPixel
    - encoder: RotaryEncoder
    - touch_snooze: TouchPad
    - touch_stop: TouchPad
    - light_sensor: ADC
    
    # State variables
    - menu_pos: int
    - in_menu: bool
    - current_hour/minute/second: int
    - alarm_hour/minute: int
    - alarm_enabled/active: bool
    - sound_type: int
    - sunrise_stage: int
    
    # Methods
    + init_hardware()
    + load_settings() / save_settings()
    + update_time()
    + handle_encoder()
    + handle_touch()
    + check_alarm()
    + start_alarm() / stop_alarm() / snooze_alarm()
    + update_alarm()
    + update_sunrise_leds()
    + update_display()
    + run() - main loop
```

## Timing & Execution

```
Main Loop Cycle (~100ms):
┌────────────────────────────────────────┐
│ 1. Read RTC time               (~5ms)  │
│ 2. Check encoder rotation      (~1ms)  │
│ 3. Check touch sensors         (~1ms)  │
│ 4. Check menu timeout          (<1ms)  │
│ 5. Read light sensor           (~1ms)  │
│ 6. Check alarm trigger         (~1ms)  │
│ 7. Update alarm if active      (~5ms)  │
│ 8. Update display              (~10ms) │
│ 9. Sleep 100ms                          │
└────────────────────────────────────────┘
Total: ~125ms per cycle = ~8 updates/sec
```

## Error Handling

Currently minimal error handling:
- Try/except in main loop catches runtime errors
- Hardware init checks for I2C device presence
- Safe defaults if settings file missing
- Continue on error with 1 second delay

**Future improvement needed:**
- Retry logic for I2C communication
- Watchdog timer for crash recovery
- LED error indicators
- Graceful degradation (work without RTC, etc.)

---

This architecture provides a solid foundation for the alarm clock with room for future enhancements!
