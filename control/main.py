import csv
import os
import threading
import time
from picarx import Picarx
from pid_controller import PIDController
from line_sensor import LineSensor

# --- CONFIG ---
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
PASS_TIME = 0.5

# Centralized timing/tuning constants
LOST_LINE_TIMEOUT = 2.0

TURN_BLIND_TIME = 0.5
TURN_SCAN_TIMEOUT = 2.0
TURN_SCAN_INTERVAL = 0.01
TURN_RECOVERY_PWM = 12
TURN_STABILIZE_TIME = 0.1

STOP_HOLD_TIME = 2.0
STOP_CLEAR_TIME = 0.5

SPEED_RAMP_RATE = 2.0
SPEED_DROP_GAIN = 0.4

MIN_DRIVE_SPEED = 5
MAX_STEER_CMD = 25

class RobotState:
    STRAIGHT = "ST"
    APPROACH_STOP = "STOP"
    LEFT_1 = "L1"
    LEFT_2 = "L2"
    RIGHT = "R"
    CALIBRATE = "CAL"
    IDLE = "IDLE"

# A list of states to execute in order.
# "None" implies driving straight until the next event.
# Example mission: Straight -> Left at the 1st cross -> Straight -> Right at the next cross -> Stop
MISSION_QUEUE = [
    RobotState.STRAIGHT,
    RobotState.LEFT_1,
    RobotState.STRAIGHT,
    RobotState.RIGHT,
    RobotState.APPROACH_STOP
]

stop_flag = False
current_state = RobotState.STRAIGHT
crossings_seen = 0
bias_mode = "c"
current_motor_speed = 0

def update_mission_state():
    """Auto-advances state when a maneuver is completed"""
    global current_state, MISSION_QUEUE
    if len(MISSION_QUEUE) > 0:
        current_state = MISSION_QUEUE.pop(0)
        print(f"MISSION UPDATE: Switched to {current_state}")
    else:
        print("MISSION COMPLETE")
        current_state = RobotState.IDLE

def set_speed_smooth(target, px, ramp_rate=1.0):
    global current_motor_speed
    # Move the current speed towards the target speed by 'ramp_rate'
    if current_motor_speed < target:
        current_motor_speed = min(target, current_motor_speed + ramp_rate)
    elif current_motor_speed > target:
        current_motor_speed = max(target, current_motor_speed - ramp_rate)

    px.forward(current_motor_speed)

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
        elif cmd == "idle":
            current_state = RobotState.IDLE
            print("State: IDLE (Stop robot)")
        elif cmd in ("bc", "bl", "br"):
            global bias_mode
            bias_mode = cmd[1:]
            print(f"Bias mode: {bias_mode}")


def execute_turn(px, eyes, direction, pid):
    """Turns until the line is actually seen, rather than guessing the time."""
    global current_motor_speed, current_state
    print(f"Executing Closed-Loop {direction} turn...")

    # 1. Blind Phase: Turn hard to clear the current intersection
    steer = -MAX_STEER_CMD if direction == "right" else MAX_STEER_CMD
    px.set_dir_servo_angle(steer)
    px.forward(TURN_PWM)
    current_motor_speed = TURN_PWM
    time.sleep(TURN_BLIND_TIME)  # Short blind duration just to leave the current line

    # 2. Scanning Phase: try an intended direction first
    line_found = False
    start_scan = time.time()
    while (time.time() - start_scan) < TURN_SCAN_TIMEOUT:
        raw = eyes.get_raw()
        # Check if the Center sensor sees the line (signal strength > threshold)
        if eyes.color_signal(raw[1], 1) > eyes.LOGIC_DETECT:
            print("Line Re-acquired!")
            line_found = True
            break
        time.sleep(TURN_SCAN_INTERVAL)

    # 3. Fallback scanning phase: scan an opposite direction slowly
    if not line_found:
        print("Turn scan timeout. Trying opposite-direction recovery scan...")
        recovery_steer = MAX_STEER_CMD if direction == "right" else -MAX_STEER_CMD
        px.set_dir_servo_angle(recovery_steer)
        px.forward(TURN_RECOVERY_PWM)
        current_motor_speed = TURN_RECOVERY_PWM

        start_scan = time.time()
        while (time.time() - start_scan) < TURN_SCAN_TIMEOUT:
            raw = eyes.get_raw()
            if eyes.color_signal(raw[1], 1) > eyes.LOGIC_DETECT:
                print("Line Re-acquired during recovery scan!")
                line_found = True
                break
            time.sleep(TURN_SCAN_INTERVAL)

    if not line_found:
        print("Turn recovery failed. Entering IDLE fail-safe state.")
        px.stop()
        current_motor_speed = 0
        pid.reset()
        current_state = RobotState.IDLE
        return False

    # 4. Stabilization Phase
    px.set_dir_servo_angle(STRAIGHT_ANGLE)  # Snap wheels straight
    px.stop()  # Briefly stop momentum
    current_motor_speed = 0
    time.sleep(TURN_STABILIZE_TIME)
    pid.reset()  # Clear PID errors
    return True

def ignore_intersection(px, speed):
    """Drive straight briefly to skip a crossing line."""
    global current_motor_speed
    px.set_dir_servo_angle(STRAIGHT_ANGLE)
    px.forward(speed)
    current_motor_speed = speed
    time.sleep(PASS_TIME)

def main():
    global stop_flag, current_state, crossings_seen, current_motor_speed

    px = Picarx()
    pid = PIDController(KP, KI, KD, min_out=-MAX_STEER, max_out=MAX_STEER)
    eyes = LineSensor(px, OFFSETS)

    print("Place robot on the line.")
    print("Ensure it has 20cm of space around it.")
    input("Press Enter to Start Wiggle Calibration...")

    eyes.calibrate(straight_angle=STRAIGHT_ANGLE)

    error_buffer = [0.0] * ERROR_BUFFER_LEN
    history = []
    start_time = time.time()

    # Initial Mission State
    update_mission_state()

    # Initialize failsafe timer
    last_valid_line_time = time.time()
    last_pid_time = time.time()

    listener = threading.Thread(target=key_listener, daemon=True)
    listener.start()

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

            if current_state == RobotState.IDLE:
                px.stop()
                current_motor_speed = 0
                time.sleep(0.5)
                continue

            pattern = eyes.analyze_pattern(raw)
            error, stop_detected, base_speed = eyes.compute_error(raw, bias_mode=bias_mode)

            # Inside the main loop
            if not eyes.last_line_seen:
                if (time.time() - last_valid_line_time) > LOST_LINE_TIMEOUT:
                    print("FAILSAFE: Line lost for > 2s. Emergency Stop.")
                    stop_flag = True
                    break
            else:
                last_valid_line_time = time.time()

            # Lower speed when approaching a possible stop
            if current_state == RobotState.APPROACH_STOP:
                base_speed = APPROACH_SPEED

            # 1) White stop line handling
            if current_state == RobotState.APPROACH_STOP and pattern == "STOP_WHITE":
                px.stop()
                current_motor_speed = 0  # Reset smooth speed tracker
                time.sleep(STOP_HOLD_TIME)
                print("Clearing line...")
                px.forward(base_speed)
                current_motor_speed = base_speed
                time.sleep(STOP_CLEAR_TIME)
                pid.reset()
                update_mission_state()
                continue

            # 2) Intersection handling (green crossings)
            if pattern == "CROSS_GREEN":
                if current_state == RobotState.LEFT_1:
                    print("Left turn on first crossing")
                    if not execute_turn(px, eyes, "left", pid):
                        continue
                    pid.reset()
                    update_mission_state()
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
                    if not execute_turn(px, eyes, "left", pid):
                        continue
                    pid.reset()
                    update_mission_state()
                    crossings_seen = 0
                    continue

                if current_state == RobotState.RIGHT:
                    print("Right turn on crossing")
                    if not execute_turn(px, eyes, "right", pid):
                        continue
                    pid.reset()
                    update_mission_state()
                    crossings_seen = 0
                    continue

                if current_state == RobotState.STRAIGHT:
                    ignore_intersection(px, base_speed)
                    pid.reset()
                    # Advance mission if we were just driving straight and reached an intersection
                    # that we are ignoring.
                    update_mission_state()
                    continue

            # 3) PID line following
            error_buffer.pop(0)
            error_buffer.append(error)
            smooth_error = sum(error_buffer) / len(error_buffer)

            # Calculate dt between PID updates
            current_time = time.time()
            dt = current_time - last_pid_time
            last_pid_time = current_time
            
            steering = pid.update(smooth_error * POLARITY, dt=dt)
            # Apply straight angle offset
            steering_with_offset = steering + STRAIGHT_ANGLE
            steering_with_offset = max(-MAX_STEER_CMD, min(MAX_STEER_CMD, steering_with_offset))

            speed_drop = abs(steering) * SPEED_DROP_GAIN
            current_speed = max(base_speed - speed_drop, MIN_DRIVE_SPEED)

            px.set_dir_servo_angle(steering_with_offset)
            set_speed_smooth(current_speed, px, ramp_rate=SPEED_RAMP_RATE)

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