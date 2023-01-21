import spidev
import time

class ADIS16470:
    def __init__(self):
        self.spi = spidev.SpiDev()
        self.spi.open(8, 0)
        self.spi.max_speed_hz = 1000000
        self.spi.mode = 0b11
        self.spi.lsbfirst = False


    def convert_deci_to_deg_per_sec(deci):
        return str((deci / 10)) + ' deg/sec' 


    def convert_deci_to_milli_g_force(deci):
        milli_g_force = deci * 1.25
        g_force = milli_g_force / 1000

        meter_per_square_second = g_force * 9.80665

        return str(round(meter_per_square_second, 2)) + ' m/s²'


    def convert_deci_to_degree(deci):
        degree = deci * 0.065917969
        return str(round(degree, 4)) + 'ᵒ'


    def convert_deci_to_velocity(deci):
        velocity = deci * 0.012207031
        return str(round(velocity, 4)) + ' m/sec'


    def read_signed_decimal(address):
        decimal_list = spi.xfer([address, 0x00])
        # print(decimal_list)
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



    def read_x_gyro_out():
        return convert_deci_to_deg_per_sec(read_signed_decimal(0x07))    


    def read_y_gyro_out():
        return convert_deci_to_deg_per_sec(read_signed_decimal(0x0B))    


    def read_z_gyro_out():
        return convert_deci_to_deg_per_sec(read_signed_decimal(0x0F))    


    def read_x_accl_out():
        return convert_deci_to_milli_g_force(read_signed_decimal(0x13))    


    def read_y_accl_out():
        return convert_deci_to_milli_g_force(read_signed_decimal(0x17))    


    def read_z_accl_out():
        return convert_deci_to_milli_g_force(read_signed_decimal(0x1B))    


    def read_x_deltang_out():
        return convert_deci_to_degree(read_signed_decimal(0x27))    


    def read_y_deltang_out():
        return convert_deci_to_degree(read_signed_decimal(0x2B))    


    def read_z_deltang_out():
        return convert_deci_to_degree(read_signed_decimal(0x2F))    


    def read_x_deltvel_out():
        return convert_deci_to_velocity(read_signed_decimal(0x33))    


    def read_y_deltvel_out():
        return convert_deci_to_velocity(read_signed_decimal(0x37))    


    def read_z_deltvel_out():
        return convert_deci_to_velocity(read_signed_decimal(0x3B))    
