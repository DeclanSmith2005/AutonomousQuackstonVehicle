import duckGraph
import duckAPI
import zmq
import time
import math

PUBPORT = 5560
SUBPORT = 5561

g = duckGraph.NavGraph()
g.readGraph("graph.txt", "adj.txt")

context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{PUBPORT}")

def sendDirs(path):
    try:
        msg = {"topic": "DIRECTIONS", "dirs": path, "time": time.time()}
        pub_socket.send_json(msg)
    except Exception as e:
        print(f"[ZMQ] Error publishing directions: {e}")

def stopped(ans):
    try:
        msg = {"topic": "STOP", "stopTheCar": ans, "time": time.time()}
        pub_socket.send_json(msg)
    except Exception as e:
        print(f"[ZMQ] Error publishing stop state: {e}")

def wait_for_fare_status(fareID, field, timeout=60):
    """Poll checkCurrFare until fare[field] is True, or timeout and drop fare."""
    start = time.time()
    last_stop_send = 0
    while True:
        if time.time() - start > timeout:
            print(f"WARNING: timeout waiting for fare '{field}', dropping fare")
            duckAPI.dropFare(fareID)
            return False
        fare_resp = duckAPI.checkCurrFare()
        fare = fare_resp.get('fare') if fare_resp else None
        if fare is None:
            print("WARNING: no active fare found while waiting")
            time.sleep(0.5)
            continue
        # Send stopped(True) heartbeat while waiting
        if time.time() - last_stop_send > 0.5:
            stopped(True)
            last_stop_send = time.time()
        if fare.get(field, False):
            return True
        time.sleep(0.2)

def close():
    pub_socket.close()
    context.term()
    print("[ZMQ] Sockets closed")

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
            time.sleep(1.0)

        print("Picked up — resuming, navigating to drop off...")
        for _ in range(3):
            stopped(True)
            time.sleep(0.1)

        print("Near pickup — waiting for inPosition confirmation...")
        if not wait_for_fare_status(fareID, 'inPosition'):
            resp = duckAPI.getMatchInfo()
            continue

        print("In position — waiting for pickup confirmation...")
        if not wait_for_fare_status(fareID, 'pickedUp'):
            resp = duckAPI.getMatchInfo()
            continue

        print("Picked up — resuming, navigating to drop off...")
        for _ in range(3):
            stopped(False)
            time.sleep(0.1)

        sendDirs(p2)
        g.updatePosition()
        while math.sqrt((g.carX - destX)**2 + (g.carY - destY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, p = g.navigate(g.heading, g.carX, g.carY, destX, destY)
            sendDirs(dirs)
            time.sleep(1.0)

        print("Picked up — resuming, navigating to drop off...")
        for _ in range(3):
            stopped(True)
            time.sleep(0.1)

        print("Near dropoff — waiting for inPosition confirmation...")
        if not wait_for_fare_status(fareID, 'inPosition'):
            resp = duckAPI.getMatchInfo()
            continue

        print("In position — waiting for dropoff completion...")
        if not wait_for_fare_status(fareID, 'completed'):
            resp = duckAPI.getMatchInfo()
            continue

        print("Fare completed!")
        for _ in range(3):
            stopped(False)
            time.sleep(0.1)

        resp = duckAPI.getMatchInfo()
    close()

if __name__ == "__main__":
    main()