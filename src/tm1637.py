"""
TM1637 7-Segment Display Driver for MicroPython
4-digit display with colon
"""

import time
from machine import Pin

class TM1637:
    # Full ASCII lookup table starting at 0x20 (space) — mcauser/micropython-tm1637 encoding
    # index = ord(char) - 0x20
    _SEGMENTS = bytearray(
        b'\x00\x86\x22\x7e\x6d\xd2\x46\x20\x29\x0b\x21\x70\x10\x40\x80\x52'  # ' ' to '/'
        b'\x3f\x06\x5b\x4f\x66\x6d\x7d\x07\x7f\x6f\x09\x0d\x61\x48\x43\x53'  # '0' to '?'
        b'\x5f\x77\x7c\x39\x5e\x79\x71\x3d\x76\x06\x1e\x75\x38\x55\x54\x3f'  # '@' to 'O'
        b'\x73\x67\x50\x6d\x78\x3e\x1c\x2a\x76\x6e\x5b\x39\x52\x0f\x23\x08'  # 'P' to '_'
        b'\x20\x77\x7c\x39\x5e\x79\x71\x3d\x74\x02\x0e\x75\x30\x55\x54\x5c'  # '`' to 'o'
        b'\x73\x67\x50\x6d\x78\x1c\x1c\x2a\x76\x6e\x5b\x46\x30\x70\x01\x00'  # 'p' to DEL
    )
    
    def __init__(self, clk, dio, brightness=7):
        self.clk = clk
        self.dio = dio
        self._bright = brightness
        
        self.clk.init(Pin.OUT, value=0)
        self.dio.init(Pin.OUT, value=0)
        time.sleep_us(10)
        
        self._write_data_cmd()
        self._write_dsp_ctrl()
    
    def _start(self):
        """Send start signal"""
        self.dio(1)
        self.clk(1)
        time.sleep_us(10)
        self.dio(0)
    
    def _stop(self):
        """Send stop signal"""
        self.dio(0)
        self.clk(1)
        time.sleep_us(10)
        self.dio(1)
    
    def _write_byte(self, b):
        """Write a byte"""
        for i in range(8):
            self.clk(0)
            time.sleep_us(10)
            self.dio((b >> i) & 1)
            time.sleep_us(10)
            self.clk(1)
            time.sleep_us(10)
        
        # Wait for ACK
        self.clk(0)
        time.sleep_us(10)
        self.dio.init(Pin.IN)
        time.sleep_us(10)
        self.clk(1)
        time.sleep_us(10)
        ack = self.dio.value()
        self.clk(0)
        self.dio.init(Pin.OUT)
        time.sleep_us(10)
        
        return ack == 0
    
    def _write_data_cmd(self):
        """Write data command"""
        self._start()
        self._write_byte(0x40)  # Data command
        self._stop()
    
    def _write_dsp_ctrl(self):
        """Write display control command"""
        self._start()
        self._write_byte(0x88 | self._bright)
        self._stop()
    
    def brightness(self, val=None):
        """Set brightness (0-7)"""
        if val is None:
            return self._bright
        if 0 <= val <= 7:
            self._bright = val
            self._write_data_cmd()
            self._write_dsp_ctrl()
    
    def write(self, segments, pos=0):
        """Write raw segments to display"""
        if not 0 <= pos <= 3:
            raise ValueError("Position out of range")
        self._write_data_cmd()
        self._start()
        self._write_byte(0xC0 | pos)
        
        if isinstance(segments, int):
            self._write_byte(segments)
        else:
            for seg in segments:
                self._write_byte(seg)
        
        self._stop()
        self._write_dsp_ctrl()
    
    def encode_digit(self, digit):
        """Encode a single digit (0-9)"""
        return self._SEGMENTS[0x10 + digit] if 0 <= digit <= 9 else 0x00

    def encode_string(self, string):
        """Encode up to 4 characters using the full ASCII table"""
        segments = bytearray(4)
        for i in range(min(4, len(string))):
            c = ord(string[i])
            if 0x20 <= c <= 0x7f:
                segments[i] = self._SEGMENTS[c - 0x20]
        return segments
    
    def show(self, string, colon=False):
        """Show a string on the display"""
        segments = self.encode_string(string)
        if colon:
            segments[1] |= 0x80  # Add colon
        self.write(segments)
    
    def show_time(self, hours, minutes, colon=True):
        """Display time in HH:MM format"""
        segments = bytearray(4)
        segments[0] = self.encode_digit(hours // 10)
        segments[1] = self.encode_digit(hours % 10)
        segments[2] = self.encode_digit(minutes // 10)
        segments[3] = self.encode_digit(minutes % 10)
        
        if colon:
            segments[1] |= 0x80  # Add colon between hours and minutes
        
        self.write(segments)
    
    def clear(self):
        """Clear the display"""
        self.write([0, 0, 0, 0])
    
    def scroll(self, string, delay=300):
        """Scroll a string across the display"""
        string = "    " + string + "    "
        for i in range(len(string) - 3):
            self.show(string[i:i+4])
            time.sleep_ms(delay)
