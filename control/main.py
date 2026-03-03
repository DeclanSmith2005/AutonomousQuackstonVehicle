import csv
import os
import threading
import time
from picarx import Picarx

import config
from pid_controller import PIDController
from line_sensor import LineSensor
from mission_manager import MissionManager, RobotState

# --- GLOBALS ---
stop_flag = False
current_motor_speed = 0
force_line_lost = False
force_intersection = False
run_calibration_flag = False

# Default calibration values (updated from calibration session)
DEFAULT_CAL_MIN = [50, 50, 50]   # Floor values (off-line)
DEFAULT_CAL_MAX = [1455, 1315, 1383]  # Peak values (on-line)

# def set_speed_smooth(px, target_speed, steer, ramp_rate=1.0):
#     """Gradually adjust speed towards target while steering."""
#     global current_motor_speed
#     if current_motor_speed < target_speed:
#         current_motor_speed = min(target_speed, current_motor_speed + ramp_rate)
#     elif current_motor_speed > target_speed:
#         current_motor_speed = max(target_speed, current_motor_speed - ramp_rate)
#
#     px.forward(current_motor_speed)
#     px.set_dir_servo_angle(steer)

def run_wiggle_calibration(px, eyes):
    """Execute wiggle calibration directly on hardware."""
    print("Starting wiggle calibration...")
    cal_min = [4095, 4095, 4095]
    cal_max = [0, 0, 0]
    
    # Calibration parameters
    CAL_TURN_ANGLE = 25
    STRAIGHT_ANGLE = 0
    CAL_TURN_SPEED = 10
    CAL_DURATION = 0.8
    CAL_INTERVAL = 0.05

    def collect_samples(duration_s):
        start = time.time()
        while (time.time() - start) < duration_s:
            sample = px.get_grayscale_data()
            for i in range(3):
                cal_min[i] = min(cal_min[i], sample[i])
                cal_max[i] = max(cal_max[i], sample[i])
            time.sleep(CAL_INTERVAL)

    # Wiggle Left
    px.set_dir_servo_angle(CAL_TURN_ANGLE)
    px.forward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)
    px.backward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)

    # Wiggle Right
    px.set_dir_servo_angle(-CAL_TURN_ANGLE)
    px.forward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)
    px.backward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)

    px.stop()
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)
    time.sleep(0.2)

    print(f"Calibration Complete: min={cal_min}, max={cal_max}")
    eyes.apply_calibration(cal_min, cal_max)
    return True


def key_listener(mission):
    """
    Interactive keyboard control for mission management and failure testing.
    s: stop
    st/a/l1/l2/r/idle/cal: manually jump to state
    n: next mission stage
    reset: reset mission
    fl: toggle forced line lost (simulates sensor failure)
    fi: trigger forced intersection detection (simulates crossing)
    wiggle: run wiggle calibration
    """
    global stop_flag, force_line_lost, force_intersection, run_calibration_flag
    print("Keyboard listener active.")
    print("Commands: s=stop, st=straight, a=approach_stop, l1/l2=left, r=right, idle=idle, cal=calibrate")
    print("          n=next, reset=reset, fl=force line lost, fi=force intersection")
    print("          wiggle=run wiggle calibration")
    
    while not stop_flag:
        try:
            cmd = input().strip().lower()
            if cmd == "s":
                stop_flag = True
            elif cmd == "st":
                mission.current_state = RobotState.STRAIGHT
                mission.crossings_seen = 0
                print("Manual State: STRAIGHT")
            elif cmd == "a":
                mission.current_state = RobotState.APPROACH_STOP
                mission.crossings_seen = 0
                print("Manual State: APPROACH STOP")
            elif cmd == "l1":
                mission.current_state = RobotState.LEFT_1
                mission.crossings_seen = 0
                print("Manual State: LEFT_1")
            elif cmd == "l2":
                mission.current_state = RobotState.LEFT_2
                mission.crossings_seen = 0
                print("Manual State: LEFT_2")
            elif cmd == "r":
                mission.current_state = RobotState.RIGHT
                mission.crossings_seen = 0
                print("Manual State: RIGHT")
            elif cmd == "cal":
                mission.current_state = RobotState.CALIBRATE
                print("Manual State: CALIBRATE")
            elif cmd == "idle":
                mission.current_state = RobotState.IDLE
                print("Manual State: IDLE")
            elif cmd in ("", "n", "next"):
                mission.request_step()
                print("Mission step requested.")
            elif cmd in ("reset", "mr"):
                mission.reset_mission()
            elif cmd == "wiggle":
                run_calibration_flag = True
                print("Wiggle calibration requested...")
        except EOFError:
            break

def execute_turn(px, eyes, direction, pid, mission):
    """Wait for full-width line, then turn until line is reacquired."""
    global current_motor_speed

    print(f"Executing {direction} turn...")

    # 1) Gate turn start on full-width line
    # Stop before turning
    current_motor_speed = 0
    px.forward(current_motor_speed)
    time.sleep(config.TURN_STOP_HOLD_TIME)

    # 2) Manual turn
    steer = -config.MAX_STEER if direction == "right" else config.MAX_STEER
    px.forward(config.TURN_PWM)
    px.set_dir_servo_angle(steer)
    current_motor_speed = config.TURN_PWM

    #entry_start = time.time()
    
    # while (time.time() - entry_start) < config.TURN_ENTRY_TIMEOUT:
    #     raw = px.get_grayscale_data()
    #     full_line_seen = all(eyes.color_signal(raw[i], i) > eyes.LOGIC_DETECT for i in range(3))
    #     if full_line_seen:
    #         print("Full-width line detected.")
    #         break
    #     time.sleep(config.TURN_SCAN_INTERVAL)
    #
    # if not full_line_seen:
    #     print("Turn aborted: No marker detected.")
    #     px.stop()
    #     current_motor_speed = 0
    #     pid.reset()
    #     mission.current_state = RobotState.IDLE
    #     return False

    line_found = False
    start_scan = time.time()
    while (time.time() - start_scan) < config.TURN_SCAN_TIMEOUT:
        raw = px.get_grayscale_data()
        pattern = eyes.analyze_pattern(raw)
        center_on_line = eyes.color_signal(raw[1], 1) > eyes.LOGIC_DETECT
        if center_on_line and pattern == "LINE":
            print("Line re-acquired.")
            line_found = True
            break
        time.sleep(config.TURN_SCAN_INTERVAL)

    if not line_found:
        print("Turn failed to re-acquire line.")
        px.stop()
        current_motor_speed = 0
        pid.reset()
        mission.current_state = RobotState.IDLE
        return False

    # 3) Stabilize
    pid.reset()
    return True

def ignore_intersection(px, speed):
    global current_motor_speed
    px.forward(speed)
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)
    current_motor_speed = speed
    time.sleep(config.PASS_TIME)

def stop_at_line(px, base_speed):
    global current_motor_speed
    px.stop()
    current_motor_speed = 0
    time.sleep(config.STOP_HOLD_TIME)
    # Clear the line
    px.forward(base_speed)
    time.sleep(config.STOP_CLEAR_TIME)

def main():
    global stop_flag, current_motor_speed, force_line_lost, force_intersection, run_calibration_flag

    # --- SENSORS & ACTUATORS ---
    px = Picarx()
    eyes = LineSensor(config.OFFSETS)
    pid = PIDController(config.KP, config.KI, config.KD, min_out=-config.MAX_STEER, max_out=config.MAX_STEER)

    # --- MISSION ---
    # Default mission from main_old.py
    initial_mission = [
        RobotState.RIGHT,
        RobotState.STRAIGHT,
        RobotState.LEFT_1,
        RobotState.STRAIGHT,
        RobotState.APPROACH_STOP
    ]
    mission = MissionManager(initial_mission)

    print("="*40)
    print("PICARX DIRECT CONTROL STARTED")
    print("="*40)
    
    # Apply default calibration values
    print("Using default calibration values...")
    eyes.apply_calibration(DEFAULT_CAL_MIN, DEFAULT_CAL_MAX)
    print("Type 'wiggle' to run live calibration if needed.")

    # Start keyboard listener
    threading.Thread(target=key_listener, args=(mission,), daemon=True).start()

    error_buffer = [0.0] * config.ERROR_BUFFER_LEN
    history = []
    start_time = time.time()
    last_valid_line_time = time.time()
    last_pid_time = time.time()

    try:
        while not stop_flag:
            loop_start = time.time()

            # Check for calibration request
            if run_calibration_flag:
                run_calibration_flag = False
                run_wiggle_calibration(px, eyes)
                continue

            # 1) Get Hardware Data
            raw = px.get_grayscale_data()
            
            # Distance check (Obstacle avoidance failsafe)
            #current_distance = None
            current_distance = px.ultrasonic.read()
            if 0 < current_distance < config.OBSTACLE_THRESHOLD:
                print(f"!!! EMERGENCY STOP: Obstacle detected at {current_distance:.1f}cm !!!")
                stop_flag = True
                break


            # 2) Fail-safe & Simulation logic
            if force_line_lost:
                # Simulate no line detected
                raw = [4095, 4095, 4095] 

            pattern = eyes.analyze_pattern(raw)
            error, stop_detected, base_speed = eyes.compute_error(raw)

            # Manual intersection trigger
            #if force_intersection:
            #   pattern = "CROSS"
            #    force_intersection = False

            # 3) Handle Mission Stages
            if mission.check_step_requested():
                print(f"Advancing mission. New state: {mission.current_state}")
                pid.reset()

            # 4) State Machine Failsafes
            if mission.current_state == RobotState.IDLE:
                px.stop()
                current_motor_speed = 0
                time.sleep(0.5)
                continue

            if mission.current_state == RobotState.CALIBRATE:
                print(f"RAW: {raw} | PATTERN: {pattern}")
                time.sleep(0.5)
                continue

            if (mission.current_state == RobotState.APPROACH_STOP or mission.current_state == RobotState.LEFT_1
                    or mission.current_state == RobotState.LEFT_2 or mission.current_state == RobotState.RIGHT):
                print("Approaching STOP LINE...")
                px.forward(config.TURN_ENTRY_SPEED)
                current_motor_speed = config.TURN_ENTRY_SPEED

            # Line Lost Failsafe
            if not eyes.last_line_seen:
                if (time.time() - last_valid_line_time) > config.LOST_LINE_TIMEOUT:
                    print(f"!!! FAILSAFE: Line lost for > {config.LOST_LINE_TIMEOUT}s !!!")
                    stop_flag = True
                    break
            else:
                last_valid_line_time = time.time()

            if pattern == "CROSS":
                if mission.current_state == RobotState.STRAIGHT:
                    print("Ignoring intersection (STRAIGHT mode).")
                    ignore_intersection(px, base_speed)
                    continue
                elif mission.current_state == RobotState.APPROACH_STOP:
                    print("STOP LINE reached.")
                    stop_at_line(px, base_speed)
                    continue
                elif mission.current_state == RobotState.LEFT_1:
                    if execute_turn(px, eyes, "left", pid, mission):
                        mission.advance_mission()
                    continue
                elif mission.current_state == RobotState.LEFT_2:
                    mission.crossings_seen += 1
                    if mission.crossings_seen >= 3: # +1 more to account for the stop line
                        if execute_turn(px, eyes, "left", pid, mission):
                            mission.advance_mission()
                    else:
                        print(f"Skipping intersection {mission.crossings_seen}/2")
                        ignore_intersection(px, base_speed)
                    continue
                elif mission.current_state == RobotState.RIGHT:
                    if execute_turn(px, eyes, "right", pid, mission):
                        mission.advance_mission()
                    continue


            # 6) PID CONTROL
            current_time = time.time()
            dt = current_time - last_pid_time
            last_pid_time = current_time

            error_buffer.append(error)
            error_buffer.pop(0)
            smooth_error = sum(error_buffer) / len(error_buffer)

            if abs(smooth_error) < config.DEADBAND:
                smooth_error = 0.0

            steering = pid.update(smooth_error * config.POLARITY, dt=dt)
            # steering_with_offset = steering + config.STRAIGHT_ANGLE
            steering = max(-config.MAX_STEER, min(config.MAX_STEER, steering))

            speed_drop = abs(steering) * config.SPEED_DROP_GAIN
            current_speed = max(base_speed - speed_drop, config.MIN_DRIVE_SPEED)

            # set_speed_smooth(px, current_speed, steering_with_offset, ramp_rate=config.SPEED_RAMP_RATE)
            px.forward(current_speed)
            px.set_dir_servo_angle(steering)

            # 7) LOGGING
            history.append((time.time() - start_time, mission.current_state, smooth_error, steering, current_speed))

            # 8) LOOP TIMING
            elapsed = time.time() - loop_start
            wait_time = config.LOOP_INTERVAL - elapsed
            if wait_time > 0:
                time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        px.stop()

        # Save Logs
        if history:
            os.makedirs("logs", exist_ok=True)
            log_name = f"logs/run_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            with open(log_name, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["time_s", "state", "error", "steer", "speed"])
                writer.writerows(history)
            print(f"Log saved to {log_name}")

if __name__ == "__main__":
    main()
