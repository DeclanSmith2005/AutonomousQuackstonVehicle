import csv
import os
import threading
import time
from picarx import Picarx

import config
from pid_controller import PIDController
from line_sensor import LineSensor
from mission_manager import MissionManager, RobotState
from server import ServerManager
from calibration import load_calibration, run_wiggle_calibration

# --- GLOBALS ---
stop_flag = False
current_motor_speed = 0
force_line_lost = False
force_intersection = False
run_calibration_flag = False
no_line_turn = False


# --- CAMERA-GUIDED TURN HELPERS (Pure Pursuit / Adaptive Lookahead) ---
def get_lookahead_cte(trajectory, target_distance):
    """
    Find the CTE at the desired lookahead distance using linear interpolation.
    
    This implements Pure Pursuit: always steer toward a point a fixed physical
    distance ahead, making turn behavior speed-invariant.
    
    Parameters
    ----------
    trajectory : list
        List of (distance_cm, cte_cm) tuples, sorted near to far.
    target_distance : float
        Lookahead distance in cm (e.g., 15.0).
    
    Returns
    -------
    float or None
        Interpolated CTE in cm at the lookahead distance, or None if invalid.
    """
    if not trajectory or len(trajectory) < 2:
        return None
    
    # Search for the two points that bracket the target distance
    for i in range(len(trajectory) - 1):
        d1, cte1 = trajectory[i]
        d2, cte2 = trajectory[i + 1]
        
        # If target distance falls between these two points, interpolate
        if d1 <= target_distance <= d2:
            if d2 - d1 > 0:  # Avoid division by zero
                ratio = (target_distance - d1) / (d2 - d1)
                return cte1 + ratio * (cte2 - cte1)
            else:
                return cte1
    
    # If target is closer than the nearest point, use nearest
    if target_distance < trajectory[0][0]:
        return trajectory[0][1]
    
    # If target is further than our vision, use the furthest point
    return trajectory[-1][1]


def scan_for_line_fallback(px, eyes, mission, pid):
    """Fallback: scan for line using grayscale after camera timeout."""
    global current_motor_speed
    
    print("Camera fallback: scanning with grayscale...")
    line_found = False
    start_scan = time.time()
    
    while (time.time() - start_scan) < config.TURN_SCAN_TIMEOUT:
        raw = px.get_grayscale_data()
        on_line = any(eyes.color_signal(raw[i], i) > eyes.LOGIC_DETECT for i in range(3))
        if on_line:
            print("Line re-acquired by grayscale.")
            line_found = True
            mission.current_state = RobotState.STRAIGHT
            px.forward(5)
            break
        time.sleep(config.TURN_SCAN_INTERVAL)
    
    if not line_found:
        print("Turn failed to re-acquire line.")
        px.stop()
        current_motor_speed = 0
        pid.reset()
        mission.current_state = RobotState.IDLE
        return False
    
    pid.reset()
    return True


def execute_turn_with_camera(px, eyes, direction, pid, mission, server):
    """Camera-guided turn using Pure Pursuit (adaptive lookahead).
    
    Uses a fixed lookahead distance to find the target point on the trajectory,
    making turn behavior speed-invariant. Steers until grayscale sensor
    re-acquires the line.
    """
    global current_motor_speed
    
    print(f"Executing camera-guided {direction} turn (lookahead={config.LOOKAHEAD_DISTANCE_CM}cm)...")
    
    # 1) Stop at intersection
    time.sleep(0.25)
    px.stop()
    current_motor_speed = 0
    time.sleep(config.TURN_STOP_HOLD_TIME)
    
    # 2) Initial rotation to point toward exit lane
    initial_steer = config.MAX_STEER if direction == "right" else -config.MAX_STEER
    px.set_dir_servo_angle(initial_steer)
    px.forward(config.TURN_PWM)
    current_motor_speed = config.TURN_PWM
    time.sleep(config.TURN_INITIAL_ROTATION_TIME)
    
    # 3) Camera-guided trajectory following with Pure Pursuit
    turn_start = time.time()
    
    while (time.time() - turn_start) < config.TURN_CAMERA_TIMEOUT:
        
        # Check grayscale — if line found, handoff to straight mode
        raw = px.get_grayscale_data()
        on_line = any(eyes.color_signal(raw[i], i) > eyes.LOGIC_DETECT for i in range(3))
        if on_line:
            print("Line re-acquired by grayscale — exiting turn")
            mission.current_state = RobotState.STRAIGHT
            pid.reset()
            px.forward(5)
            return True
        
        # Get camera trajectory
        trajectory_msg = server.receive_trajectory()

        if trajectory_msg is not None:
            trajectory_points, _distance_line = trajectory_msg
        else:
            trajectory_points = None

        if trajectory_points and len(trajectory_points) > 0:
            # Pure Pursuit: always target a point at fixed distance ahead
            cte_cm = get_lookahead_cte(trajectory_points, config.LOOKAHEAD_DISTANCE_CM)
            
            if cte_cm is not None:
                # P-controller acting on the lookahead point
                # Negative sign: positive CTE (lane to right) → steer right (negative angle)
                steering = -cte_cm * config.TRAJECTORY_KP
                steering = max(-config.MAX_STEER, min(config.MAX_STEER, steering))
                
                px.set_dir_servo_angle(steering)
                px.forward(config.TURN_PWM)
                
                # Debug output (throttled to ~2.5Hz)
                if int(time.time() * 5) % 2 == 0:
                    print(f"  Lookahead: CTE={cte_cm:.1f}cm @ {config.LOOKAHEAD_DISTANCE_CM}cm → Steer={steering:.1f}°")
        else:
            # No camera data — maintain initial steering direction
            px.set_dir_servo_angle(initial_steer)
            px.forward(config.TURN_PWM)
        
        time.sleep(0.05)  # ~20Hz camera loop
    
    # 4) Camera timeout — fall back to grayscale scan
    return scan_for_line_fallback(px, eyes, mission, pid)


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
    global stop_flag, force_line_lost, force_intersection, run_calibration_flag, no_line_turn
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
                no_line_turn = False
                print("Manual State: STRAIGHT")
            elif cmd == "a":
                mission.current_state = RobotState.APPROACH_STOP
                mission.crossings_seen = 0
                no_line_turn = False
                print("Manual State: APPROACH STOP")
            elif cmd == "l1":
                mission.current_state = RobotState.LEFT_1
                mission.crossings_seen = 0
                no_line_turn = False
                print("Manual State: LEFT_1")
            elif cmd == "l2":
                mission.current_state = RobotState.LEFT_2
                mission.crossings_seen = 0
                no_line_turn = False
                print("Manual State: LEFT_2")
            elif cmd == "r":
                mission.current_state = RobotState.RIGHT
                mission.crossings_seen = 0
                no_line_turn = False
                print("Manual State: RIGHT")
            elif cmd == "cal":
                mission.current_state = RobotState.CALIBRATE
                no_line_turn = False
                print("Manual State: CALIBRATE")
            elif cmd == "idle":
                mission.current_state = RobotState.IDLE
                no_line_turn = False
                print("Manual State: IDLE")
            elif cmd in ("", "n", "next"):
                mission.request_step()
                no_line_turn = False
                print("Mission step requested.")
            elif cmd in ("reset", "mr"):
                no_line_turn = False
                mission.reset_mission()
            elif cmd == "wiggle":
                run_calibration_flag = True
                print("Wiggle calibration requested...")
            elif cmd == "rnl":
                mission.current_state = RobotState.RIGHT
                mission.crossings_seen = 0
                no_line_turn = True
                print("Manual State: RIGHT_NO_LINE")
            elif cmd == "lnl_1":
                mission.current_state = RobotState.LEFT_1
                mission.crossings_seen = 0
                no_line_turn = True
                print("Manual State: LEFT_1_NO_LINE")
            elif cmd == "lnl_2":
                mission.current_state = RobotState.LEFT_2
                mission.crossings_seen = 0
                no_line_turn = True
                print("Manual State: LEFT_2_NO_LINE")

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
    steer = config.MAX_STEER if direction == "right" else -config.MAX_STEER
    px.forward(config.TURN_PWM)
    px.set_dir_servo_angle(steer)
    current_motor_speed = config.TURN_PWM
    time.sleep(1.5) 

    line_found = False
    start_scan = time.time()
    while (time.time() - start_scan) < config.TURN_SCAN_TIMEOUT:
        raw = px.get_grayscale_data()
        on_line = eyes.color_signal(raw[0], 0) > eyes.LOGIC_DETECT or eyes.color_signal(raw[1], 1) > eyes.LOGIC_DETECT or eyes.color_signal(raw[2], 2) > eyes.LOGIC_DETECT 
        if on_line:
            print("Line re-acquired.")
            line_found = True
            mission.current_state = RobotState.STRAIGHT
            px.forward(5)
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
    time.sleep(config.STOP_DELAY)
    px.stop()
    current_motor_speed = 0
    time.sleep(config.STOP_HOLD_TIME)
    # Clear the line
    px.forward(base_speed)
    time.sleep(config.STOP_CLEAR_TIME)

def main():
    global stop_flag, current_motor_speed, force_line_lost, force_intersection, run_calibration_flag, no_line_turn

    # --- SENSORS & ACTUATORS ---
    px = Picarx()
    eyes = LineSensor(config.OFFSETS)
    pid = PIDController(config.KP, config.KI, config.KD, min_out=-config.MAX_STEER, max_out=config.MAX_STEER)

    # --- MISSION ---
    # Default mission from main_old.py
    initial_mission = [
        RobotState.STRAIGHT,
        RobotState.LEFT_2,
        RobotState.STRAIGHT,
        RobotState.RIGHT,
        RobotState.STRAIGHT,
        RobotState.APPROACH_STOP
    ]
    mission = MissionManager(initial_mission)

    print("="*40)
    print("PICARX DIRECT CONTROL STARTED")
    print("="*40)
    
    # Load calibration from file (or use defaults)
    cal_min, cal_max = load_calibration()
    eyes.apply_calibration(cal_min, cal_max)
    print("Type 'wiggle' to run live calibration if needed.")

    # Start keyboard listener
    threading.Thread(target=key_listener, args=(mission,), daemon=True).start()

    # --- ZMQ SERVER ---
    server = ServerManager()
    last_published_state = None
    last_published_no_line_turn = None

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

            # --- RECEIVE CAMERA CTE ---
            #camera_cte = server.receive_camera_cte()
            #if camera_cte is not None:
                # Camera CTE available - can be used for sensor fusion
                # For now, log it; uncomment below to blend with line sensor
                # error = camera_cte  # Use camera CTE directly
                # error = 0.5 * error + 0.5 * camera_cte  # Blend both sources
            #    pass

            # Manual intersection trigger
            #if force_intersection:
            #   pattern = "CROSS"
            #    force_intersection = False

            # 3) Handle Mission Stages
            if mission.check_step_requested():
                print(f"Advancing mission. New state: {mission.current_state}")
                pid.reset()

            # --- PUBLISH MISSION STATE ON CHANGE ---
            if mission.current_state != last_published_state or no_line_turn != last_published_no_line_turn:
                server.publish_mission_state(mission.current_state, mission.mission_queue, no_line_turn)
                last_published_state = mission.current_state
                last_published_no_line_turn = no_line_turn

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

            # Trigger no-stop-line turn using camera-provided distance to intersection.
            # This only applies when operator/planner has flagged no-line mode.
            if no_line_turn:
                distance_line = server.receive_intersection_distance()
                if distance_line is not None and 0 < distance_line < config.MAX_TURN_PROXIMITY:
                    if mission.current_state in (RobotState.LEFT_1, RobotState.LEFT_2):
                        turn_dir = "left"
                    elif mission.current_state == RobotState.RIGHT:
                        turn_dir = "right"
                    else:
                        turn_dir = None

                    if turn_dir is not None:
                        if config.TURN_USE_CAMERA:
                            success = execute_turn_with_camera(px, eyes, turn_dir, pid, mission, server)
                        else:
                            success = execute_turn(px, eyes, turn_dir, pid, mission)
                        if success:
                            no_line_turn = False
                            mission.advance_mission()
                        continue

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
                    # Use camera-guided turn if enabled
                    if config.TURN_USE_CAMERA:
                        success = execute_turn_with_camera(px, eyes, "left", pid, mission, server)
                    else:
                        success = execute_turn(px, eyes, "left", pid, mission)
                    if success:
                        no_line_turn = False
                        mission.advance_mission()
                    continue
                elif mission.current_state == RobotState.LEFT_2:
                    mission.crossings_seen += 1
                    if mission.crossings_seen >= 2: # +1 more to account for the stop line
                        if config.TURN_USE_CAMERA:
                            success = execute_turn_with_camera(px, eyes, "left", pid, mission, server)
                        else:
                            success = execute_turn(px, eyes, "left", pid, mission)
                        if success:
                            no_line_turn = False
                            mission.advance_mission()
                    else:
                        print(f"Skipping intersection {mission.crossings_seen}/2")
                        ignore_intersection(px, base_speed)
                    continue
                elif mission.current_state == RobotState.RIGHT:
                    if config.TURN_USE_CAMERA:
                        success = execute_turn_with_camera(px, eyes, "right", pid, mission, server)
                    else:
                        success = execute_turn(px, eyes, "right", pid, mission)
                    if success:
                        no_line_turn = False
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

            steering = pid.update(-smooth_error, dt=dt)
            # steering_with_offset = steering + config.STRAIGHT_ANGLE
            steering = max(-config.MAX_STEER, min(config.MAX_STEER, steering))

            speed_drop = abs(steering) * config.SPEED_DROP_GAIN
            current_speed = max(base_speed - speed_drop, config.MIN_DRIVE_SPEED)

            # set_speed_smooth(px, current_speed, steering_with_offset, ramp_rate=config.SPEED_RAMP_RATE)
            px.forward(current_speed)
            px.set_dir_servo_angle(steering)

            # 7) LOGGING & TELEMETRY
            history.append((time.time() - start_time, mission.current_state, smooth_error, steering, current_speed))
            server.publish_telemetry(current_speed, smooth_error, steering)

            # 8) LOOP TIMING
            elapsed = time.time() - loop_start
            wait_time = config.LOOP_INTERVAL - elapsed
            if wait_time > 0:
                time.sleep(wait_time)

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        px.stop()
        server.close()

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
