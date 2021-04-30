import socket
from .packet import Packet
from .common import *
from .controlblock import ControlBlock
from .coutput import Coutput
from .cinput import Cinput
import logging
import time

class Socket:
    def __init__(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.cb = ControlBlock()
        self.cb.sock = sock
        self.coutput = Coutput(self.cb)
        self.cinput = Cinput(self.cb)
        

    ##################################################################
    # API Calls - used by the client and server.
    # All your hard work is hidden by these few functions.
    # Let's take a moment to thank everyone who has worked on
    # implementing TCP for our respective operating systems.
    ##################################################################
    def connect(self, address):
        print("connect!")
        self.cb.dst = address
        self.coutput.cirt_output()
        # wait for synack
        packet, address = self.cinput.cirt_input()
        # check for valid synack
        if packet.is_synack() and packet.ackno == self.cb.seqno + 1:
            logging.info("Received SYNACK")
            logging.info("Active Opener ESTABLISHED")
            self.cb.state = ESTABLISHED
            self.cb.seqno += 1
            self.cb.ackno = packet.seqno + 1 
            self.coutput.cirt_output()



    def listen(self, port):
        addr = ('127.0.0.1', port)
        self.cb.sock.bind(addr)
        self.cb.state = LISTEN


    def accept(self):
        # send a syn ack
        packet, address = self.cinput.cirt_input()
        if packet.is_syn():
            logging.info("Received SYN packet")
            print("accept connection!")
            # send syn and ack
            self.cb.state = SYN_RECV
            self.cb.dst = address
            self.cb.seqno = S_ISN
            self.cb.ackno = packet.seqno + 1
            self.coutput.cirt_output()
            # wait for ack from active opener
            packet, address = self.cinput.cirt_input()
            if packet.is_ack() and packet.ackno == self.cb.seqno + 1:
                logging.info("Passive Opener ESTABLISHED")
                self.cb.seqno = packet.ackno
                self.cb.state = ESTABLISHED



    def send(self, data):
        print("send some data!")
        self.coutput.cirt_output(data=data)
        self.cb.seqno += len(data)
        # wait for ack before being able to send more
        is_ack = False
        while not is_ack:
            packet, address = self.cinput.cirt_input()
            is_ack = packet.is_ack() and packet.ackno == self.cb.seqno




    def recv(self, size):
        print("receive some data!")
        packet, address = self.cinput.cirt_input()
        if packet.is_fin():
            # we have a valid fin segment, ack and fin
            self.cb.state = CLOSE_WAIT
            logging.info(f"State = {self.cb.state}")
            self.cb.ackno = packet.ackno + 1
            self.coutput.cirt_output()
            self.cb.state = LAST_ACK
            logging.info(f"State = {self.cb.state}")
            self.cb.ackno = self.cb.ackno + MSS + 1
            self.coutput.cirt_output()
            packet, address = self.cinput.cirt_input()
            if packet.is_ack() and packet.ackno == self.cb.ackno + 1:
                self.cb.state = CLOSED
                logging.info("Passive CLOSED")
        elif len(packet.data) > 0:
            #packet has data, send back ack
            self.cb.ackno = packet.seqno + len(packet.data)
            self.coutput.cirt_output()
            return packet.data



    def close(self):
        print("we done here")
        # if already closed you're done
        if self.cb.state == CLOSED:
            return
        self.cb.state = FIN_WAIT_1
        logging.info(f"State = {self.cb.state}")
        # ackno for last data sent from client to server
        self.cb.ackno = 0
        # seqno = current seqno server expects, already set
        self.coutput.cirt_output()
        packet, address = self.cinput.cirt_input()
        if packet.is_ack() and packet.ackno == 1:
            # valid fin ack
            self.cb.state = FIN_WAIT_2
            logging.info(f"State = {self.cb.state}")
            # wait for fin from the other side
            packet, address = self.cinput.cirt_input()
            # if packet.is_fin() and packet.ackno == self.cb.seqno + MSS + 1:
            # valid fin from other side
            self.cb.state = TIME_WAIT
            self.cb.ackno = packet.ackno + 1
            self.coutput.cirt_output()
            print("Waiting 1 minute to close.")
            time.sleep(60)
            self.cb.state = CLOSED
            logging.info("Server Connection CLOSED")
            
