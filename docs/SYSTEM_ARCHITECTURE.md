# ESP32 Alarm Clock — System Architecture

## Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        ESP32 D1 Mini                             │
│                       (MicroPython 1.24.1)                       │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  main.py — AlarmClock                     │  │
│  │  100 ms main loop:                                        │  │
│  │   update_time · handle_encoder · handle_touch             │  │
│  │   check_menu_timeout · update_display_brightness          │  │
│  │   check_alarm · update_alarm · update_night_light         │  │
│  │   update_display                                          │  │
│  └──────────────────────────┬────────────────────────────────┘  │
│                             │                                    │
│   ┌─────────────┬───────────┼──────────────┬──────────────┐     │
│   ▼             ▼           ▼              ▼              ▼     │
│ tm1637.py   ds3231.py  dfplayer.py  rotary_encoder.py  config.py │
│ Display      RTC        MP3          Encoder             Constants│
└──────────────────────────────────────────────────────────────────┘
        │          │          │            │
     GPIO 18/19  I2C 21/22  UART 16/17  GPIO 32/25/15
        │          │          │            │
   [TM1637]    [DS3231]  [DFPlayer]   [KY-040]
                               │
                           [Speaker]

   neopixel (built-in): GPIO 27 → [WS2812B ×5]
   machine.TouchPad:    GPIO 4  → Snooze pad
                        GPIO 0  → Stop pad (unreliable)
   machine.ADC:         GPIO 36 → Light sensor (ATTN_0DB)
```

---

## Timekeeping

The RTC is read **at most once per minute** to avoid I2C load. Between reads, time is extrapolated using `ticks_ms`:

```
On each loop tick:
  elapsed_s = ticks_diff(now, _sync_ticks) // 1000
  total_s   = (_sync_epoch + elapsed_s) % 86400
  current_hour   = total_s // 3600
  current_minute = (total_s % 3600) // 60
  current_second = total_s % 60

Every 60 seconds:
  dt = rtc.get_time()
  _sync_epoch = dt[4]*3600 + dt[5]*60 + dt[6]
  _sync_ticks = now
  (on OSError: skip sync, keep extrapolating, retry next minute)
```

**Power-loss detection (OSF flag):** On boot, `ds3231.osf_set()` reads bit 7 of status register `0x0F`. If set, the RTC oscillator was stopped (dead battery) and the stored time is invalid — the display shows `bAt?` for 3 seconds. `set_time()` clears the flag automatically.

---

## Menu State Machine

```
[Time display]
      │
  Rotate encoder
      │
      ▼
 [in_menu = True]  ◄──── 5 s timeout ────┐
  menu_pos 0–4                            │
  ALRM / ON-F / SOND / CLOC / LED         │
      │                                   │
   Click                                  │
      │                                   │
      ▼                                   │
 [edit_mode set] ──────────────────────────┘

edit_mode values and transitions:

  'alrm_h'    → rotate sets edit_hour
     click    → edit_mode = 'alrm_m'
  'alrm_m'    → rotate sets edit_minute
     click    → save alarm_hour/minute, exit menu

  'onf_select' → rotate toggles alarm_enabled; LEDs show green/red
     click    → save, exit menu

  'sond_select'→ rotate cycles sound_type 0–5; plays 5 s preview
     click    → save, exit menu

  'cloc_h'    → rotate sets edit_hour
     click    → edit_mode = 'cloc_m'
  'cloc_m'    → rotate sets edit_minute
     click    → write RTC, update _sync_epoch/_sync_ticks, exit menu

  'led_select'→ rotate toggles led_enabled; LEDs show green/red
     click    → save, exit menu
```

---

## Alarm State Machine

```
[Alarm inactive]
      │
  current_hour == alarm_hour
  current_minute == alarm_minute
  current_second == 0
  alarm_enabled == True
      │
      ▼
  start_alarm()
   alarm_active = True
   alarm_start_time = time.time()
   dfplayer.play(track)
      │
      ▼
  update_alarm()  (every loop tick)
   progress = alarm_elapsed / SUNRISE_DURATION  (0.0–1.0)
   update_sunrise_leds(progress)  [if led_enabled]
   set dfplayer volume (ramps from vol_start to DFPLAYER_VOLUME_MAX)
      │
      ├── encoder click ──────────────────► stop_alarm()
      │
      ├── touch GPIO 4 ──────────────────► snooze_alarm()
      │                                     saves _alarm_elapsed
      │                                     resumes from same point
      │
      └── elapsed > ALARM_MAX_DURATION ──► stop_alarm() [auto]
```

### Sunrise LED Color Progression

```
Progress  Time     Color
0.00      0:00     (0, 0, 0)       — off
0.25      2:30     (128, 0, 0)     — red
0.50      5:00     (255, 100, 0)   — orange
0.75      7:30     (255, 255, 0)   — yellow
1.00      10:00    (255, 255, 255) — white
```

---

## Class Structure

```python
class AlarmClock:
    # Hardware
    display       : TM1637
    rtc           : DS3231 | None
    dfplayer      : DFPlayer
    leds          : NeoPixel
    encoder       : RotaryEncoder
    touch_snooze  : TouchPad
    touch_stop    : TouchPad
    light_sensor  : ADC

    # Timekeeping
    current_hour, current_minute, current_second : int
    _sync_epoch   : int          # seconds-since-midnight at last RTC read
    _sync_ticks   : int          # ticks_ms at last RTC read
    _last_rtc_sync: int          # ticks_ms; triggers re-sync every 60 s

    # Alarm
    alarm_hour, alarm_minute : int
    alarm_enabled  : bool
    alarm_active   : bool
    alarm_start_time: float      # time.time() when alarm started
    snooze_until   : float
    _alarm_elapsed : float       # seconds, for snooze resume
    sound_type     : int         # 0–5, index into SOUND_TYPES
    led_enabled    : bool
    _vol_start, _ramp_dur : int  # per-track volume settings

    # Menu
    menu_pos       : int         # 0–4
    in_menu        : bool
    last_menu_time : int         # ticks_ms
    edit_mode      : str | None  # 'alrm_h'|'alrm_m'|'onf_select'|'sond_select'|
                                 #  'cloc_h'|'cloc_m'|'led_select'
    edit_hour, edit_minute : int
    _blink_state   : bool
    _blink_time    : int

    # Feedback / effects
    _feedback_until : int        # ticks_ms deadline; 0 = inactive
    _feedback_msg   : str
    _preview_until  : int        # stops SOND preview
    _night_light_start : float   # time.time(); 0 = inactive
    _light_ema      : float | None  # EMA(alpha=0.05) of ADC reading

    # Key methods
    init_hardware()
    load_settings() / save_settings()
    update_time()               # extrapolates; re-syncs RTC every 60 s
    handle_encoder()            # click → stop alarm OR menu nav
    handle_touch()              # snooze or night light
    check_alarm()
    start_alarm() / stop_alarm() / snooze_alarm() / resume_alarm()
    update_alarm()              # sunrise LEDs + volume ramp
    update_sunrise_leds(progress)
    update_night_light()
    update_display_brightness() # EMA light sensor → TM1637 brightness
    update_display()            # feedback msg → edit display → menu → time
    _update_edit_display()      # blinking HH:MM for alrm/cloc modes only
    _handle_edit_rotation(rotation)
    _handle_edit_click()
    _play_sound_preview()       # 5 s preview at half volume
    _show_feedback(msg, duration_ms)
    _flash_leds_status(enabled) # green / red flash
    run()                       # 100 ms main loop
```

---

## Persistent Storage

`alarm_settings.json` on ESP32 flash (survives power loss):

```json
{
  "alarm_hour": 7,
  "alarm_minute": 0,
  "alarm_enabled": false,
  "sound_type": 0,
  "led_enabled": true
}
```

The **clock time** is stored in the DS3231 RTC chip backed by a CR2032 coin cell.

---

## Main Loop Timing

```
Each 100 ms cycle:
  1. update_time()               — RTC re-sync if due; else ticks_ms extrapolation
  2. handle_encoder()            — rotation + click
  3. handle_touch()              — snooze / night light
  4. check_menu_timeout()        — return to time display after 5 s
  5. update_display_brightness() — EMA light sensor
  6. check_alarm()               — trigger if time matches
  7. update_alarm()              — sunrise LEDs + volume (if active)
  8. update_night_light()        — white LEDs + fade (if active)
  9. update_display()            — TM1637 output
 10. sleep_ms(100)
```

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
              │  Display current time  │<────┐
              │  (alarm inactive)      │     │
              │                        │     │
              └────────┬───────────────┘     │
                       │                     │
                Rotate Encoder              Timeout
                       │                  5 seconds
                       ▼                     │
              ┌────────────────────┐         │
              │  in_menu = True    │         │
              │  menu_pos = 0      │         │
              │  Display: ALRM     │─────────┘
              │  (Set alarm time)  │
              └────────┬───────────┘
                       │ Click
                       ▼
              ┌────────────────┐
              │ edit_mode→alrm_h│
              │ Rotate to set   │
              └────────┬────────┘
                       │ Click
                       ▼
              ┌────────────────┐
              │ edit_mode→alrm_m│
              └────────┬────────┘
                       │ Click → Save
                       │
              ┌────────┴──────────────────────────┐
              │ Rotate again to menu_pos = 1      │
              │ Display: ON-F (toggle alarm)      │
              │ Round-robin through:              │
              │   0 = ALRM (set time)             │
              │   1 = ON-F  (enable/disable)      │
              │   2 = SOND  (sound choice)        │
              │   3 = CLOC  (set clock)           │
              │   4 = LED   (sunrise toggle)      │
              │ Wraps back to 0                   │
              └─────────────────────────────────┘

While Alarm Active:
  - Encoder rotation:  Ignored
  - Encoder click:     Stop alarm immediately
  - Touch snooze:      Snooze 5 min (resume from same point)
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
│  │    "sound_type": 0,           │ │
│  │    "led_enabled": true        │ │
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
    - rtc: DS3231 (or None if unavailable)
    - dfplayer: DFPlayer
    - leds: NeoPixel
    - encoder: RotaryEncoder
    - touch_snooze: TouchPad
    - touch_stop: TouchPad
    - light_sensor: ADC
    
    # Time state
    - current_hour/minute/second: int
    - _last_rtc_sync: ticks_ms (RTC read once per minute)
    
    # Alarm state
    - alarm_hour/minute: int
    - alarm_enabled: bool
    - alarm_active: bool
    - alarm_start_time: time.time()
    - snooze_until: time.time()
    - sound_type: int (0-5, index into SOUND_TYPES)
    - led_enabled: bool (LED sunrise on/off toggle)
    - _alarm_elapsed: seconds (for snooze resume)
    - _vol_start, _ramp_dur: per-track settings
    
    # Menu state
    - menu_pos: int (0-4)
    - in_menu: bool
    - edit_mode: str | None ('alrm_h', 'alrm_m', 'cloc_h', 'cloc_m')
    - edit_hour/minute: int
    - last_menu_time: ticks_ms
    
    # Feedback & effects
    - _feedback_until: ticks_ms (message display timeout)
    - _feedback_msg: str
    - _preview_until: ticks_ms (SOND preview timeout)
    - _night_light_start: time.time() (0 = inactive)
    - _light_ema: float (exponential moving average of sensor)
    
    # Methods (key ones)
    + init_hardware()
    + load_settings() / save_settings()
    + update_time()  # RTC read once per minute
    + handle_encoder()  # Click stops alarm when active
    + handle_touch()  # Snooze or night light
    + check_alarm()
    + start_alarm() / stop_alarm() / snooze_alarm() / resume_alarm()
    + update_alarm()
    + update_sunrise_leds()
    + update_night_light()
    + update_display_brightness()  # EMA smoothing
    + update_display()
    + run()  # main loop (100ms tick)
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
