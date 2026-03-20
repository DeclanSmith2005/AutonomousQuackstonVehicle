import duckGraph
import duckAPI
import zmq
import time
import math

PUBPORT = 5557

g = duckGraph.NavGraph()
g.readGraph("graph.txt", "adj.txt")
fareID, srcX, srcY, destX, destY, score, p1, p2 = -1, -1, -1, -1, -1, -1, [], []
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{PUBPORT}")

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

def main():
    while True:
        if not duckAPI.checkCurrFare()['fare']:
            while True:
                fareID, srcX, srcY, destX, destY, score, p1, p2 = g.getBestFare()
                if duckAPI.claimFare(fareID):
                    break
        sendDirs(p1)
        
        while math.sqrt((g.carX - srcX)**2 + (g.carY - srcY)**2) > 15:
            g.updatePosition()
            dirs, dist = g.navigate(g.carX, g.carY, srcX, srcY)
            sendDirs(dirs)
            time.sleep(0.5)

        stopped(True)

        sendDirs(p2)


            
if __name__ == "__main__":
    main()