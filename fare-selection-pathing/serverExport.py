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
    if resp is None:
        print("[ZMQ] Error: Could not get match info. Exiting.")
        return

    while resp.get('inMatch') and resp.get('timeRemain', 0) > 0:
        # stopped(False)
        print("Getting best fare...")
        while True:
            try:
                best_fare_info = g.getBestFare()
                if best_fare_info is None:
                    print("[ZMQ] No fares available, retrying...")
                    time.sleep(2.0)
                    continue
                
                fareID, info = best_fare_info
                srcX, srcY, destX, destY, score, p1, p2, points1, points2 = info
                if duckAPI.claimFare(fareID):
                    print(f"Claimed best fare: {fareID}")
                    break
                else:
                    print(f"Failed to claim fare {fareID}, retrying...")
            except Exception as e:
                print(f"[ZMQ] Error in fare selection loop: {e}")
            
            time.sleep(1.0)  # Rate limit the search if no fare is claimed

        sendDirs(p1)
        print("Navigating to pickup...")
        g.updatePosition()
        while math.sqrt((g.carX - srcX)**2 + (g.carY - srcY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, p = g.navigate(g.heading, g.carX, g.carY, srcX, srcY)
            sendDirs(dirs)
            time.sleep(0.2)

        # print("Picked up — resuming, navigating to drop off...")
        # for _ in range(3):
        #     stopped(True)
        #     time.sleep(0.05)

        print("Near pickup — waiting for inPosition confirmation...")
        if not wait_for_fare_status(fareID, 'inPosition'):
            resp = duckAPI.getMatchInfo()
            if resp is None: break
            continue

        print("In position — waiting for pickup confirmation...")
        if not wait_for_fare_status(fareID, 'pickedUp'):
            resp = duckAPI.getMatchInfo()
            if resp is None: break
            continue

        print("Picked up — resuming, navigating to drop off...")
        for _ in range(3):
            stopped(False)
            time.sleep(0.05)

        sendDirs(p2)
        g.updatePosition()
        while math.sqrt((g.carX - destX)**2 + (g.carY - destY)**2) > 15:
            g.updatePosition()
            dirs, dist, h, p = g.navigate(g.heading, g.carX, g.carY, destX, destY)
            sendDirs(dirs)
            time.sleep(0.2)

        print("Picked up — resuming, navigating to drop off...")
        for _ in range(3):
            stopped(True)
            time.sleep(0.05)

        print("Near dropoff — waiting for inPosition confirmation...")
        if not wait_for_fare_status(fareID, 'inPosition'):
            resp = duckAPI.getMatchInfo()
            if resp is None: break
            continue

        print("In position — waiting for dropoff completion...")
        if not wait_for_fare_status(fareID, 'completed'):
            resp = duckAPI.getMatchInfo()
            if resp is None: break
            continue

        print("Fare completed!")
        for _ in range(3):
            stopped(False)
            time.sleep(0.05)

        resp = duckAPI.getMatchInfo()
        if resp is None: break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ZMQ] Interrupt received, shutting down...")
    finally:
        close()