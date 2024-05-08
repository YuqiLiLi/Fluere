import traci
import csv

def set_all_green(junction_id):
    current_state = traci.trafficlight.getRedYellowGreenState(junction_id)
    num_signals = len(current_state)
    green_state = 'G' * num_signals
    traci.trafficlight.setRedYellowGreenState(junction_id, green_state)

def collect_edge_data(edge_ids):
    data = []
    for edge_id in edge_ids:
        speed = traci.edge.getLastStepMeanSpeed(edge_id)
        occupancy = traci.edge.getLastStepOccupancy(edge_id)
        data.append((edge_id, speed, occupancy))
    return data

def move_non_emergency_to_right(vehicles):
    for veh_id in vehicles:
        if traci.vehicle.getTypeID(veh_id) != "emergencyVehicle":
            current_lane = traci.vehicle.getLaneIndex(veh_id)
            rightmost_lane = 0
            if current_lane != rightmost_lane:
                traci.vehicle.changeLane(veh_id, rightmost_lane, 10)

def run_simulation():
    traci.start([
        'sumo-gui',  
        '-n', 'map/jhumap2.net.xml',  
        '-r', 'your_output_routes.rou.xml',  
        '--log', 'logfile.txt'  
    ])

    emergency_edges = set()

    with open('traffic_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Time", "EdgeID", "Speed", "Occupancy"])

        while traci.simulation.getMinExpectedNumber() > 0:
            traci.simulationStep()
            vehicles = traci.vehicle.getIDList()

            move_non_emergency_to_right(vehicles)

            for veh_id in vehicles:
                if traci.vehicle.getTypeID(veh_id) == "emergencyVehicle":
                
                    junction_id = traci.vehicle.getNextTLS(veh_id)[0][0] if traci.vehicle.getNextTLS(veh_id) else None
                    if junction_id:
                      
                        set_all_green(junction_id)

                    current_edge = traci.vehicle.getRoadID(veh_id)
                    emergency_edges.add(current_edge)


            if emergency_edges:
                edge_data = collect_edge_data(list(emergency_edges))
                for edge_id, speed, occupancy in edge_data:
                    writer.writerow([traci.simulation.getTime(), edge_id, speed, occupancy])

    traci.close()

if __name__ == '__main__':
    run_simulation()
