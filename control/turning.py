import math
import time

import config
from mission_manager import RobotState


def scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed):
    """
    Fallback routine: scan for the line using grayscale sensors after a 
    timed or camera-guided turn segment.

    Parameters
    ----------
    px : Picarx
        The robot hardware interface.
    eyes : LineSensor
        The grayscale sensor processor.
    mission : MissionManager
        To update robot state upon line acquisition.
    pid : PIDController
        To reset steering memory after re-acquisition.
    current_motor_speed : int
        Current speed to be updated.

    Returns
    -------
    tuple (bool, int)
        (Success status, updated motor speed).
    """
    print("Camera fallback: scanning with grayscale...")
    line_found = False
    start_scan = time.time()

    while (time.time() - start_scan) < config.TURN_SCAN_TIMEOUT:
        raw = px.get_grayscale_data()
        # Check if any sensor detects the line
        on_line = any(eyes.color_signal(raw[i], i) > eyes.LOGIC_DETECT for i in range(3))
        if on_line:
            print("Line re-acquired by grayscale.")
            line_found = True
            mission.current_state = RobotState.STRAIGHT
            px.forward(config.BASE_SPEED)
            current_motor_speed = config.BASE_SPEED
            break
        time.sleep(config.TURN_SCAN_INTERVAL)

    if not line_found:
        print("Turn failed to re-acquire line.")
        px.stop()
        current_motor_speed = 0
        pid.reset()
        mission.current_state = RobotState.IDLE
        return False, current_motor_speed

    pid.reset()
    return True, current_motor_speed


def execute_turn_with_camera(px, eyes, direction, pid, mission, server, current_motor_speed, stopped):
    """
    Camera-guided turn using a single trajectory snapshot.

    Captures the first valid trajectory snapshot after stop + camera down-tilt,
    then follows it by stepping through CTE points on a fixed time schedule
    (bicycle model).
    Exits when grayscale sensor re-acquires the line.

    Parameters
    ----------
    direction : str
        "left" or "right".
    server : ServerManager
        To receive trajectory data from perception.
    """
    print(f"Executing snapshot-based {direction} turn...")
    camera_tilt_down = int(config.TURN_TRAJECTORY_CAMERA_TILT_DOWN)
    px.set_cam_tilt_angle(camera_tilt_down)

    try:
        trajectory_max_age = float(config.TURN_TRAJECTORY_MAX_AGE)

        # 1) Stop at intersection to stabilize
        time.sleep(0.1)
        px.stop()
        time.sleep(0.5)
        stopped = True
        current_motor_speed = 0
        time.sleep(config.TURN_STOP_HOLD_TIME)

        # 2) Default steering direction for backup
        initial_steer = config.MAX_STEER if direction == "right" else -config.MAX_STEER

        # 3) Capture single trajectory snapshot
        print("  Waiting for trajectory snapshot...")
        snapshot_trajectory = None
        snapshot_start = time.time()

        while (time.time() - snapshot_start) < config.SNAPSHOT_WAIT_TIMEOUT:
            server.process_incoming_messages()
            trajectory_data = server.receive_trajectory(max_age_s=trajectory_max_age)
            if trajectory_data is not None:
                cte_list = trajectory_data.get("cte")
                distance_list = trajectory_data.get("distance")

                if cte_list and distance_list and len(cte_list) == len(distance_list):
                    # Build trajectory as list of (distance_cm, cte_cm)
                    snapshot_trajectory = [(d * 100, c * 100) for d, c in zip(distance_list, cte_list)]
                    # Enforce closest-to-furthest order so steering angles progress along the path.
                    snapshot_trajectory.sort(key=lambda p: p[0])
                    print(f"  Captured trajectory with {len(snapshot_trajectory)} points")
                    break
            time.sleep(0.05)

        if snapshot_trajectory is None:
            print("  No trajectory received — using blind turn")
            px.set_dir_servo_angle(initial_steer)
            px.forward(config.TURN_PWM)
            current_motor_speed = config.TURN_PWM
            time.sleep(config.TURN_BLIND_TIME)
            success, current_motor_speed = scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed)
            return success, current_motor_speed, stopped

        # Use near-to-far ordering: (elapsed_distance_cm, cte_cm)
        start_distance_cm = snapshot_trajectory[0][0]
        turn_profile = [(dist - start_distance_cm, cte) for dist, cte in snapshot_trajectory]

        # 4) Follow the snapshot trajectory on a fixed timeline.
        profile_duration = max(config.TURN_PROFILE_DURATION, 0.01)
        profile_span = turn_profile[-1][0] if turn_profile else 0.0
        snapshot_max_abs_cte = max((abs(cte) for _, cte in turn_profile), default=1.0)
        if snapshot_max_abs_cte <= 0.0:
            snapshot_max_abs_cte = 1.0
        
        turn_start = time.time()
        smoothed_steering = 0.0
        # Guarantee we complete the planned profile before attempting grayscale recovery.
        min_turn_runtime = max(float(config.TURN_CAMERA_TIMEOUT), float(profile_duration))

        while (time.time() - turn_start) < min_turn_runtime:
            current_time = time.time()
            elapsed = current_time - turn_start
            profile_position = min(elapsed / profile_duration, 1.0) * profile_span if profile_span > 0 else 0.0

            # Linear interpolation for target CTE
            cte_cm = None
            slope_cte_per_cm = 0.0
            for i, (dist, cte) in enumerate(turn_profile):
                if profile_position <= dist:
                    if i == 0:
                        cte_cm = cte
                    else:
                        prev_dist, prev_cte = turn_profile[i - 1]
                        ratio = (profile_position - prev_dist) / (dist - prev_dist) if dist != prev_dist else 0
                        cte_cm = prev_cte + ratio * (cte - prev_cte)
                        if dist != prev_dist:
                            slope_cte_per_cm = (cte - prev_cte) / (dist - prev_dist)
                    break

            if cte_cm is None:
                cte_cm = turn_profile[-1][1]
                if len(turn_profile) >= 2:
                    last_dist, last_cte = turn_profile[-1]
                    prev_dist, prev_cte = turn_profile[-2]
                    if last_dist != prev_dist:
                        slope_cte_per_cm = (last_cte - prev_cte) / (last_dist - prev_dist)

            # Progressive steering profile:
            # - sign follows CTE direction
            # - magnitude follows relative CTE size in the snapshot
            # - command ramps up over profile time
            cte_sign = -1.0 if cte_cm < 0.0 else (1.0 if cte_cm > 0.0 else 0.0)
            cte_mag_norm = min(1.0, abs(cte_cm) / snapshot_max_abs_cte)
            time_progress = min(max(elapsed / profile_duration, 0.0), 1.0)
            steering_cmd = cte_sign * config.MAX_STEER * cte_mag_norm * time_progress
            alpha = max(0.0, min(1.0, config.TURN_STEER_SMOOTHING_ALPHA))
            smoothed_steering = smoothed_steering + alpha * (steering_cmd - smoothed_steering)
            steering = max(-config.MAX_STEER, min(config.MAX_STEER, smoothed_steering))

            # Keep steering sign consistent with the current target CTE.
            if cte_cm < 0.0 and steering > 0.0:
                steering = 0.0
            elif cte_cm > 0.0 and steering < 0.0:
                steering = 0.0

            servo_cmd = -steering
            if direction == "right" and servo_cmd < 0:
                servo_cmd = 0.0
            elif direction == "left" and servo_cmd > 0:
                servo_cmd = 0.0

            if direction == "right":
                servo_cmd += 27
            else:
                servo_cmd -= 27

            px.set_dir_servo_angle(servo_cmd)
            px.forward(config.TURN_PWM)
            current_motor_speed = config.TURN_PWM

            # Throttled debug logs
            if int(time.time() * 5) % 2 == 0:
                print(f"  Turn Tracking: CTE={cte_cm:.1f}cm, Steer={steering:.1f}°")

            time.sleep(0.05)

        # 5) Timeout — fall back to grayscale scan
        print(f"  Turn segment complete at {time.time() - turn_start:.2f}s; starting grayscale recovery scan")
        success, current_motor_speed = scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed)
        return success, current_motor_speed, stopped
    finally:
        px.set_cam_tilt_angle(0)


def execute_turn(px, eyes, direction, pid, mission, current_motor_speed):
    """
    Classic timed turn: steer at max angle for a fixed duration, 
    then scan for line.
    """
    print(f"Executing {direction} turn...")

    # 1) Stop before turning
    current_motor_speed = 0
    px.forward(current_motor_speed)
    time.sleep(config.TURN_STOP_HOLD_TIME)

    # 2) Manual turn
    steer = config.MAX_STEER if direction == "right" else -config.MAX_STEER
    px.forward(config.TURN_PWM)
    px.set_dir_servo_angle(steer)
    current_motor_speed = config.TURN_PWM
    time.sleep(config.TURN_BLIND_TIME)

    # 3) Scan for line re-acquisition
    success, current_motor_speed = scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed)
    return success, current_motor_speed


def execute_pivot_turn(px, eyes, direction, pid, mission, current_motor_speed, stopped):
    """
    In-place pivot turn using differential motor control.
    """
    print(f"Executing in-place {direction} turn...")

    # Stop and center steering before pivoting.
    time.sleep(0.1)
    px.stop()
    stopped = True
    current_motor_speed = 0
    time.sleep(config.TURN_STOP_HOLD_TIME)
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)

    pivot_sign = 1 if direction == "right" else -1
    pivot_speed = config.PIVOT_TURN_PWM * pivot_sign
    align_threshold = float(config.PIVOT_ALIGN_SENSOR_THRESHOLD)
    align_enabled = bool(config.PIVOT_ALIGN_ENABLE)
    
    # Detect sensors in specific order based on turn direction
    sequence_order = [2, 1, 0] if direction == "right" else [0, 1, 2]
    sequence_index = 0
    require_line_sequence = bool(config.PIVOT_REQUIRE_LINE_SEQUENCE)
    pivot_max_pre_scan = min(
        float(config.PIVOT_SCAN_TIMEOUT),
        float(config.PIVOT_MAX_PRE_SCAN_TIME),
    )

    pivot_start = time.time()
    while True:
        px.set_motor_speed(1, pivot_speed)
        px.set_motor_speed(2, pivot_speed)

        elapsed = time.time() - pivot_start
        raw = px.get_grayscale_data()
        
        # Check for sensor alignment sequence
        if align_enabled and elapsed >= config.PIVOT_ALIGN_MIN_TIME:
            current_sensor = sequence_order[sequence_index]
            current_seen = eyes.color_signal(raw[current_sensor], current_sensor) > align_threshold
            if current_seen:
                sequence_index += 1
                if sequence_index >= len(sequence_order):
                    print(f"Pivot alignment sequence acquired after {elapsed:.2f}s.")
                    break

        if (not require_line_sequence) and elapsed >= pivot_max_pre_scan:
            print(f"Pivot pre-scan timeout reached ({elapsed:.2f}s); switching to forward scan.")
            break

        time.sleep(config.TURN_SCAN_INTERVAL)

    px.stop()
    current_motor_speed = 0
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)

    print("Pivot complete. Driving forward before line scan...")
    px.forward(config.TURN_POST_SPEED)
    current_motor_speed = config.TURN_POST_SPEED
    stopped = False
    time.sleep(config.PIVOT_FORWARD_SETTLE_TIME)

    success, current_motor_speed = scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed)
    if success:
        stopped = False
    return success, current_motor_speed, stopped