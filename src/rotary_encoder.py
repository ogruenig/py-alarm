"""
Rotary Encoder Driver for MicroPython
Handles rotation detection and button press
"""

from machine import Pin
import time

class RotaryEncoder:
    def __init__(self, clk_pin, dt_pin, sw_pin):
        self.clk = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(sw_pin, Pin.IN, Pin.PULL_UP)

        self._steps = 0           # detent count, updated by ISR
        self._last_clk = self.clk.value()
        self.last_button_state = 1
        self.last_button_time = 0
        self.debounce_delay = 50  # milliseconds

        # Interrupt on both edges of CLK to catch every pulse
        self.clk.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING,
                     handler=self._clk_isr)

    def _clk_isr(self, pin):
        clk = pin.value()
        if clk != self._last_clk:
            # Each pair of pulses = 1 detent; count raw pulses, divide in get_rotation
            self._steps += -1 if self.dt.value() != clk else 1
        self._last_clk = clk

    def get_rotation(self):
        """Return number of detents turned since last call (+CW, -CCW, 0=none)."""
        raw = self._steps
        if raw == 0:
            return 0
        self._steps = 0
        # 2 raw pulses per detent on most encoders
        steps = raw // 2
        # keep any leftover sub-detent pulse for next call
        self._steps = raw - steps * 2
        return steps

    def get_click(self):
        """Returns True if button was clicked (with debouncing)"""
        current_time = time.ticks_ms()
        button_state = self.sw.value()

        if button_state == 0 and self.last_button_state == 1:
            if time.ticks_diff(current_time, self.last_button_time) > self.debounce_delay:
                self.last_button_time = current_time
                self.last_button_state = button_state
                return True

        self.last_button_state = button_state
        return False
