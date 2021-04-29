import socket
from .packet import Packet
from .common import *
from .controlblock import ControlBlock
from .coutput import Coutput
from .cinput import Cinput
import logging

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
        if packet.is_synack():
            logging.info("Received SYNACK")
            logging.info("Active Opener ESTABLISHED")
            self.cb.state = ESTABLISHED
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
            self.coutput.cirt_output()
            # wait for ack from active opener
            packet, address = self.cinput.cirt_input()
            if packet.is_ack():
                logging.info("Passive Opener ESTABLISHED")
                self.cb.state = ESTABLISHED



    def send(self, data):
        print("send some data!")


    def recv(self, size):
        print("receive some data!")


    def close(self):
        print("we done here")
