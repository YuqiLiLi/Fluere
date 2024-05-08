from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, EthAddr
from pox.lib.util import dpid_to_str
import pox.lib.packet as pkt

log = core.getLogger()

class TrafficController(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        self.hard_timeout = 30  # Flow entry hard timeout

    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def act_like_router(self, packet, packet_in):
        # Check for IP packets from emergency vehicles
        ip = packet.find('ipv4')
        if ip and IPAddr('10.0.1.1') <= ip.srcip <= IPAddr('10.0.1.3'):  # Range of emergency vehicle IPs
            # Set high priority
            msg = of.ofp_flow_mod()
            msg.match = of.ofp_match.from_packet(packet, packet_in.in_port)
            msg.idle_timeout = 10
            msg.hard_timeout = self.hard_timeout
            msg.priority = 65535  # Highest priority
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            self.connection.send(msg)
        else:
            # Normal handling for other packets
            self.resend_packet(packet_in, of.OFPP_FLOOD)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp
        self.act_like_router(packet, packet_in)

def launch():
    def start_switch(event):
        log.info("Controlling %s" % (event.connection,))
        TrafficController(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)