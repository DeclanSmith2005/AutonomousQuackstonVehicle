import csv
import os
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

class RobotState:
    STRAIGHT = "ST"
    APPROACH_STOP = "STOP"
    LEFT_1 = "L1"
    LEFT_2 = "L2"
    RIGHT = "R"
    CALIBRATE = "CAL"
    IDLE = "IDLE"

# A list of states to execute in order.
# "None" implies drive straight until next event.
# Example mission: Straight -> Left at 1st cross -> Straight -> Right at next cross -> Stop
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
    global current_motor_speed
    print(f"Executing Closed-Loop {direction} turn...")

    # 1. Blind Phase: Turn hard to clear the current intersection
    steer = -25 if direction == "right" else 25
    px.set_dir_servo_angle(steer)
    px.forward(TURN_PWM)
    current_motor_speed = TURN_PWM
    time.sleep(0.3)  # Short blind duration just to leave the current line

    # 2. Scanning Phase: Keep turning until Middle Sensor sees black
    # Timeout safety: If we don't see a line in 2 seconds, stop to prevent spinning forever
    start_scan = time.time()
    while (time.time() - start_scan) < 2.0:
        raw = eyes.get_raw()
        # Check if the Center sensor sees the line (signal strength > threshold)
        if eyes.color_signal(raw[1], eyes.offsets[1]) > eyes.LOGIC_DETECT:
            print("Line Re-acquired!")
            break
        time.sleep(0.01)

    # 3. Stabilization Phase
    px.set_dir_servo_angle(STRAIGHT_ANGLE)  # Snap wheels straight
    px.stop()  # Briefly stop momentum
    current_motor_speed = 0
    time.sleep(0.1)
    pid.reset()  # Clear PID errors

def ignore_intersection(px, speed):
    """Drive straight briefly to skip a crossing line."""
    global current_motor_speed
    px.set_dir_servo_angle(STRAIGHT_ANGLE)
    px.forward(speed)
    current_motor_speed = speed
    time.sleep(PASS_TIME)

def main():
    global stop_flag, current_state, crossings_seen

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

            # Inside main loop
            if not eyes.last_line_seen:
                if (time.time() - last_valid_line_time) > 2.0:
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
                time.sleep(2.0)
                print("Clearing line...")
                px.forward(base_speed)
                current_motor_speed = base_speed
                time.sleep(0.5)
                pid.reset()
                update_mission_state()
                continue

            # 2) Intersection handling (green crossings)
            if pattern == "CROSS_GREEN":
                if current_state == RobotState.LEFT_1:
                    print("Left turn on first crossing")
                    execute_turn(px, eyes, "left", pid)
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
                    execute_turn(px, eyes, "left", pid)
                    pid.reset()
                    update_mission_state()
                    crossings_seen = 0
                    continue

                if current_state == RobotState.RIGHT:
                    print("Right turn on crossing")
                    execute_turn(px, eyes, "right", pid)
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

            # Calculate actual dt
            current_time = time.time()
            dt = current_time - loop_start
            
            steering = pid.update(smooth_error * POLARITY, dt=dt)
            # Apply straight angle offset
            steering_with_offset = steering + STRAIGHT_ANGLE
            steering_with_offset = max(-25, min(25, steering_with_offset))

            speed_drop = abs(steering) * 0.4
            current_speed = max(base_speed - speed_drop, 5)

            px.set_dir_servo_angle(steering_with_offset)
            set_speed_smooth(current_speed, px, ramp_rate=2.0)

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