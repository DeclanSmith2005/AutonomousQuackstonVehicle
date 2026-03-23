import duckGraph
import duckAPI
import zmq
import time
import math

PUBPORT = 5557
SUBPORT = 5558

g = duckGraph.NavGraph()
g.readGraph("graph.txt", "adj.txt")
fareID, srcX, srcY, destX, destY, score, p1, p2 = -1, -1, -1, -1, -1, -1, [], []
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{PUBPORT}")
sub_socket = context.socket(zmq.SUB)
sub_socket.bind(f"tcp://*:{SUBPORT}")
sub_socket.subscribe("")  # Subscribe to all topics

def sendDirs(path):
    try:
        msg = {
            "topic": "DIRECTIONS",
            "dirs" : path,
            "time" : time.time()
        }
        pub_socket.send_json(msg)
    except Exception as e:
        print(f"[ZMQ] Error publishing directions: {e}")

def duckReady():
    try:
        msg = sub_socket.recv_json(flags=zmq.NOBLOCK)
        topic = msg.get("topic")
        if topic == "DUCK_READY":
            return msg.get("ready", False)
    except zmq.Again:
        pass  # No message available yet
    except Exception as e:
        print(f" issue getting ready status: {e}")
    return False

def stopped(ans):
    try:
        msg = {
            "topic": "STOP",
            "stopTheCar" : ans,
            "time" : time.time()
        }
        pub_socket.send_json(msg)
    except Exception as e:
        print(f"[ZMQ] Error publishing stop state: {e}")

def close(self):
        """Clean up ZMQ resources."""
        pub_socket.close()
        sub_socket.close()
        print("[ZMQ] Sockets closed")

def main():
    resp = duckAPI.getMatchInfo()
    while resp['inMatch'] and resp['timeRemain'] > 0:
        stopped(False)
        print("getting best fare")
        while True:
            fareID, info = g.getBestFare()
            srcX, srcY, destX, destY, score, p1, p2, points1, points2 = info
            if duckAPI.claimFare(fareID) == True:
                print("claimed best fare")
                break
        sendDirs(p1)
        print("navigating to pickup")
        while math.sqrt((g.carX - srcX)**2 + (g.carY - srcY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, p = g.navigate(g.heading, g.carX, g.carY, srcX, srcY)
            sendDirs(dirs)
        stopped(True)
        print("arrived at pickup")
        while not duckReady():
            time.sleep(0.5)
        stopped(False)
        print("picked up, navigating to drop off")

        sendDirs(p2)
        while math.sqrt((g.carX - destX)**2 + (g.carY - destY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, p = g.navigate(g.heading, g.carX, g.carY, destX, destY)
            sendDirs(dirs)
        stopped(True)
        print("arrived at drop off")

        while not duckReady():
            time.sleep(0.5)

        resp = duckAPI.getMatchInfo()
    close()
        
if __name__ == "__main__":
    main()