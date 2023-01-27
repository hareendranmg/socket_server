import spidev
import time
from datetime import datetime


class ADIS16470:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(8, 0)
        self.spi.max_speed_hz = 1000000
        self.spi.mode = 0b11
        self.spi.lsbfirst = False

    def __del__(self):
        self.spi.close()

    def convert_deci_to_deg_per_sec(self, deci):
        return str((deci / 10)) + ' deg/sec' 

    def convert_deci_to_milli_g_force(self, deci):
        milli_g_force = deci * 1.25
        g_force = milli_g_force / 1000
        meter_per_square_second = g_force * 9.80665

        return str(round(meter_per_square_second, 2)) + ' m/s²'

    def convert_deci_to_temp(self, deci):
        return str((deci / 10)) + 'ᵒC'

    def convert_deci_to_degree(self, deci):
        degree = deci * 0.065917969

        return str(round(degree, 4)) + 'ᵒ'

    def convert_deci_to_velocity(self, deci):
        velocity = deci * 0.012207031

        return str(round(velocity, 4)) + ' m/sec'

    def read_signed_decimal(self, address):
        try:
            decimal_list = self.spi.xfer([address, 0x00])
            if decimal_list is None or len(decimal_list) != 2:
                raise RuntimeError('Did not read expected number of bytes from device!')

            hex_list = [hex(x) for x in decimal_list]
            
            hex_int_1 = int(hex_list[0], 16)
            hex_int_2 = int(hex_list[1], 16)

            hex_16_bit = (hex_int_1 << 8 | hex_int_2)
            binary_string = bin(hex_16_bit)[2:].zfill(16)
            
            # Check if the binary number is negative (starts with 1)
            if binary_string[0] == '1':
                # Convert the binary number to an unsigned integer
                unsigned_decimal = int(binary_string, 2)
                # Subtract 65536 from the unsigned integer to get the signed decimal
                signed_decimal = unsigned_decimal - 65536

                return signed_decimal
            # If the binary number is not negative (starts with 0), simply convert it to an integer
            else:
                return int(binary_string, 2)
        except Exception as e:
            print(f'{datetime.now()}: {e}')
            return 0

    def read_x_gyro_out(self):
        return self.convert_deci_to_deg_per_sec(self.read_signed_decimal(0x07))    

    def read_y_gyro_out(self):
        return self.convert_deci_to_deg_per_sec(self.read_signed_decimal(0x0B))    

    def read_z_gyro_out(self):
        return self.convert_deci_to_deg_per_sec(self.read_signed_decimal(0x0F))    

    def read_x_accl_out(self):
        return self.convert_deci_to_milli_g_force(self.read_signed_decimal(0x13))    

    def read_y_accl_out(self):
        return self.convert_deci_to_milli_g_force(self.read_signed_decimal(0x17))    

    def read_z_accl_out(self):
        return self.convert_deci_to_milli_g_force(self.read_signed_decimal(0x1B))    
    
    def read_temp_out(self):
        return self.convert_deci_to_temp(self.read_signed_decimal(0x1D))    
    
    def read_timestamp_out(self):
        pass    

    # TODO: Fix delta angle for y and z axis

    def read_x_deltang_out(self):
        return self.convert_deci_to_degree(self.read_signed_decimal(0x27))    

    def read_y_deltang_out(self):
        return self.convert_deci_to_degree(self.read_signed_decimal(0x2B))    

    def read_z_deltang_out(self):
        return self.convert_deci_to_degree(self.read_signed_decimal(0x2F))    

    def read_x_deltvel_out(self):
        return self.convert_deci_to_velocity(self.read_signed_decimal(0x32))    

    def read_y_deltvel_out(self):
        return self.convert_deci_to_velocity(self.read_signed_decimal(0x36))    

    def read_z_deltvel_out(self):
        return self.convert_deci_to_velocity(self.read_signed_decimal(0x3A))    

    def read_data(self):
        accl_data = self.read_x_accl_out()+':'+self.read_y_accl_out()+':'+self.read_z_accl_out()
        delta_ang_data = self.read_x_deltang_out()+':'+self.read_y_deltang_out()+':'+self.read_z_deltang_out()
        delta_vel_data = self.read_x_deltvel_out()+':'+self.read_y_deltvel_out()+':'+self.read_z_deltvel_out()
        gyro_data = self.read_x_gyro_out()+':'+self.read_y_gyro_out()+':'+self.read_z_gyro_out()
        gyro_data = self.read_x_gyro_out()+':'+self.read_y_gyro_out()+':'+self.read_z_gyro_out()

        return gyro_data + "::" + accl_data + "::" + delta_ang_data + "::" + delta_vel_data 