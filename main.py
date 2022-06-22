from smbus2 import SMBus
import PanNTilt

i2c_devices = {'GROVE_MOTOR': 0x0f,
            'LIGHT_SENSOR': 0x29,
            'PAN_N_TILT': 0x40,
            'LSM9DS1_ADDRESS_ACCELGYRO': 0x6B,
            'LSM9DS1_ADDRESS_MAG': 0x1E,
            'BMP180': 0x77}

def scan(force=False):
    devices = []
    for addr in range(0x03, 0x77 + 1):
        read = SMBus.read_byte, (addr,), {'force':force}
        write = SMBus.write_byte, (addr, 0), {'force':force}

        for func, args, kwargs in (read, write):
            try:
                with SMBus(1) as bus:
                    data = func(bus, *args, **kwargs)
                    devices.append(hex(addr))
                    break
            except OSError as expt:
                if expt.errno == 16:
                    # just busy, maybe permanent by a kernel driver or just temporary by some user code
                    pass

    return devices

def check_modules():
    scanned_list = scan(force=True)

    devices = i2c_devices.items()

    for module in devices:
        if hex(module[1]) in scanned_list:
            print(module[0] + ' ' + hex(module[1]) + ":CONNECTED")
        else:
            print(module[0] + ' ' + hex(module[1]) + ":NOT CONNECTED")

if __name__ == '__main__':
    check_modules()

    pan_driver = PanNTilt.PCA9685()
    pan_driver.start_PCA9685()
    pan_driver.set_pwm_Freq(50)

    # y axis control channel 1 range(5,100)
    pan_driver.set_rotation_angle(1,40)
    # x axis control channel 0 range(10, 120)
    pan_driver.set_rotation_angle(0,120)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
