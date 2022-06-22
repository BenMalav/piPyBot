from smbus2 import SMBus

class Motor:
    # ******I2C command definitions*************/
    MotorSpeedSet = 0x82
    PWMFrequencySet = 0x84
    DirectionSet = 0xaa
    MotorSetA = 0xa1
    MotorSetB = 0xa5
    Nothing = 0x01
    # **************Motor ID**********************/
    MOTOR1 = 1
    MOTOR2 = 2
    # **************Motor Direction***************/
    BothClockWise = 0x0a
    BothAntiClockWise = 0x05
    M1CWM2ACW = 0x06
    M1ACWM2CW = 0x09
    # **************Motor Direction***************/
    ClockWise = 0x0a
    AntiClockWise = 0x05
    # **************Pre-scaler Frequencies***********/
    F_31372Hz = 0x01
    F_3921Hz = 0x02
    F_490Hz = 0x03
    F_122Hz = 0x04
    F_30Hz = 0x05

    def __init__(self, address=0x0f, debug=False):
        self.bus = SMBus(1)
        self.address = address
        self.debug = debug
        if (self.debug):
            print("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)
