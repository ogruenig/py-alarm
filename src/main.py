"""
ESP32 Alarm Clock - Main Program
MicroPython implementation
"""

import time
import uio
import sys
import machine
from machine import Pin, I2C, UART, TouchPad, ADC
import neopixel
import json
from config import (PINS, NUM_LEDS, UART_ID, UART_BAUDRATE,
                    DISPLAY_BRIGHTNESS_MIN, DISPLAY_BRIGHTNESS_MAX,
                    LIGHT_SENSOR_MIN, LIGHT_SENSOR_MAX,
                    MENU_TIMEOUT, MENU_ITEMS,
                    SUNRISE_DURATION, SNOOZE_DURATION, ALARM_MAX_DURATION,
                    NIGHT_LIGHT_ON_DURATION, NIGHT_LIGHT_DIM_DURATION, NIGHT_LIGHT_THRESHOLD,
                    DFPLAYER_VOLUME_MAX, SOUND_TYPES, SOUND_PROFILES,
                    TOUCH_THRESHOLD_MIN, TOUCH_THRESHOLD_MAX)

# Import hardware drivers (to be created separately)
# These will need to be uploaded alongside main.py
try:
    from tm1637 import TM1637
    from ds3231 import DS3231
    from dfplayer import DFPlayer
    from rotary_encoder import RotaryEncoder
except ImportError as e:
    print(f"Warning: Could not import library: {e}")
    print("Make sure all library files are uploaded to the ESP32")

class AlarmClock:
    def __init__(self):
        print("Initializing Alarm Clock...")
        
        # Hardware initialization
        self.init_hardware()
        
        # State variables
        self.menu_pos = 0
        self.menu_max = len(MENU_ITEMS) - 1
        self.last_menu_time = time.ticks_ms()
        self.in_menu = False
        
        # Time variables
        self.current_hour = 0
        self.current_minute = 0
        self.current_second = 0
        self._last_rtc_sync = time.ticks_add(time.ticks_ms(), -60001)  # force sync on first tick
        
        # Alarm variables
        self.alarm_hour = 7
        self.alarm_minute = 0
        self.alarm_enabled = False
        self.alarm_active = False
        self.alarm_start_time = 0
        self.snooze_until = 0
        self.sound_type = 0  # Index into SOUND_TYPES list (default: first entry)
        self.led_enabled = True  # Sunrise LED on by default
        self._night_light_start = 0  # 0 = inactive
        self._light_ema = None        # exponential moving average of light sensor
        
        # Sunrise variables
        self.sunrise_stage = 0  # 0-255 for gradual brightening

        # Edit mode state (for setting alarm/clock time via encoder)
        self.edit_mode = None   # None | 'alrm_h' | 'alrm_m' | 'cloc_h' | 'cloc_m'
        self.edit_hour = 0
        self.edit_minute = 0
        self._blink_state = True
        self._blink_time = time.ticks_ms()

        # Feedback display: show a message for a short time after menu action
        self._feedback_until = 0  # ticks_ms() deadline; 0 = no feedback active
        self._feedback_msg = ''
        self._preview_until = 0   # stop DFPlayer preview after this time
        self.load_settings()
        
        print("Alarm Clock initialized!")
    
    def init_hardware(self):
        """Initialize all hardware components"""
        
        # TM1637 Display
        self.display = TM1637(
            clk=Pin(PINS['DISPLAY_CLK']),
            dio=Pin(PINS['DISPLAY_DIO'])
        )
        self.display.brightness(5)
        self.display.show("INIT")
        
        # I2C for RTC
        self.rtc = None
        try:
            self.i2c = I2C(0, scl=Pin(PINS['RTC_SCL']), sda=Pin(PINS['RTC_SDA']))
            self.rtc = DS3231(self.i2c)
        except Exception as e:
            print("RTC init failed:", e)
        
        # DFPlayer Mini
        self.uart = UART(UART_ID, baudrate=UART_BAUDRATE, 
                        tx=PINS['DFPLAYER_TX'], rx=PINS['DFPLAYER_RX'])
        self.dfplayer = DFPlayer(self.uart)
        self.dfplayer.volume(0)
        
        # WS2812B LED Strip
        self.leds = neopixel.NeoPixel(Pin(PINS['LED_DATA']), NUM_LEDS)
        self.clear_leds()
        
        # Rotary Encoder
        self.encoder = RotaryEncoder(
            clk_pin=PINS['ENCODER_CLK'],
            dt_pin=PINS['ENCODER_DT'],
            sw_pin=PINS['ENCODER_SW']
        )
        
        # Touch Sensors
        self.touch_snooze = TouchPad(Pin(PINS['TOUCH_SNOOZE']))
        self.touch_stop = TouchPad(Pin(PINS['TOUCH_STOP']))
        
        # Light Sensor
        self.light_sensor = ADC(Pin(PINS['LIGHT_SENSOR']))
        self.light_sensor.atten(ADC.ATTN_0DB)  # 0-1.1V range; sensor output is low voltage
        
        time.sleep(1)
    
    def load_settings(self):
        """Load alarm settings from non-volatile storage"""
        try:
            with open('alarm_settings.json', 'r') as f:
                settings = json.load(f)
                self.alarm_hour = settings.get('alarm_hour', 7)
                self.alarm_minute = settings.get('alarm_minute', 0)
                self.alarm_enabled = settings.get('alarm_enabled', False)
                self.sound_type = settings.get('sound_type', 0)
                self.led_enabled = settings.get('led_enabled', True)
            print(f"Loaded settings: Alarm {self.alarm_hour:02d}:{self.alarm_minute:02d}, Enabled: {self.alarm_enabled}")
        except:
            print("No saved settings found, using defaults")
    
    def save_settings(self):
        """Save alarm settings to non-volatile storage"""
        settings = {
            'alarm_hour': self.alarm_hour,
            'alarm_minute': self.alarm_minute,
            'alarm_enabled': self.alarm_enabled,
            'sound_type': self.sound_type,
            'led_enabled': self.led_enabled
        }
        with open('alarm_settings.json', 'w') as f:
            json.dump(settings, f)
        print("Settings saved")
    
    def clear_leds(self):
        """Turn off all LEDs"""
        for i in range(NUM_LEDS):
            self.leds[i] = (0, 0, 0)
        self.leds.write()
    
    def update_time(self):
        """Read from RTC once per minute; use ticks_ms drift for in-between seconds."""
        if self.rtc is None:
            return
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_rtc_sync) >= 60000:
            try:
                dt = self.rtc.get_time()
                self.current_hour = dt[4]
                self.current_minute = dt[5]
                self.current_second = dt[6]
                self._last_rtc_sync = now
            except OSError:
                pass  # Keep cached values; try again next minute
    
    def update_display_brightness(self):
        """Adjust display brightness based on smoothed light sensor (EMA)"""
        raw = self.light_sensor.read()
        # Exponential moving average: alpha=0.05 gives ~20s lag, removes flicker
        if self._light_ema is None:
            self._light_ema = raw
        else:
            self._light_ema = 0.05 * raw + 0.95 * self._light_ema
        light_value = int(self._light_ema)
        # Map sensor reading to display brightness
        brightness = self.map_value(
            light_value,
            LIGHT_SENSOR_MIN, LIGHT_SENSOR_MAX,
            DISPLAY_BRIGHTNESS_MIN, DISPLAY_BRIGHTNESS_MAX
        )
        brightness = max(DISPLAY_BRIGHTNESS_MIN, min(DISPLAY_BRIGHTNESS_MAX, brightness))
        self.display.brightness(brightness // 10)  # TM1637 uses 0-7 range
    
    def map_value(self, x, in_min, in_max, out_min, out_max):
        """Map a value from one range to another"""
        return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)
    
    def handle_encoder(self):
        """Process rotary encoder input"""
        rotation = self.encoder.get_rotation()
        clicked = self.encoder.get_click()

        if rotation != 0:
            self.last_menu_time = time.ticks_ms()

            if self.edit_mode is not None:
                self._handle_edit_rotation(rotation)
            elif self.in_menu:
                # Navigate menu
                self.menu_pos = (self.menu_pos + rotation) % (self.menu_max + 1)
                if self.menu_pos < 0:
                    self.menu_pos = self.menu_max
            else:
                # Enter menu on rotation
                self.in_menu = True
                self.menu_pos = 0  # Start at ALRM menu

        if clicked:
            self.last_menu_time = time.ticks_ms()
            if self.edit_mode is not None:
                self._handle_edit_click()
            else:
                self.handle_menu_action()
    
    def handle_menu_action(self):
        """Handle encoder button click based on current menu position"""
        if self.menu_pos == 0:  # ALRM - Set alarm time
            self.edit_hour = self.alarm_hour
            self.edit_minute = self.alarm_minute
            self.edit_mode = 'alrm_h'
            self._blink_state = True
            self._blink_time = time.ticks_ms()
        elif self.menu_pos == 1:  # ON-F - Toggle alarm
            self.alarm_enabled = not self.alarm_enabled
            self.save_settings()
            self._show_feedback(' ON ' if self.alarm_enabled else 'OFF ')
            self._flash_leds_status(self.alarm_enabled)
            print(f"Alarm {'enabled' if self.alarm_enabled else 'disabled'}")
        elif self.menu_pos == 2:  # SOND - Cycle sound type
            self.sound_type = (self.sound_type + 1) % len(SOUND_TYPES)
            self.save_settings()
            entry = SOUND_TYPES[self.sound_type]
            self._show_feedback(entry['name'])
            # Play a short preview at medium volume so user can hear the track
            self.dfplayer.volume(DFPLAYER_VOLUME_MAX // 2)
            self.dfplayer.play(entry['track'])
            self._preview_until = time.ticks_add(time.ticks_ms(), 5000)
            print(f"Sound type: {entry['name']}")
        elif self.menu_pos == 3:  # CLOC - Set current time
            if self.rtc is None:
                self._show_feedback('ERR ')
                return
            dt = self.rtc.get_time()
            self.edit_hour = dt[4]
            self.edit_minute = dt[5]
            self.edit_mode = 'cloc_h'
            self._blink_state = True
            self._blink_time = time.ticks_ms()
        elif self.menu_pos == 4:  # LED  - Toggle sunrise LED
            self.led_enabled = not self.led_enabled
            self.save_settings()
            self._show_feedback(' ON ' if self.led_enabled else 'OFF ')
            self._flash_leds_status(self.led_enabled)
            print(f"Sunrise LED {'enabled' if self.led_enabled else 'disabled'}")
    
    def _show_feedback(self, msg, duration_ms=2000):
        """Display a short message on the display for duration_ms milliseconds"""
        self._feedback_msg = msg
        self._feedback_until = time.ticks_add(time.ticks_ms(), duration_ms)

    def _flash_leds_status(self, enabled):
        """Briefly show green (alarm on) or red (alarm off) on all LEDs"""
        color = (0, 40, 0) if enabled else (40, 0, 0)
        for i in range(NUM_LEDS):
            self.leds[i] = color
        self.leds.write()

    def check_menu_timeout(self):
        """Return to clock display after timeout"""
        if self.in_menu or self.edit_mode is not None:
            if time.ticks_diff(time.ticks_ms(), self.last_menu_time) > MENU_TIMEOUT:
                self.in_menu = False
                self.edit_mode = None
                self.menu_pos = 0

    def _handle_edit_rotation(self, rotation):
        """Adjust the value currently being edited"""
        if self.edit_mode in ('alrm_h', 'cloc_h'):
            self.edit_hour = (self.edit_hour + rotation) % 24
        else:
            self.edit_minute = (self.edit_minute + rotation) % 60
        # Reset blink so user immediately sees the updated value
        self._blink_state = True
        self._blink_time = time.ticks_ms()

    def _handle_edit_click(self):
        """Advance to next edit field, or commit and save when done"""
        if self.edit_mode == 'alrm_h':
            self.edit_mode = 'alrm_m'
        elif self.edit_mode == 'alrm_m':
            self.alarm_hour = self.edit_hour
            self.alarm_minute = self.edit_minute
            self.save_settings()
            print(f"Alarm set to {self.alarm_hour:02d}:{self.alarm_minute:02d}")
            self.edit_mode = None
            self.in_menu = False
        elif self.edit_mode == 'cloc_h':
            self.edit_mode = 'cloc_m'
        elif self.edit_mode == 'cloc_m':
            if self.rtc is not None:
                dt = self.rtc.get_time()
                self.rtc.set_time(dt[0], dt[1], dt[2], dt[3],
                                  self.edit_hour, self.edit_minute, 0)
            print(f"Clock set to {self.edit_hour:02d}:{self.edit_minute:02d}")
            self.edit_mode = None
            self.in_menu = False
    
    def handle_touch(self):
        """Process touch sensor input"""
        try:
            touch_snooze_value = self.touch_snooze.read()
        except ValueError:
            touch_snooze_value = 0
        try:
            touch_stop_value = self.touch_stop.read()
        except ValueError:
            touch_stop_value = 0

        if TOUCH_THRESHOLD_MIN < touch_snooze_value < TOUCH_THRESHOLD_MAX:
            if self.alarm_active:
                self.snooze_alarm()
            elif self._night_light_start == 0:
                ema = self._light_ema if self._light_ema is not None else NIGHT_LIGHT_THRESHOLD + 1
                if ema < NIGHT_LIGHT_THRESHOLD:
                    self._night_light_start = time.time()
                    print("Night light on, t=", self._night_light_start)

        if TOUCH_THRESHOLD_MIN < touch_stop_value < TOUCH_THRESHOLD_MAX:
            if self.alarm_active:
                self.stop_alarm()
    
    def check_alarm(self):
        """Check if it's time to trigger the alarm"""
        if not self.alarm_enabled or self.alarm_active:
            return
        
        # Check if we're in snooze period
        if self.snooze_until > 0:
            if time.time() < self.snooze_until:
                return
            else:
                self.snooze_until = 0
                self.resume_alarm()
                return
        
        # Check if current time matches alarm time
        if self.current_hour == self.alarm_hour and self.current_minute == self.alarm_minute:
            if self.current_second == 0:  # Only trigger once per minute
                self.start_alarm()
    
    def start_alarm(self):
        """Start the alarm sequence"""
        print("ALARM! Starting alarm sequence...")
        self.alarm_active = True
        self.alarm_start_time = time.time()
        self.sunrise_stage = 0

        # Load per-track profile using track number from SOUND_TYPES list
        track = SOUND_TYPES[self.sound_type]['track']
        profile = SOUND_PROFILES.get(track, SOUND_PROFILES[1])
        self._vol_start = profile['vol_start']
        self._ramp_dur = profile['ramp_dur']

        # Start sound at the profile's starting volume and loop the track
        self.dfplayer.volume(self._vol_start)
        self.dfplayer.loop_track(track)
        self._alarm_elapsed = 0  # seconds of alarm time accumulated across snoozes
    
    def update_alarm(self):
        """Update alarm state during sunrise sequence"""
        if not self.alarm_active:
            return
        
        elapsed = time.time() - self.alarm_start_time
        
        # LED sunrise only runs if led_enabled
        if self.led_enabled:
            led_progress = min(elapsed / SUNRISE_DURATION, 1.0)
            self.update_sunrise_leds(led_progress)

        # Volume ramp uses per-track ramp_dur and vol_start
        ramp_progress = min(elapsed / self._ramp_dur, 1.0)
        volume = int(self._vol_start + ramp_progress * (DFPLAYER_VOLUME_MAX - self._vol_start))
        self.dfplayer.volume(volume)
        
        # Check if alarm has been running too long
        if elapsed > ALARM_MAX_DURATION:
            self.stop_alarm()
    
    def update_sunrise_leds(self, progress):
        """Create sunrise effect on LEDs (dark red -> orange -> yellow -> white)"""
        # Sunrise color palette
        if progress < 0.25:
            # Dark red to red
            brightness = int(progress * 4 * 255)
            r, g, b = brightness // 2, 0, 0
        elif progress < 0.5:
            # Red to orange
            stage = (progress - 0.25) * 4
            r = 128 + int(stage * 127)
            g = int(stage * 100)
            b = 0
        elif progress < 0.75:
            # Orange to yellow
            stage = (progress - 0.5) * 4
            r = 255
            g = 100 + int(stage * 155)
            b = 0
        else:
            # Yellow to white
            stage = (progress - 0.75) * 4
            r = 255
            g = 255
            b = int(stage * 255)
        
        # Set all LEDs to the same color
        for i in range(NUM_LEDS):
            self.leds[i] = (r, g, b)
        self.leds.write()
    
    def snooze_alarm(self):
        """Snooze the alarm: pause sound, keep LEDs, resume after SNOOZE_DURATION"""
        print(f"Snoozing for {SNOOZE_DURATION // 60} minutes...")
        # Save how far into the alarm we are so we can resume from here
        self._alarm_elapsed = time.time() - self.alarm_start_time
        self.alarm_active = False
        self.snooze_until = time.time() + SNOOZE_DURATION
        self.dfplayer.pause()
        # LEDs stay on — intentionally not calling clear_leds()
    
    def resume_alarm(self):
        """Resume alarm after snooze, continuing from where it paused"""
        print("Resuming alarm after snooze...")
        self.alarm_active = True
        # Wind back start_time so elapsed continues from where we left off
        self.alarm_start_time = time.time() - self._alarm_elapsed
        # Restore the volume we were at when snooze was pressed
        ramp_progress = min(self._alarm_elapsed / self._ramp_dur, 1.0)
        volume = int(self._vol_start + ramp_progress * (DFPLAYER_VOLUME_MAX - self._vol_start))
        self.dfplayer.volume(volume)
        self.dfplayer.resume()

    def stop_alarm(self):
        """Stop the alarm completely"""
        print("Alarm stopped")
        self.alarm_active = False
        self.snooze_until = 0
        self.dfplayer.stop()
        self.clear_leds()
    
    def update_display(self):
        """Update the display based on current mode"""
        # Feedback message overrides everything for a short time
        if self._feedback_until and time.ticks_diff(self._feedback_until, time.ticks_ms()) > 0:
            self.display.show(self._feedback_msg)
            return
        elif self._feedback_until:
            self._feedback_until = 0
            # Clear status LEDs only when alarm and night light are both inactive
            if not self.alarm_active and self._night_light_start == 0:
                self.clear_leds()

        if self.edit_mode is not None:
            self._update_edit_display()
        elif self.in_menu:
            # Show menu item
            self.display.show(MENU_ITEMS[self.menu_pos])
        else:
            # Show current time
            self.display.show_time(self.current_hour, self.current_minute)

    def _update_edit_display(self):
        """Show blinking hour or minute field while editing"""
        if time.ticks_diff(time.ticks_ms(), self._blink_time) > 500:
            self._blink_state = not self._blink_state
            self._blink_time = time.ticks_ms()

        h = self.edit_hour
        m = self.edit_minute
        seg = bytearray(4)

        if self.edit_mode in ('alrm_h', 'cloc_h'):
            # Hours blink, minutes steady
            seg[0] = self.display.encode_digit(h // 10) if self._blink_state else 0x00
            seg[1] = self.display.encode_digit(h % 10) if self._blink_state else 0x00
            seg[2] = self.display.encode_digit(m // 10)
            seg[3] = self.display.encode_digit(m % 10)
        else:
            # Hours steady, minutes blink
            seg[0] = self.display.encode_digit(h // 10)
            seg[1] = self.display.encode_digit(h % 10)
            seg[2] = self.display.encode_digit(m // 10) if self._blink_state else 0x00
            seg[3] = self.display.encode_digit(m % 10) if self._blink_state else 0x00

        seg[1] |= 0x80  # always show colon
        self.display.write(seg)
    
    def update_night_light(self):
        """Manage the night light: full white, then fade to off."""
        if self._night_light_start == 0 or self.alarm_active:
            return
        elapsed = time.time() - self._night_light_start
        total = NIGHT_LIGHT_ON_DURATION + NIGHT_LIGHT_DIM_DURATION
        if elapsed >= total:
            self._night_light_start = 0
            self.clear_leds()
            return
        if elapsed < NIGHT_LIGHT_ON_DURATION:
            brightness = 255
        else:
            # Linear fade from 255 to 0 over DIM_DURATION
            fade = (elapsed - NIGHT_LIGHT_ON_DURATION) / NIGHT_LIGHT_DIM_DURATION
            brightness = int(255 * (1.0 - fade))
        for i in range(NUM_LEDS):
            self.leds[i] = (brightness, brightness, brightness)
        self.leds.write()

    def run(self):
        """Main loop"""
        print("Starting main loop...")
        
        while True:
            try:
                # Update current time
                self.update_time()
                
                # Handle inputs
                self.handle_encoder()
                self.handle_touch()
                
                # Check menu timeout
                self.check_menu_timeout()
                
                # Update display brightness
                self.update_display_brightness()

                # Stop sound preview if its timer expired
                if self._preview_until and time.ticks_diff(time.ticks_ms(), self._preview_until) >= 0:
                    self._preview_until = 0
                    if not self.alarm_active:
                        self.dfplayer.stop()

                # Check and update alarm
                self.check_alarm()
                if self.alarm_active:
                    self.update_alarm()

                # Night light
                self.update_night_light()

                # Update display
                self.update_display()
                
                # Small delay
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                print("Shutting down...")
                self.stop_alarm()
                self.clear_leds()
                break
            except Exception as e:
                buf = uio.StringIO()
                sys.print_exception(e, buf)
                msg = buf.getvalue()
                print("Error in main loop:", msg)
                try:
                    with open('error.log', 'a') as f:
                        f.write("loop {} {}\n".format(time.time(), msg))
                except:
                    pass
                time.sleep(1)

# Main entry point
try:
    alarm_clock = AlarmClock()
    alarm_clock.run()
except Exception as e:
    buf = uio.StringIO()
    sys.print_exception(e, buf)
    msg = buf.getvalue()
    print("FATAL:", msg)
    try:
        with open('error.log', 'a') as f:
            f.write("boot {} {}\n".format(time.time(), msg))
    except:
        pass
    time.sleep(5)
    machine.reset()
