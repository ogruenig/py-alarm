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
    'TOUCH_STOP': 33,    # T8 - GPIO33 (GPIO0 avoided: it's the ESP32 boot pin)
    
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
LIGHT_SENSOR_MIN = 280        # at or below this -> minimum brightness
LIGHT_SENSOR_MAX = 771        # at or above this -> maximum brightness

# Menu Settings
MENU_TIMEOUT = 5000  # milliseconds to return to clock display
MENU_ITEMS = [
    "TIME",   # 0 - Show current time (default)
    "ALRM",   # 1 - Set alarm time
    "ON-F",   # 2 - Alarm on/off
    "SOND",   # 3 - Sound type selection
    "CLOC",   # 4 - Set current time
]

# Alarm Settings
SUNRISE_DURATION = 600  # 10 minutes in seconds
SNOOZE_DURATION = 300   # 5 minutes in seconds
ALARM_MAX_DURATION = 1800  # 30 minutes max alarm duration

# Sound Settings
# Global max volume (0-30). Tune this to match your speaker/room.
DFPLAYER_VOLUME_MAX = 25

SOUND_TYPES = {
    1: "BIRD",   # Track 1 - Birds twittering (default sunrise alarm)
    2: "SIRN",   # Track 2 - Siren / alarm
    3: "COCK",   # Track 3 - Cock crow
}

# Per-track sound profiles
# vol_start : initial volume when alarm fires (0-30)
# ramp_dur  : seconds to ramp from vol_start to DFPLAYER_VOLUME_MAX
SOUND_PROFILES = {
    1: {'vol_start':  0, 'ramp_dur': 600},  # Birds: gentle 10-min ramp from silence
    2: {'vol_start': 15, 'ramp_dur':  60},  # Siren: loud within 1 min
    3: {'vol_start': 15, 'ramp_dur':  60},  # Cock crow: loud within 1 min
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
