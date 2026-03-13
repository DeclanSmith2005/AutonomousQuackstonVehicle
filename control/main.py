import csv
import math
import os
import threading
import time
from picarx import Picarx
from robot_hat import Music

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
run_calibration_flag = False
no_line_turn = False
stopped = False

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
            px.forward(config.BASE_SPEED)
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
    """Camera-guided turn using a single trajectory snapshot.
    
    Captures the trajectory once at the start of the turn, then follows it
    open-loop by stepping through CTE points on a fixed time schedule.
    Exits when grayscale sensor re-acquires the line.
    """
    global current_motor_speed, stopped
    
    print(f"Executing snapshot-based {direction} turn...")
    
    # 1) Stop at intersection
    time.sleep(0.1)
    px.stop()
    stopped = True
    current_motor_speed = 0
    time.sleep(config.TURN_STOP_HOLD_TIME)
    
    # 2) Default steering direction if no camera data
    initial_steer = config.MAX_STEER if direction == "right" else -config.MAX_STEER
    
    # 3) Capture single trajectory snapshot (wait up to 1 second)
    print("  Waiting for trajectory snapshot...")
    snapshot_trajectory = None
    snapshot_start = time.time()
    
    while (time.time() - snapshot_start) < config.SNAPSHOT_WAIT_TIMEOUT:
        trajectory_data = server.receive_trajectory()
        if trajectory_data is not None:
            cte_list = trajectory_data.get('cte')
            distance_list = trajectory_data.get('distance')
            
            if cte_list and distance_list and len(cte_list) == len(distance_list):
                # Build trajectory as list of (distance_cm, cte_cm)
                snapshot_trajectory = [(d * 100, c * 100) for d, c in zip(distance_list, cte_list)]
                print(f"  Captured trajectory with {len(snapshot_trajectory)} points")
                print(f"  Distance range: {snapshot_trajectory[0][0]:.1f}cm to {snapshot_trajectory[-1][0]:.1f}cm")
                break
        time.sleep(0.05)
    
    if snapshot_trajectory is None:
        print("  No trajectory received — using blind turn")
        px.set_dir_servo_angle(initial_steer)
        px.forward(config.TURN_PWM)
        time.sleep(config.TURN_BLIND_TIME)
        return scan_for_line_fallback(px, eyes, mission, pid)

    # Use near-to-far ordering: (elapsed_distance_cm, cte_cm) starting from 0.0
    start_distance_cm = snapshot_trajectory[0][0]
    turn_profile = [(dist - start_distance_cm, cte) for dist, cte in snapshot_trajectory]

    print(
        f"  Turn profile (near-to-far): {len(turn_profile)} samples from "
        f"{turn_profile[0][0]:.1f}cm to {turn_profile[-1][0]:.1f}cm"
    )
    
    # 4) Follow the snapshot trajectory on a fixed timeline.
    profile_duration = max(config.TURN_PROFILE_DURATION, 0.01)
    profile_span = turn_profile[-1][0] if turn_profile else 0.0
    print(f"  Turn profile duration: {profile_duration:.2f}s")

    # Start with full steering lock, then blend into the camera trajectory.
    # px.set_dir_servo_angle(initial_steer)
    # px.forward(config.TURN_PWM)
    # current_motor_speed = config.TURN_PWM
    
    turn_start = time.time()
    
    while (time.time() - turn_start) < config.TURN_CAMERA_TIMEOUT:
        current_time = time.time()
        elapsed = current_time - turn_start
        profile_position = min(elapsed / profile_duration, 1.0) * profile_span if profile_span > 0 else 0.0
        
        # Check grayscale — if line found, handoff to straight mode
        # Only check after the turn profile is complete to avoid detecting the intersection line.
        # For right turns, monitor right sensor (index 2); for left turns, monitor left sensor (index 0)
        # if elapsed >= profile_duration:
        #     raw = px.get_grayscale_data()
        #     sensor_idx = 2 if direction == "right" else 0  # right=2, left=0
        #     on_line = eyes.color_signal(raw[sensor_idx], sensor_idx) > eyes.LOGIC_DETECT
        #     if on_line:
        #         print(f"Line re-acquired by {direction} grayscale (sensor {sensor_idx}) at {elapsed:.2f}s — exiting turn")
        #         mission.current_state = RobotState.STRAIGHT
        #         pid.reset()
        #         px.forward(5)
        #         return True
        
        # Step through the turn profile from the strongest turn command
        # toward smaller CTE values as time accumulates.
        cte_cm = None
        for i, (dist, cte) in enumerate(turn_profile):
            if profile_position <= dist:
                # Interpolate between previous and current point
                if i == 0:
                    cte_cm = cte
                else:
                    prev_dist, prev_cte = turn_profile[i - 1]
                    # Linear interpolation
                    ratio = (profile_position - prev_dist) / (dist - prev_dist) if dist != prev_dist else 0
                    cte_cm = prev_cte + ratio * (cte - prev_cte)
                break

        # If we've traveled past all points, use the last one
        if cte_cm is None:
            cte_cm = turn_profile[-1][1]
        
        # Bicycle model steering: delta = arctan(2 * L * CTE / y_ref^2)
        # Negative CTE maps to positive (right) steering for right turns
        # where L = wheelbase, CTE = lateral error, y_ref = distance to point
        y_ref_cm = max(start_distance_cm + profile_position, config.TURN_LOOKAHEAD_MIN_CM)
        if y_ref_cm > 0:
            numerator = -2 * config.WHEELBASE_CM * cte_cm
            denominator = y_ref_cm * y_ref_cm
            raw_steering = math.degrees(math.atan(numerator / denominator))
        else:
            raw_steering = 0.0

        steering = max(-config.MAX_STEER, min(config.MAX_STEER, raw_steering))

        # if direction == "right":
        #     steering += config.ANGLE_BUFFER_RIGHT
        # else:
        #     steering -= config.ANGLE_BUFFER_LEFT

        px.set_dir_servo_angle(steering)
        px.forward(config.TURN_PWM)
        current_motor_speed = config.TURN_PWM
        
        # Debug output (throttled to ~2.5Hz)
        if int(time.time() * 5) % 2 == 0:
            print(
                f"  Elapsed={elapsed:.2f}s, Profile={profile_position:.1f}, CTE={cte_cm:.1f}cm, "
                f"y_ref={y_ref_cm:.1f}cm → Steer={steering:.1f}° (raw={raw_steering:.1f}°)"
            )
        
        time.sleep(0.05)  # ~20Hz control loop
    
    # 5) Timeout — fall back to grayscale scan
    print(f"  Turn timeout at {time.time() - turn_start:.2f}s elapsed")
    return scan_for_line_fallback(px, eyes, mission, pid)


def key_listener(mission):
    """
    Interactive keyboard control for mission management and failure testing.
    s: stop
    st/a/l1/l2/r/idle/cal: manually jump to state
    n: next mission stage
    reset: reset mission
    fl: toggle forced line lost (simulates sensor failure)
    wiggle: run wiggle calibration
    """
    global stop_flag, force_line_lost, run_calibration_flag, no_line_turn
    print("Keyboard listener active.")
    print("Commands: s=stop, st=straight, a=approach_stop, l1/l2=left, r=right, idle=idle, cal=calibrate")
    print("          n=next, reset=reset, fl=force line lost")
    print("          wiggle=run wiggle calibration")
    
    while not stop_flag:
        try:
            cmd = input().strip().lower()
            if not cmd:
                continue

            # Default: reset no_line_turn unless command is one of the *_no_line variants
            if cmd not in ("rnl", "lnl_1", "lnl_2"):
                no_line_turn = False

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
            elif cmd in ("n", "next"):
                mission.request_step()
                print("Mission step requested.")
            elif cmd in ("reset", "mr"):
                mission.reset_mission()
            elif cmd == "wiggle":
                run_calibration_flag = True
                print("Wiggle calibration requested...")
            elif cmd == "fl":
                force_line_lost = not force_line_lost
                print(f"Forced line lost: {force_line_lost}")
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
    time.sleep(config.TURN_BLIND_TIME)  # Blind turn duration before scanning for line

    line_found = False
    start_scan = time.time()
    while (time.time() - start_scan) < config.TURN_SCAN_TIMEOUT:
        raw = px.get_grayscale_data()
        on_line = any(eyes.color_signal(raw[i], i) > eyes.LOGIC_DETECT for i in range(3))
        if on_line:
            print("Line re-acquired.")
            line_found = True
            mission.current_state = RobotState.STRAIGHT
            px.forward(config.TURN_POST_SPEED)
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


def execute_pivot_turn(px, eyes, direction, pid, mission):
    """Turn in place using direct left/right motor control."""
    global current_motor_speed, stopped

    print(f"Executing in-place {direction} turn...")

    # Stop and center steering before pivoting.
    time.sleep(0.3)
    px.stop()
    stopped = True
    current_motor_speed = 0
    time.sleep(config.TURN_STOP_HOLD_TIME)
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)

    # Picarx API is indexed: 1=left motor, 2=right motor.
    # Due motor orientation, same signed values produce opposite wheel motion physically.
    pivot_sign = 1 if direction == "right" else -1
    pivot_speed = config.PIVOT_TURN_PWM * pivot_sign

    line_found = False
    start_scan = time.time()
    while (time.time() - start_scan) < config.PIVOT_SCAN_TIMEOUT:
        px.set_motor_speed(1, pivot_speed)
        px.set_motor_speed(2, pivot_speed)

        raw = px.get_grayscale_data()
        sensor_idx = 2 if direction == "right" else 0
        on_line = eyes.color_signal(raw[sensor_idx], sensor_idx) > eyes.LOGIC_DETECT
        if on_line:
            print(f"Line re-acquired during pivot ({direction}).")
            line_found = True
            mission.current_state = RobotState.STRAIGHT
            px.forward(config.TURN_POST_SPEED)
            current_motor_speed = config.TURN_POST_SPEED
            break

        time.sleep(config.TURN_SCAN_INTERVAL)

    if not line_found:
        print("Pivot turn failed to re-acquire line.")
        px.stop()
        current_motor_speed = 0
        pid.reset()
        mission.current_state = RobotState.IDLE
        return False

    pid.reset()
    return True

def ignore_intersection(px, speed):
    """Drive straight through an intersection without turning."""
    global current_motor_speed
    px.forward(speed)
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)
    current_motor_speed = speed
    time.sleep(config.PASS_TIME)

def stop_at_line(px, base_speed):
    """Stop at a stop line, hold, then drive forward to clear it."""
    global current_motor_speed
    time.sleep(config.STOP_DELAY)
    px.stop()
    current_motor_speed = 0
    time.sleep(config.STOP_HOLD_TIME)
    # Clear the line
    px.forward(base_speed)
    time.sleep(config.STOP_CLEAR_TIME)

def main():
    global stop_flag, current_motor_speed, force_line_lost, run_calibration_flag, no_line_turn, stopped

    # --- SENSORS & ACTUATORS ---
    px = Picarx()
    eyes = LineSensor(config.OFFSETS)
    pid = PIDController(config.KP, config.KI, config.KD, min_out=-config.MAX_STEER, max_out=config.MAX_STEER)
    # --- MISSION ---
    # Current active mission
    initial_mission = [
        RobotState.STRAIGHT,
        RobotState.STRAIGHT,
        RobotState.STRAIGHT,
        RobotState.RIGHT,
        RobotState.STRAIGHT,
        RobotState.RIGHT
    ]
    mission = MissionManager(initial_mission)

    # Preload the horn sound once so duck events can trigger immediate playback.
    horn_file = os.path.join(os.path.dirname(__file__), "testing", "sound", "car-double-horn.wav")
    horn_player = None
    if os.path.exists(horn_file):
        try:
            horn_player = Music()
            horn_player.music_set_volume(100)
        except Exception as e:
            print(f"Horn audio unavailable: {e}")
    else:
        print(f"Horn sound file not found: {horn_file}")

    # True while perception reports a duck in view; blocks all motion commands.
    duck_stop_active = False

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
    last_mission_publish_time = 0.0

    error_buffer = [0.0] * config.ERROR_BUFFER_LEN
    history = []
    start_time = time.time()
    last_valid_line_time = time.time()
    last_pid_time = time.time()

    try:
        while not stop_flag:
            loop_start = time.time()
            
            # Process all incoming ZMQ messages once per loop
            server._process_incoming_messages()

            # Check for calibration request
            if run_calibration_flag:
                run_calibration_flag = False
                run_wiggle_calibration(px, eyes)
                continue

            # 1) Get Hardware Data
            raw = px.get_grayscale_data()
            
            # Distance check (Obstacle avoidance failsafe)
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

            # 3) Handle Mission Stages
            if mission.check_step_requested():
                print(f"Advancing mission. New state: {mission.current_state}")
                pid.reset()

            # --- PUBLISH MISSION STATE ON CHANGE ---
            should_heartbeat_publish = (time.time() - last_mission_publish_time) >= config.MISSION_STATE_HEARTBEAT
            if mission.current_state != last_published_state or no_line_turn != last_published_no_line_turn or should_heartbeat_publish:
                server.publish_mission_state(mission.current_state, mission.mission_queue, no_line_turn, stopped)
                last_published_state = mission.current_state
                last_published_no_line_turn = no_line_turn
                last_mission_publish_time = time.time()

            # Highest-priority perception safety override.
            # While a duck is visible, stop, honk once on entry, and skip control actions.
            duck_visible = server.receive_duck_visible()
            if duck_visible:
                if not duck_stop_active:
                    print("Duck detected: stopping vehicle and playing horn.")
                    duck_stop_active = True
                    # Freeze in IDLE so downstream logic cannot reissue drive commands.
                    mission.current_state = RobotState.IDLE
                    pid.reset()
                    px.stop()
                    current_motor_speed = 0
                    stopped = True
                    # One-shot horn on transition False -> True.
                    if horn_player is not None:
                        try:
                            horn_player.sound_play(horn_file, volume=100)
                        except Exception as e:
                            print(f"Horn playback failed: {e}")
                else:
                    # Keep applying stop while the duck remains visible.
                    px.stop()
                    current_motor_speed = 0
                    stopped = True
                time.sleep(config.LOOP_INTERVAL)
                continue
            elif duck_stop_active:
                # Duck is gone: clear lockout and return to lane-following state.
                duck_stop_active = False
                stopped = False
                mission.current_state = RobotState.STRAIGHT
                pid.reset()
                # Reset timing state to avoid derivative and failsafe spikes on resume.
                last_pid_time = time.time()
                last_valid_line_time = time.time()
                print("Duck no longer visible: resuming motion.")

            # 4) State Machine Failsafes
            if mission.current_state == RobotState.IDLE:
                px.stop()
                current_motor_speed = 0
                stopped = True
                time.sleep(0.5)
                continue

            if mission.current_state == RobotState.CALIBRATE:
                print(f"RAW: {raw} | PATTERN: {pattern}")
                time.sleep(0.5)
                continue

            if (mission.current_state == RobotState.APPROACH_STOP or mission.current_state == RobotState.LEFT_1
                    or mission.current_state == RobotState.LEFT_2 or mission.current_state == RobotState.RIGHT):
                print("Approaching STOP LINE...")
                px.set_cam_tilt_angle(-30)
                px.forward(config.TURN_ENTRY_SPEED)
                current_motor_speed = config.TURN_ENTRY_SPEED

            # No-stop-line mode: wait for CROSS detection, then execute a pivot turn.
            if no_line_turn:
                if mission.current_state in (RobotState.LEFT_1, RobotState.LEFT_2):
                    turn_dir = "left"
                elif mission.current_state == RobotState.RIGHT:
                    turn_dir = "right"
                else:
                    turn_dir = None

                if turn_dir is not None and pattern == "CROSS":
                    print(f"No-stop-line CROSS detected. Executing pivot {turn_dir} turn.")
                    success = execute_pivot_turn(px, eyes, turn_dir, pid, mission)
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
                    elif config.TURN_USE_PIVOT:
                        success = execute_pivot_turn(px, eyes, "left", pid, mission)
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
                        elif config.TURN_USE_PIVOT:
                            success = execute_pivot_turn(px, eyes, "left", pid, mission)
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
                    elif config.TURN_USE_PIVOT:
                        success = execute_pivot_turn(px, eyes, "right", pid, mission)
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
            steering = max(-config.MAX_STEER, min(config.MAX_STEER, steering))

            speed_drop = abs(steering) * config.SPEED_DROP_GAIN
            current_speed = max(base_speed - speed_drop, config.MIN_DRIVE_SPEED)

            px.forward(current_speed)
            px.set_dir_servo_angle(steering)
            stopped = False

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
