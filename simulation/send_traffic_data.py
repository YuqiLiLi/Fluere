import socket
import time
import random

def send_data(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode())
        print("Data sent:", data)


def dynamic_sleep_time(vehicle_count):
    if vehicle_count > 50:
        return 5  
    else:
        return 10  

if __name__ == "__main__":
    while True:
       
        traffic_data = random.randint(1, 60) 
        is_emergency = random.choice([0, 1]) 
        data_string = f"{traffic_data},{is_emergency}"
        send_data("localhost", 5000, data_string)
        sleep_time = dynamic_sleep_time(traffic_data)
        time.sleep(sleep_time)
