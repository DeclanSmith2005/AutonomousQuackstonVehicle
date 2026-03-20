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

def sendDirs(path, distToNextNode=0.0):
    try:
        msg = {
            "topic": "DIRECTIONS",
            "dirs" : path,
            "distToNextNode": distToNextNode,
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
        stopped(False)
        if not duckAPI.checkCurrFare()['fare']:
            while True:
                bestFare_res = g.getBestFare()
                fareID = bestFare_res[0]
                srcX, srcY, destX, destY, score, p1, p2, nextDist1, nextDist2 = bestFare_res[1]
                if duckAPI.claimFare(fareID):
                    break
        sendDirs(p1, nextDist1)
        
        while math.sqrt((g.carX - srcX)**2 + (g.carY - srcY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, distToNextNode = g.navigate(g.carX, g.carY, srcX, srcY)
            sendDirs(dirs, distToNextNode)
            time.sleep(0.5)
        stopped(True)


        while not duckAPI.checkCurrFare()['fare']['pickedUp']:
            time.sleep(0.5)
        stopped(False)

        sendDirs(p2, nextDist2)
        while math.sqrt((g.carX - destX)**2 + (g.carY - destY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, distToNextNode = g.navigate(g.carX, g.carY, destX, destY)
            sendDirs(dirs, distToNextNode)
            time.sleep(0.5)
        stopped(True)

        while not duckAPI.checkCurrFare()['fare']['completed']:
            time.sleep(0.5)
        
if __name__ == "__main__":
    main()