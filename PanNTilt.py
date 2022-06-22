import time
import math
from smbus2 import SMBus


# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================

class PCA9685:
    # Registers/etc.
    __SUBADR1       = 0x02
    __SUBADR2       = 0x03
    __SUBADR3       = 0x04
    __MODE1         = 0x00
    __MODE2         = 0x01
    __PRESCALE      = 0xFE
    __LED0_ON_L     = 0x06
    __LED0_ON_H     = 0x07
    __LED0_OFF_L    = 0x08
    __LED0_OFF_H    = 0x09
    __ALLLED_ON_L   = 0xFA
    __ALLLED_ON_H   = 0xFB
    __ALLLED_OFF_L  = 0xFC
    __ALLLED_OFF_H  = 0xFD

    # Bits:
    __RESTART   = 0x80
    __SLEEP     = 0x10
    __ALLCALL   = 0x01
    __INVRT     = 0x10
    __OUTDRV    = 0x04

    def __init__(self, address=0x40, debug=False):
        self.bus = SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        if (self.debug):
            print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        if (self.debug):
            print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def set_pwm_Freq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0  # 25MHz
        prescaleval /= 4096.0  # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        if (self.debug):
            print("Setting PWM frequency to %d Hz" % freq)
            print("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        if (self.debug):
            print("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1);
        newmode = (oldmode & 0x7F) | 0x10  # sleep
        self.write(self.__MODE1, newmode)  # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)
        self.write(self.__MODE2, 0x04)

    def set_pwm(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L + 4 * channel, on & 0xFF)
        self.write(self.__LED0_ON_H + 4 * channel, on >> 8)
        self.write(self.__LED0_OFF_L + 4 * channel, off & 0xFF)
        self.write(self.__LED0_OFF_H + 4 * channel, off >> 8)
        if (self.debug):
            print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def set_all_pwm(self, on, off):
        """Sets all PWM channels."""
        self.write(self.__ALLLED_ON_L, on & 0xFF)
        self.write(self.__ALLLED_ON_H, on >> 8)
        self.write(self.__ALLLED_OFF_L, off & 0xFF)
        self.write(self.__ALLLED_OFF_H, off >> 8)

    def set_servo_pulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse * 4096 / 20000  # PWM frequency is 50HZ,the period is 20000us
        self.set_pwm(channel, 0, int(pulse))

    def set_rotation_angle(self, channel, Angle):
        if (Angle >= 0 and Angle <= 180):
            temp = Angle * (2000 / 180) + 501
            self.set_servo_pulse(channel, temp)
        else:
            print("Angle out of range")

    def start_PCA9685(self):
        self.set_all_pwm(0, 0)
        self.write(self.__MODE2, self.__OUTDRV)
        self.write(self.__MODE1, self.__ALLCALL)
        time.sleep(0.005)  # wait for oscillator
        mode1 = self.read(self.__MODE1)
        mode1 = mode1 & ~self.__SLEEP  # wake up (reset sleep)
        self.write(self.__MODE1, mode1)
        time.sleep(0.005)
        # Just restore the stopped state that should be set for exit_PCA9685

    def exit_PCA9685(self):
        self.write(self.__MODE2, 0x00)  # Please use initialization or __MODE2 =0x04
