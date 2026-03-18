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
        
        self.last_clk_state = self.clk.value()
        self.rotation = 0
        self.clicked = False
        self.last_button_state = 1
        self.last_button_time = 0
        self.debounce_delay = 50  # milliseconds
    
    def get_rotation(self):
        """
        Returns rotation direction:
        1 for clockwise, -1 for counter-clockwise, 0 for no rotation
        """
        rotation_detected = 0
        clk_state = self.clk.value()
        
        if clk_state != self.last_clk_state:
            if self.dt.value() != clk_state:
                rotation_detected = 1  # Clockwise
            else:
                rotation_detected = -1  # Counter-clockwise
        
        self.last_clk_state = clk_state
        return rotation_detected
    
    def get_click(self):
        """
        Returns True if button was clicked (with debouncing)
        """
        current_time = time.ticks_ms()
        button_state = self.sw.value()
        
        # Detect falling edge (button press) with debounce
        if button_state == 0 and self.last_button_state == 1:
            if time.ticks_diff(current_time, self.last_button_time) > self.debounce_delay:
                self.last_button_time = current_time
                self.last_button_state = button_state
                return True
        
        self.last_button_state = button_state
        return False
