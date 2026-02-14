import csv
import os
import time
import threading
from picarx import Picarx
from pid_controller import PIDController
from line_sensor import LineSensor

# --- CONFIG (mirrors pid.py) ---
OFFSETS = [111, 95, 100]
KP, KI, KD = 0.35, 0.0, 0.05
MAX_STEER = 25
POLARITY = -1
LOOP_INTERVAL = 0.01
ERROR_BUFFER_LEN = 5

# Turn / approach tuning
APPROACH_SPEED = 10
TURN_PWM = 20
STRAIGHT_ANGLE = -13.9
TURN_TIME = 0.6
PASS_TIME = 0.4

class RobotState:
    STRAIGHT = "ST"
    APPROACH_STOP = "STOP"
    LEFT_1 = "L1"
    LEFT_2 = "L2"
    RIGHT = "R"
    CALIBRATE = "CAL"

stop_flag = False
current_state = RobotState.STRAIGHT
crossings_seen = 0
bias_mode = "c"

def key_listener():
    """Keyboard control for the state machine."""
    global stop_flag, current_state, crossings_seen
    while not stop_flag:
        cmd = input().strip().lower()
        if cmd == "s":
            stop_flag = True
        elif cmd == "st":
            current_state = RobotState.STRAIGHT
            crossings_seen = 0
            print("State: STRAIGHT (ignore crossings)")
        elif cmd == "a":
            current_state = RobotState.APPROACH_STOP
            crossings_seen = 0
            print("State: APPROACH STOP (slow & stop on white line)")
        elif cmd == "l1":
            current_state = RobotState.LEFT_1
            crossings_seen = 0
            print("State: LEFT TURN on first crossing")
        elif cmd == "l2":
            current_state = RobotState.LEFT_2
            crossings_seen = 0
            print("State: LEFT TURN on second crossing")
        elif cmd == "r":
            current_state = RobotState.RIGHT
            crossings_seen = 0
            print("State: RIGHT TURN on first crossing")
        elif cmd == "cal":
            current_state = RobotState.CALIBRATE
            print("State: CALIBRATE (Show sensor values)")
        elif cmd in ("bc", "bl", "br"):
            global bias_mode
            bias_mode = cmd[1:]
            print(f"Bias mode: {bias_mode}")


def execute_turn(px, direction):
    """Blind turn for 90-deg intersections where PID would fail."""
    steer = -25 if direction == "right" else 25
    px.stop()
    px.set_dir_servo_angle(steer)
    px.forward(TURN_PWM)
    time.sleep(TURN_TIME)
    px.set_dir_servo_angle(STRAIGHT_ANGLE)

def ignore_intersection(px, speed):
    """Drive straight briefly to skip a crossing line."""
    px.set_dir_servo_angle(STRAIGHT_ANGLE)
    px.forward(speed)
    time.sleep(PASS_TIME)

def main():
    global stop_flag, current_state, crossings_seen

    px = Picarx()
    pid = PIDController(KP, KI, KD, min_out=-MAX_STEER, max_out=MAX_STEER)
    eyes = LineSensor(px, OFFSETS)

    error_buffer = [0.0] * ERROR_BUFFER_LEN
    history = []
    start_time = time.time()

    threading.Thread(target=key_listener, daemon=True).start()

    try:
        while not stop_flag:
            loop_start = time.time()

            try:
                raw = eyes.get_raw()
            except Exception as e:
                print(f"Sensor error: {e}")
                time.sleep(LOOP_INTERVAL)
                continue

            if current_state == RobotState.CALIBRATE:
                print(f"RAW: {raw}")
                time.sleep(0.5)
                continue

            pattern = eyes.analyze_pattern(raw)
            error, stop_detected, base_speed = eyes.compute_error(raw, bias_mode=bias_mode)

            # Lower speed when approaching a possible stop
            if current_state == RobotState.APPROACH_STOP:
                base_speed = APPROACH_SPEED

            # 1) White stop line handling
            if current_state == RobotState.APPROACH_STOP and pattern == "STOP_WHITE":
                px.stop()
                time.sleep(2.0)
                print("Clearing line...")
                px.forward(base_speed)
                time.sleep(0.5)
                pid.reset()
                continue

            # 2) Intersection handling (green crossings)
            if pattern == "CROSS_GREEN":
                if current_state == RobotState.LEFT_1:
                    print("Left turn on first crossing")
                    execute_turn(px, "left")
                    pid.reset()
                    current_state = RobotState.STRAIGHT
                    crossings_seen = 0
                    continue

                if current_state == RobotState.LEFT_2:
                    crossings_seen += 1
                    if crossings_seen == 1:
                        print("Skipping first left crossing")
                        ignore_intersection(px, base_speed)
                        pid.reset()
                        continue
                    print("Left turn on second crossing")
                    execute_turn(px, "left")
                    pid.reset()
                    current_state = RobotState.STRAIGHT
                    crossings_seen = 0
                    continue

                if current_state == RobotState.RIGHT:
                    print("Right turn on crossing")
                    execute_turn(px, "right")
                    pid.reset()
                    current_state = RobotState.STRAIGHT
                    crossings_seen = 0
                    continue

                if current_state == RobotState.STRAIGHT:
                    ignore_intersection(px, base_speed)
                    pid.reset()
                    continue

            # 3) PID line following
            error_buffer.pop(0)
            error_buffer.append(error)
            smooth_error = sum(error_buffer) / len(error_buffer)

            # Calculate actual dt
            current_time = time.time()
            dt = current_time - loop_start
            
            steering = pid.update(smooth_error * POLARITY, dt=dt)
            steering = max(-25, min(25, steering))

            speed_drop = abs(steering) * 0.4
            current_speed = max(base_speed - speed_drop, 5)

            px.set_dir_servo_angle(steering)
            px.forward(current_speed)

            history.append((time.time() - start_time, smooth_error, steering, current_speed))

            elapsed = time.time() - loop_start
            wait_time = LOOP_INTERVAL - elapsed
            if wait_time > 0:
                time.sleep(wait_time)

    finally:
        px.stop()

        if history:
            os.makedirs("logs", exist_ok=True)
            log_name = f"logs/pid_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                with open(log_name, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["time_s", "error", "steering_angle", "speed"])
                    writer.writerows(history)
                print(f"Wrote log to {log_name}")
            except OSError as exc:
                print(f"Failed to write log: {exc}")


if __name__ == "__main__":
    main()