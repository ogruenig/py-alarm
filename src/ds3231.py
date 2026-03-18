"""
DS3231 RTC Driver for MicroPython
Real-time clock with I2C interface
"""

class DS3231:
    DS3231_I2C_ADDR = 0x68
    
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = self.DS3231_I2C_ADDR
        
        # Check if DS3231 is connected (warn only — caller handles absence)
        try:
            devices = self.i2c.scan()
            if self.addr not in devices:
                print("Warning: DS3231 not found at", hex(self.addr))
        except OSError as e:
            print("Warning: I2C scan failed:", e)
    
    def _bcd_to_dec(self, bcd):
        """Convert BCD to decimal"""
        return (bcd // 16) * 10 + (bcd % 16)
    
    def _dec_to_bcd(self, dec):
        """Convert decimal to BCD"""
        return (dec // 10) * 16 + (dec % 10)
    
    def get_time(self):
        """
        Get current time from RTC
        Returns tuple: (year, month, day, weekday, hour, minute, second)
        """
        # Read time registers (0x00 to 0x06)
        data = self.i2c.readfrom_mem(self.addr, 0x00, 7)
        
        second = self._bcd_to_dec(data[0] & 0x7F)
        minute = self._bcd_to_dec(data[1] & 0x7F)
        hour = self._bcd_to_dec(data[2] & 0x3F)
        weekday = self._bcd_to_dec(data[3] & 0x07)
        day = self._bcd_to_dec(data[4] & 0x3F)
        month = self._bcd_to_dec(data[5] & 0x1F)
        year = self._bcd_to_dec(data[6]) + 2000
        
        return (year, month, day, weekday, hour, minute, second)
    
    def set_time(self, year, month, day, weekday, hour, minute, second):
        """
        Set RTC time
        year: 2000-2099
        month: 1-12
        day: 1-31
        weekday: 1-7 (1=Monday)
        hour: 0-23
        minute: 0-59
        second: 0-59
        """
        data = bytearray(7)
        data[0] = self._dec_to_bcd(second)
        data[1] = self._dec_to_bcd(minute)
        data[2] = self._dec_to_bcd(hour)
        data[3] = self._dec_to_bcd(weekday)
        data[4] = self._dec_to_bcd(day)
        data[5] = self._dec_to_bcd(month)
        data[6] = self._dec_to_bcd(year - 2000)
        
        self.i2c.writeto_mem(self.addr, 0x00, data)
    
    def get_temperature(self):
        """
        Get temperature from DS3231 internal sensor
        Returns temperature in Celsius
        """
        data = self.i2c.readfrom_mem(self.addr, 0x11, 2)
        temp = data[0] + (data[1] >> 6) * 0.25
        if data[0] & 0x80:  # Negative temperature
            temp = temp - 256
        return temp
    
    def set_alarm(self, alarm_num, day, hour, minute, second, mode=0):
        """
        Set alarm (not implemented in basic version)
        Use software alarm checking instead
        """
        pass
    
    def format_time(self):
        """Return formatted time string HH:MM:SS"""
        dt = self.get_time()
        return f"{dt[4]:02d}:{dt[5]:02d}:{dt[6]:02d}"
    
    def format_date(self):
        """Return formatted date string YYYY-MM-DD"""
        dt = self.get_time()
        return f"{dt[0]:04d}-{dt[1]:02d}-{dt[2]:02d}"
