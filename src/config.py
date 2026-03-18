"""
Configuration file for ESP32 Alarm Clock
Pin assignments and constants
"""

# GPIO Pin Assignments
PINS = {
    # Display TM1637
    'DISPLAY_CLK': 18,
    'DISPLAY_DIO': 19,
    
    # RTC DS3231 (I2C)
    'RTC_SDA': 21,
    'RTC_SCL': 22,
    
    # DFPlayer Mini (UART)
    'DFPLAYER_TX': 17,  # ESP32 TX -> DFPlayer RX
    'DFPLAYER_RX': 16,  # ESP32 RX -> DFPlayer TX
    
    # WS2812B LED Strip
    'LED_DATA': 27,
    
    # Rotary Encoder
    'ENCODER_CLK': 32,
    'ENCODER_DT': 25,
    'ENCODER_SW': 15,
    
    # Touch Sensors
    'TOUCH_SNOOZE': 4,   # T0 - GPIO4
    'TOUCH_STOP': 0,     # T1 - GPIO0
    
    # Light Sensor (analog)
    'LIGHT_SENSOR': 36,
}

# Hardware Constants
NUM_LEDS = 5
UART_ID = 1
UART_BAUDRATE = 9600

# Display Settings
DISPLAY_BRIGHTNESS_MIN = 10   # -> TM1637 level 1 (very dim)
DISPLAY_BRIGHTNESS_MAX = 70   # -> TM1637 level 7 (fully bright)
LIGHT_SENSOR_MIN = 20         # at or below this -> minimum brightness (ATTN_0DB)
LIGHT_SENSOR_MAX = 160        # at or above this -> maximum brightness (ATTN_0DB)

# Menu Settings
MENU_TIMEOUT = 5000  # milliseconds to return to clock display
MENU_ITEMS = [
    "ALRM",   # 0 - Set alarm time
    "ON-F",   # 1 - Alarm on/off
    "SOND",   # 2 - Sound type selection
    "CLOC",   # 3 - Set current time
    "LED ",   # 4 - Sunrise LED on/off
]

# Alarm Settings
SUNRISE_DURATION = 600  # 10 minutes in seconds
SNOOZE_DURATION = 300   # 5 minutes in seconds
ALARM_MAX_DURATION = 1800  # 30 minutes max alarm duration

# Night light (touch STOP when dark and alarm not active)
NIGHT_LIGHT_ON_DURATION  = 30   # seconds at full white
NIGHT_LIGHT_DIM_DURATION = 10   # seconds to fade from full white to off
NIGHT_LIGHT_THRESHOLD    = 80   # only trigger night light below this EMA value (dark room)

# Sound Settings
# Global max volume (0-30). Tune this to match your speaker/room.
DFPLAYER_VOLUME_MAX = 25

# Sound tracks — add new entries here to extend the sound menu.
# 'track': DFPlayer track number, 'name': 4-char display label
SOUND_TYPES = [
    {'track': 1, 'name': 'BIRD'},   # Birds twittering (default sunrise alarm)
    {'track': 2, 'name': 'SIRN'},   # Siren / alarm
    {'track': 3, 'name': 'COCK'},   # Cock crow
    {'track': 4, 'name': 'BELL'},   # Bell
    {'track': 5, 'name': 'BRD2'},   # Bird 2
    {'track': 6, 'name': 'POP '},   # Pop music
]

# Per-track sound profiles keyed by track number
# vol_start : initial volume when alarm fires (0-30)
# ramp_dur  : seconds to ramp from vol_start to DFPLAYER_VOLUME_MAX
SOUND_PROFILES = {
    1: {'vol_start':  5, 'ramp_dur': 600},  # Birds: gentle 10-min ramp, audible from start
    2: {'vol_start': 15, 'ramp_dur':  60},  # Siren: loud within 1 min
    3: {'vol_start': 15, 'ramp_dur':  60},  # Cock crow: loud within 1 min
    4: {'vol_start': 10, 'ramp_dur': 120},  # Bell: moderate ramp over 2 min
    5: {'vol_start':  5, 'ramp_dur': 600},  # Bird 2: gentle ramp like Bird 1
    6: {'vol_start': 15, 'ramp_dur': 180},  # Pop music: starts loud, full volume in 3 min
}

# Touch Sensor Thresholds
TOUCH_THRESHOLD_MIN = 20
TOUCH_THRESHOLD_MAX = 150

# Storage Keys
STORAGE_NAMESPACE = "ogalarm"
STORAGE_KEYS = {
    'alarm_hour': 'alm_h',
    'alarm_minute': 'alm_m',
    'alarm_enabled': 'alm_en',
    'sound_type': 'snd_typ',
}
