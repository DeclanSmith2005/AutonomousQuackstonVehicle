import json
import socket
import time

DEFAULT_ADDR = ("127.0.0.1", 5005)

class UdpDetectionSender:
    def __init__(self, addr=DEFAULT_ADDR):
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, objects, frame_id):
        msg = {
            "timestamp": time.time(),
            "frame_id": frame_id,
            "objects": objects,
        }
        self.sock.sendto(json.dumps(msg).encode("utf-8"), self.addr)