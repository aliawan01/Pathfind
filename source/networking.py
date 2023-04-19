import pygame
from pygame.locals import *

import socket
import threading
import sys

class Client:
    def __init__(self, ip_address):
        self.server_ip_address = ip_address
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(ip_address.encode())


class Server:
    def __init__(self):
        pass