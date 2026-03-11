#!/usr/bin/env python3
"""
Mock Perception Sender for Testing Control System

Run this script to simulate camera trajectory data without the actual track.
The control system (main.py) should be running in a separate terminal.

Usage:
    python test_perception_mock.py

Commands:
    straight  - Send CTE=0 (perfectly centered)
    left      - Send positive CTE (lane is to the right, steer right)
    right     - Send negative CTE (lane is to the left, steer left)
    curve_l   - Simulate approaching a left curve
    curve_r   - Simulate approaching a right curve
    sweep     - Continuously sweep CTE left-to-right
    custom X  - Send custom CTE in cm (e.g., "custom 5" or "custom -3")
    stop      - Stop sending data
    quit/q    - Exit
"""

import zmq
import time
import threading
import sys

# Connect to the control system's SUB socket (port 5556)
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.connect("tcp://127.0.0.1:5556")
time.sleep(0.2)  # Let connection establish

# Sending state
sending = False
send_thread = None
current_trajectory = None


def meters_to_csv(values_m):
    """Convert list of meter values to CSV string."""
    return ','.join(str(v) for v in values_m)


def make_trajectory(cte_cm_list, distance_cm_list):
    """Create trajectory message from cm values (converts to meters internally)."""
    cte_m = [c / 100.0 for c in cte_cm_list]
    dist_m = [d / 100.0 for d in distance_cm_list]
    return {
        "topic": "TRAJECTORY",
        "cte": meters_to_csv(cte_m),
        "distance": meters_to_csv(dist_m),
        "timestamp": time.time()
    }


# Standard distance points (near to far, in cm)
# These simulate the 10 lookahead points from BEV
DISTANCES_CM = [2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 18.0, 20.0]


def trajectory_straight():
    """Perfectly centered - CTE = 0 at all distances."""
    cte = [0.0] * 10
    return make_trajectory(cte, DISTANCES_CM)


def trajectory_offset_left(offset_cm=3.0):
    """Lane is to the RIGHT of car center (positive CTE) → car should steer RIGHT."""
    cte = [offset_cm] * 10
    return make_trajectory(cte, DISTANCES_CM)


def trajectory_offset_right(offset_cm=3.0):
    """Lane is to the LEFT of car center (negative CTE) → car should steer LEFT."""
    cte = [-offset_cm] * 10
    return make_trajectory(cte, DISTANCES_CM)


def trajectory_curve_left():
    """Approaching a left curve - CTE increases (lane curves right then left)."""
    # Near points: lane slightly right, far points: lane curves left
    cte = [2.0, 1.5, 1.0, 0.5, 0.0, -0.5, -1.0, -2.0, -3.0, -4.0]
    return make_trajectory(cte, DISTANCES_CM)


def trajectory_curve_right():
    """Approaching a right curve - CTE decreases (lane curves left then right)."""
    cte = [-2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 2.0, 3.0, 4.0]
    return make_trajectory(cte, DISTANCES_CM)


def trajectory_custom(cte_cm):
    """Uniform CTE at all distances."""
    cte = [cte_cm] * 10
    return make_trajectory(cte, DISTANCES_CM)


def send_loop():
    """Continuously send current trajectory at ~20Hz."""
    global sending, current_trajectory
    while sending:
        if current_trajectory:
            # Update timestamp each send
            current_trajectory["timestamp"] = time.time()
            pub_socket.send_json(current_trajectory)
        time.sleep(0.05)  # 20Hz


def start_sending(trajectory):
    """Start continuously sending a trajectory."""
    global sending, send_thread, current_trajectory
    current_trajectory = trajectory
    if not sending:
        sending = True
        send_thread = threading.Thread(target=send_loop, daemon=True)
        send_thread.start()
    print(f"  Sending: CTE={trajectory['cte'][:30]}...")


def stop_sending():
    """Stop sending trajectory data."""
    global sending
    sending = False
    print("  Stopped sending.")


def sweep_mode():
    """Sweep CTE from -5 to +5 repeatedly."""
    global sending, current_trajectory
    print("  Sweep mode: CTE will oscillate -5cm to +5cm. Press Enter to stop.")
    sending = True
    
    def sweep_loop():
        global sending
        cte_val = -5.0
        direction = 0.5
        while sending:
            current = trajectory_custom(cte_val)
            current["timestamp"] = time.time()
            pub_socket.send_json(current)
            print(f"\r  CTE: {cte_val:+.1f} cm", end="", flush=True)
            cte_val += direction
            if cte_val >= 5.0 or cte_val <= -5.0:
                direction *= -1
            time.sleep(0.1)
        print()
    
    thread = threading.Thread(target=sweep_loop, daemon=True)
    thread.start()
    input()  # Wait for Enter
    sending = False
    time.sleep(0.2)


def print_help():
    print("""
Commands:
  straight  - CTE=0 (centered)
  left      - Positive CTE (steer right to correct)
  right     - Negative CTE (steer left to correct)  
  curve_l   - Left curve trajectory
  curve_r   - Right curve trajectory
  sweep     - Oscillate CTE -5 to +5
  custom X  - Set CTE to X cm (e.g., "custom 5")
  stop      - Stop sending
  quit/q    - Exit
""")


def main():
    print("=" * 50)
    print("Mock Perception Sender")
    print("=" * 50)
    print("Make sure main.py is running in another terminal.")
    print("This sends TRAJECTORY messages to port 5556.")
    print_help()
    
    while True:
        try:
            cmd = input("\n> ").strip().lower()
            
            if cmd in ("quit", "q", "exit"):
                stop_sending()
                break
            elif cmd == "straight":
                start_sending(trajectory_straight())
            elif cmd == "left":
                start_sending(trajectory_offset_left(3.0))
            elif cmd == "right":
                start_sending(trajectory_offset_right(3.0))
            elif cmd == "curve_l":
                start_sending(trajectory_curve_left())
            elif cmd == "curve_r":
                start_sending(trajectory_curve_right())
            elif cmd == "sweep":
                sweep_mode()
            elif cmd.startswith("custom"):
                parts = cmd.split()
                if len(parts) >= 2:
                    try:
                        cte_val = float(parts[1])
                        start_sending(trajectory_custom(cte_val))
                    except ValueError:
                        print("  Invalid number. Usage: custom 5")
                else:
                    print("  Usage: custom <cte_cm>  (e.g., custom 5)")
            elif cmd == "stop":
                stop_sending()
            elif cmd == "help":
                print_help()
            elif cmd == "":
                pass  # Ignore empty input
            else:
                print(f"  Unknown command: {cmd}")
                print_help()
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
    
    pub_socket.close()
    context.term()
    print("Done.")


if __name__ == "__main__":
    main()
