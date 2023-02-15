import socket

camera_one_port = 1001
camera_two_port = 1002
radar_port = 1003
imu_port = 1004
gps_port = 1005
test_port = 1010

def get_host_ip():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        
        return host_ip
    except:
        return None