from .common import *
from .packet import Packet
import logging

logging.basicConfig(level=logging.INFO)

class Coutput:
    def __init__(self, cb):
        self.cb = cb


    def __send(self, packet):
        # comment out because we aren't using cwnd right now
        # logging.info(f'SEND SEQ:{packet.seqno} ACK:{packet.ackno} LEN:{len(packet.data)} CWND:{self.cb.cwnd} FLAG:{FLAG_STR[packet.flags]}')
        logging.info(f"dest = {self.cb.dst}")
        logging.info(f'SEND SEQ:{packet.seqno} ACK:{packet.ackno} LEN:{len(packet.data)} FLAG:{FLAG_STR[packet.flags]}')
        send_packet = packet.make_packet()
        logging.info(f"packet = {send_packet}")
        self.cb.sock.sendto(packet.make_packet(), self.cb.dst)
    
    
    def cirt_output(self):
        flag = OUT_FLAGS[self.cb.state]

        packet = Packet(self.cb.seqno, self.cb.ackno, 0, flag, b'')
        self.__send(packet)
