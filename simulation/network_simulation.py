from mininet.node import Controller
from mininet.log import setLogLevel, info
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import OVSKernelAP
import threading
import socket
import heapq
import time
import csv


data_collected = []

def dijkstra(graph, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))
    distances = {start: 0}
    predecessors = {start: None}

    while queue:
        (current_distance, current_node) = heapq.heappop(queue)

        if current_node == goal:
            path = []
            while current_node is not None:
                path.insert(0, current_node)
                current_node = predecessors[current_node]
            return path

        for neighbor, weight in graph.get(current_node, []):
            distance = current_distance + weight
            if neighbor not in distances or distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(queue, (distance, neighbor))

    return []

def build_graph():
   
    return {
        'sta1': [('sta2', 1), ('sta3', 1)],
        'sta2': [('sta1', 1), ('sta3', 1)],
        'sta3': [('sta1', 1), ('sta2', 1)],
        'emergency1': [('sta1', 1)],
        'emergency2': [('sta2', 1)]
    }

def update_routes(net, best_path):
   
    for index in range(len(best_path) - 1):
        current_node = best_path[index]
        next_node = best_path[index + 1]
        net.get(current_node).cmd(f'route add default gw {next_node}')

def notify_vehicles(net, emergency_vehicle, all_vehicles):
    
    notification_times = {}
    for vehicle in all_vehicles:
        if vehicle != emergency_vehicle:
            start_notify = time.time()
            net.get(vehicle).cmd(f'echo "Clear the way for {emergency_vehicle}"')
            end_notify = time.time()
            notification_duration = end_notify - start_notify
            notification_times[vehicle] = notification_duration
            data_collected.append({
                "event": "Notify Vehicle",
                "vehicle": vehicle,
                "duration": notification_duration
            })

def handle_emergency(net, status, emergency_vehicle):
    
    start_time = time.time()  
    if status == "Clear Path for Emergency Vehicle":
        graph = build_graph()
        best_path = dijkstra(graph, emergency_vehicle, 'sta3')  # Example goal
        update_routes(net, best_path)
        notify_vehicles(net, emergency_vehicle, graph.keys())
    end_time = time.time()  
    data_collected.append({
        "event": "Handle Emergency",
        "duration": end_time - start_time,
        "path_length": len(best_path) if best_path else 0
    })

def listen_for_decisions(net):
    
    host = ''
    port = 9999
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()
        while True:
            conn, _ = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    vehicle, is_emergency = data.decode().split(",")
                    status = "Clear Path for Emergency Vehicle" if int(is_emergency) else "Allow Traffic"
                    handle_emergency(net, status, vehicle)

def save_data_to_csv(file_path):
    
    keys = data_collected[0].keys() if data_collected else []
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_collected)

def create_network():
    
    net = Mininet_wifi(controller=Controller, accessPoint=OVSKernelAP)
    info("*** Creating nodes\n")
    ap1 = net.addAccessPoint('ap1', ssid='new-ssid', mode='g', channel='1', position='50,50,0', range=100)
    fogNode = net.addHost('fogNode', ip='10.0.0.10')
    sta1 = net.addStation('sta1', ip='10.0.0.1', position='30,50,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2', position='70,50,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3', position='90,50,0')
    emergency1 = net.addStation('emergency1', ip='10.0.0.101', position='10,20,0')
    emergency2 = net.addStation('emergency2', ip='10.0.0.102', position='20,20,0')

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Adding controller\n")
    c0 = net.addController('c0')

    info("*** Creating links\n")
    net.addLink(ap1, fogNode)
    net.addLink(ap1, sta1)
    net.addLink(ap1, sta2)
    net.addLink(ap1, sta3)
    net.addLink(ap1, emergency1)
    net.addLink(ap1, emergency2)

    info("*** Starting network\n")
    net.build()
    c0.start()
    ap1.start([c0])

    
    threading.Thread(target=listen_for_decisions, args=(net,)).start()

    info("*** Running CLI\n")
    CLI(net)

    info("*** Stopping network\n")
    net.stop()

    
    save_data_to_csv('network_data.csv')

if __name__ == '__main__':
    setLogLevel('info')
    create_network()
