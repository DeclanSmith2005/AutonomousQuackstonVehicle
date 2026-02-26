"""
Minimal State Listener - Server Side.

This script acts as the "Server" that receives mission state updates
from the robot (main.py). It no longer touches the hardware.
"""
import zmq
import time

def main():
    context = zmq.Context()
    
    # SUB Socket: Listens to State/Telemetry from main.py (Port 5555)
    sub_socket = context.socket(zmq.SUB)
    # If running on the same Pi, use 127.0.0.1. 
    # If running on a laptop, use the Pi's IP.
    sub_socket.connect("tcp://127.0.0.1:5555")
    sub_socket.subscribe("") # Subscribe to all topics
    
    print("Mission State Server Listening on port 5555...")
    print("Waiting for updates from main.py...")
    
    try:
        while True:
            try:
                msg = sub_socket.recv_json(flags=zmq.NOBLOCK)
                topic = msg.get("topic")
                
                if topic == "MISSION_STATE":
                    print(f"[{time.strftime('%H:%M:%S')}] STATE: {msg.get('state')} | Queue: {msg.get('queue')}")
                
                elif topic == "TELEMETRY":
                    # Only print telemetry occasionally to avoid flooding
                    if int(time.time() * 10) % 20 == 0:
                        print(f"  > Telemetry: Speed={msg.get('speed'):.1f} Error={msg.get('error'):.1f}")
                
            except zmq.Again:
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nStopping Server...")
    finally:
        sub_socket.close()
        context.term()

if __name__ == "__main__":
    main()
