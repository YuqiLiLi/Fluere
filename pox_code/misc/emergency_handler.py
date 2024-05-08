from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
import pox.lib.packet as pkt
from pox.lib.recoco import Timer
import socket
import threading

log = core.getLogger()

class EmergencyVehicleHandler(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)

    def resend_packet(self, packet_in, action):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        msg.actions.append(action)
        msg.in_port = packet_in.in_port
        self.connection.send(msg)

    def act_on_decision(self, packet, packet_in, decision):
        if decision == "Clear Path Quickly for Ambulance" or decision == "Clear Wide Path for Fire Truck":
            
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet)
            msg.priority = 65535 
            msg.actions.append(of.ofp_action_output(port=of.OFPP_NORMAL))
            self.connection.send(msg)
            log.info("Clearing path for emergency vehicle.")
        else:
           
            self.resend_packet(packet_in, of.ofp_action_output(port=of.OFPP_NORMAL))

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet:
            return

        packet_in = event.ofp
        decision = self.wait_for_decision() 
        self.act_on_decision(packet, packet_in, decision)

    def wait_for_decision(self):
        
        return "Clear Path for Emergency Vehicle"  

def handle_incoming_decisions():
    host = ''
    port = 12345
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        log.info('Connected by %s' % str(addr))
        while True:
            data = conn.recv(1024)
            if not data:
                break
            decision = data.decode()
            log.info("Received decision: %s" % decision)
           

def launch():
    
    decision_thread = threading.Thread(target=handle_incoming_decisions)
    decision_thread.daemon = True
    decision_thread.start()

    def start_switch(event):
        log.info("Controlling %s" % (dpid_to_str(event.dpid),))
        handler = EmergencyVehicleHandler(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
