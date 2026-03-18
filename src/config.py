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
DISPLAY_BRIGHTNESS_MIN = 10
DISPLAY_BRIGHTNESS_MAX = 80
LIGHT_SENSOR_MIN = 50
LIGHT_SENSOR_MAX = 3000

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
DFPLAYER_VOLUME_MIN = 0
DFPLAYER_VOLUME_MAX = 30
SOUND_TYPES = {
    1: "Birds",    # MP3 file 1
    2: "Ring",     # MP3 file 2
    3: "Beep",     # MP3 file 3
}

# Touch Sensor Thresholds
TOUCH_THRESHOLD_MIN = 5
TOUCH_THRESHOLD_MAX = 20

# Storage Keys
STORAGE_NAMESPACE = "ogalarm"
STORAGE_KEYS = {
    'alarm_hour': 'alm_h',
    'alarm_minute': 'alm_m',
    'alarm_enabled': 'alm_en',
    'sound_type': 'snd_typ',
}
