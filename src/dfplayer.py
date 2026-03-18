"""
DFPlayer Mini Driver for MicroPython
Simplified UART control for MP3 playback
Based on DFRobotDFPlayerMini protocol
"""

import time

class DFPlayer:
    def __init__(self, uart):
        self.uart = uart
        self.current_volume = 15
        time.sleep(0.5)  # Wait for DFPlayer to initialize
        self.reset()
    
    def _send_command(self, cmd, param1=0, param2=0):
        """Send command to DFPlayer"""
        # DFPlayer command structure: 
        # [0] Start byte: 0x7E
        # [1] Version: 0xFF
        # [2] Length: 0x06
        # [3] Command
        # [4] Feedback: 0x00 (no feedback) or 0x01 (feedback)
        # [5] Parameter high byte
        # [6] Parameter low byte
        # [7-8] Checksum
        # [9] End byte: 0xEF
        
        buffer = bytearray(10)
        buffer[0] = 0x7E  # Start
        buffer[1] = 0xFF  # Version
        buffer[2] = 0x06  # Length
        buffer[3] = cmd   # Command
        buffer[4] = 0x00  # No feedback
        buffer[5] = param1  # Parameter high byte
        buffer[6] = param2  # Parameter low byte
        
        # Calculate checksum
        checksum = -(buffer[1] + buffer[2] + buffer[3] + buffer[4] + buffer[5] + buffer[6])
        checksum = checksum & 0xFFFF
        buffer[7] = (checksum >> 8) & 0xFF  # Checksum high byte
        buffer[8] = checksum & 0xFF         # Checksum low byte
        buffer[9] = 0xEF  # End
        
        self.uart.write(buffer)
        time.sleep(0.1)  # Small delay between commands
    
    def reset(self):
        """Reset the DFPlayer module"""
        self._send_command(0x0C)
        time.sleep(1)
    
    def play(self, track_number):
        """Play specific track (1-255)"""
        self._send_command(0x03, 0x00, track_number)
    
    def stop(self):
        """Stop playback"""
        self._send_command(0x16)
    
    def pause(self):
        """Pause playback"""
        self._send_command(0x0E)
    
    def resume(self):
        """Resume playback"""
        self._send_command(0x0D)
    
    def next(self):
        """Play next track"""
        self._send_command(0x01)
    
    def previous(self):
        """Play previous track"""
        self._send_command(0x02)
    
    def volume(self, vol):
        """Set volume (0-30)"""
        vol = max(0, min(30, vol))
        self.current_volume = vol
        self._send_command(0x06, 0x00, vol)
    
    def volume_up(self):
        """Increase volume"""
        if self.current_volume < 30:
            self.current_volume += 1
            self.volume(self.current_volume)
    
    def volume_down(self):
        """Decrease volume"""
        if self.current_volume > 0:
            self.current_volume -= 1
            self.volume(self.current_volume)
    
    def set_source(self, source):
        """Set playback source (1=USB, 2=SD, 3=AUX, 4=SLEEP, 5=FLASH)"""
        self._send_command(0x09, 0x00, source)
    
    def loop_track(self, track_number):
        """Loop a specific track"""
        self._send_command(0x08, 0x00, track_number)
    
    def loop_all(self):
        """Loop all tracks"""
        self._send_command(0x11, 0x00, 0x01)
