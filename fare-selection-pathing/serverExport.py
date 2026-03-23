import duckGraph
import duckAPI
import zmq
import time
import math

PUBPORT = 5557
SUBPORT = 5558

g = duckGraph.NavGraph()
g.readGraph("graph.txt", "adj.txt")

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{PUBPORT}")
sub_socket = context.socket(zmq.SUB)
sub_socket.connect(f"tcp://127.0.0.1:5559")
sub_socket.subscribe("")

def sendDirs(path):
    try:
        msg = {"topic": "DIRECTIONS", "dirs": path, "time": time.time()}
        pub_socket.send_json(msg)
    except Exception as e:
        print(f"[ZMQ] Error publishing directions: {e}")

def duckReady():
    try:
        while True:
            msg = sub_socket.recv_json(flags=zmq.NOBLOCK)
            if msg.get("topic") == "DUCK_READY" and msg.get("ready", False):
                return True
    except zmq.Again:
        pass
    except Exception as e:
        print(f"Issue getting ready status: {e}")
    return False

def stopped(ans):
    try:
        msg = {"topic": "STOP", "stopTheCar": ans, "time": time.time()}
        pub_socket.send_json(msg)
    except Exception as e:
        print(f"[ZMQ] Error publishing stop state: {e}")

def close():
    pub_socket.close()
    sub_socket.close()
    print("[ZMQ] Sockets closed")

def wait_for_duck_ready(fareID, timeout=60):
    start = time.time()
    while not duckReady():
        if time.time() - start > timeout:
            print("WARNING: duck_ready timeout, dropping fare and continuing")
            duckAPI.dropFare(fareID)
            return False
        time.sleep(0.5)
    return True

def main():
    resp = duckAPI.getMatchInfo()
    while resp['inMatch'] and resp['timeRemain'] > 0:
        stopped(False)
        print("Getting best fare...")
        while True:
            fareID, info = g.getBestFare()
            srcX, srcY, destX, destY, score, p1, p2, points1, points2 = info
            if duckAPI.claimFare(fareID):
                print("Claimed best fare")
                break

        sendDirs(p1)
        print("Navigating to pickup...")
        g.updatePosition()
        while math.sqrt((g.carX - srcX)**2 + (g.carY - srcY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, p = g.navigate(g.heading, g.carX, g.carY, srcX, srcY)
            sendDirs(dirs)
            time.sleep(0.2)

        while not duckAPI.checkCurrFare()['pickedUp']:
            time.sleep(0.1)

        # Arrived at pickup — send stop on heartbeat
        print("Arrived at pickup")
        last_stop_send = 0
        while not duckReady():
            if time.time() - last_stop_send > 0.5:
                stopped(True)
                last_stop_send = time.time()
            if time.time() - last_stop_send > 60:
                print("WARNING: duck_ready timeout, dropping fare")
                duckAPI.dropFare(fareID)
                break
            time.sleep(0.1)

        # Resume — send stopped(False) a few times to ensure delivery
        for _ in range(3):
            stopped(False)
            time.sleep(0.05)
        print("Picked up, navigating to drop off...")

        sendDirs(p2)
        g.updatePosition()
        while math.sqrt((g.carX - destX)**2 + (g.carY - destY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, p = g.navigate(g.heading, g.carX, g.carY, destX, destY)
            sendDirs(dirs)
            time.sleep(0.2)

        while not duckAPI.checkCurrFare()['completed']:
            time.sleep(0.1)

        # Arrived at dropoff
        print("Arrived at drop off")
        last_stop_send = 0
        while not duckReady():
            if time.time() - last_stop_send > 0.5:
                stopped(True)
                last_stop_send = time.time()
            if time.time() - last_stop_send > 60:
                print("WARNING: duck_ready timeout at dropoff")
                duckAPI.dropFare(fareID)
                break
            time.sleep(0.1)

        for _ in range(3):
            stopped(False)
            time.sleep(0.05)

        resp = duckAPI.getMatchInfo()
    close()

if __name__ == "__main__":
    main()