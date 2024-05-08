import socket

def start_server():
    host = ''
    port = 5000
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        print('Server started. Waiting for connection...')
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    vehicle_data = data.decode()
                    vehicle_count, is_emergency = map(int, vehicle_data.split(","))
                    decision = process_traffic_data(vehicle_count, is_emergency)
                    print("Decision:", decision)

def process_traffic_data(vehicle_count, is_emergency):
    traffic_threshold = 50
    if is_emergency:
        return "Clear Path for Emergency Vehicle"
    elif vehicle_count > traffic_threshold:
        return "Block Traffic"
    else:
        return "Allow Traffic"

if __name__ == "__main__":
    start_server()
