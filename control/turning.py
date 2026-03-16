import math
import time

import config
from mission_manager import RobotState


def scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed):
    """Fallback: scan for line using grayscale after camera timeout."""
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
    """Camera-guided turn using a single trajectory snapshot.

    Captures the trajectory once at the start of the turn, then follows it
    open-loop by stepping through CTE points on a fixed time schedule.
    Exits when grayscale sensor re-acquires the line.
    """
    print(f"Executing snapshot-based {direction} turn...")
    camera_tilt_down = int(getattr(config, "TURN_TRAJECTORY_CAMERA_TILT_DOWN", -30))
    px.set_cam_tilt_angle(camera_tilt_down)

    try:
        # Grab the newest trajectory immediately when turn is requested, before
        # stop-hold delays can let fresh data expire.
        server._process_incoming_messages()
        pre_turn_trajectory = server.receive_trajectory()

        # 1) Stop at intersection
        time.sleep(0.1)
        px.stop()
        time.sleep(0.5)
        stopped = True
        current_motor_speed = 0
        time.sleep(config.TURN_STOP_HOLD_TIME)

        # 2) Default steering direction if no camera data
        initial_steer = config.MAX_STEER if direction == "right" else -config.MAX_STEER

        # 3) Capture single trajectory snapshot (wait up to timeout)
        print("  Waiting for trajectory snapshot...")
        snapshot_trajectory = None
        snapshot_start = time.time()

        while (time.time() - snapshot_start) < config.SNAPSHOT_WAIT_TIMEOUT:
            # Keep draining ZMQ while waiting so fresh trajectory packets are ingested.
            server._process_incoming_messages()
            trajectory_data = server.receive_trajectory()
            if trajectory_data is not None:
                cte_list = trajectory_data.get("cte")
                distance_list = trajectory_data.get("distance")

                if cte_list and distance_list and len(cte_list) == len(distance_list):
                    # Build trajectory as list of (distance_cm, cte_cm)
                    snapshot_trajectory = [(d * 100, c * 100) for d, c in zip(distance_list, cte_list)]
                    print(f"  Captured trajectory with {len(snapshot_trajectory)} points")
                    print(f"  Distance range: {snapshot_trajectory[0][0]:.1f}cm to {snapshot_trajectory[-1][0]:.1f}cm")
                    break
            time.sleep(0.05)

        if snapshot_trajectory is None and pre_turn_trajectory is not None:
            cte_list = pre_turn_trajectory.get("cte")
            distance_list = pre_turn_trajectory.get("distance")
            if cte_list and distance_list and len(cte_list) == len(distance_list):
                snapshot_trajectory = [(d * 100, c * 100) for d, c in zip(distance_list, cte_list)]
                print(f"  Using pre-turn trajectory snapshot with {len(snapshot_trajectory)} points")

        if snapshot_trajectory is None:
            print("  No trajectory received — using blind turn")
            px.set_dir_servo_angle(initial_steer)
            px.forward(config.TURN_PWM)
            current_motor_speed = config.TURN_PWM
            time.sleep(config.TURN_BLIND_TIME)
            success, current_motor_speed = scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed)
            return success, current_motor_speed, stopped

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

        turn_start = time.time()
        smoothed_steering = 0.0

        while (time.time() - turn_start) < config.TURN_CAMERA_TIMEOUT:
            current_time = time.time()
            elapsed = current_time - turn_start
            profile_position = min(elapsed / profile_duration, 1.0) * profile_span if profile_span > 0 else 0.0

            # Step through the turn profile from the strongest turn command
            # toward smaller CTE values as time accumulates.
            cte_cm = None
            slope_cte_per_cm = 0.0
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
                        if dist != prev_dist:
                            slope_cte_per_cm = (cte - prev_cte) / (dist - prev_dist)
                    break

            # If we've traveled past all points, use the last one
            if cte_cm is None:
                cte_cm = turn_profile[-1][1]
                if len(turn_profile) >= 2:
                    last_dist, last_cte = turn_profile[-1]
                    prev_dist, prev_cte = turn_profile[-2]
                    if last_dist != prev_dist:
                        slope_cte_per_cm = (last_cte - prev_cte) / (last_dist - prev_dist)

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

            # Feedforward + feedback steering (removes static direction buffer).
            steering_ff = config.TURN_FEEDFORWARD_GAIN * raw_steering

            # Pull fresh trajectory for live CTE tracking during the turn.
            server._process_incoming_messages()
            live_data = server.receive_trajectory()
            cte_tracking_error_cm = 0.0
            if live_data is not None:
                live_cte = live_data.get("cte")
                if live_cte:
                    live_cte_cm = float(live_cte[0]) * 100.0
                    cte_tracking_error_cm = live_cte_cm - cte_cm

            steering_cte_fb = -config.TURN_CTE_FEEDBACK_GAIN * cte_tracking_error_cm

            heading_error_deg = math.degrees(math.atan(slope_cte_per_cm))
            steering_heading_fb = config.TURN_HEADING_FEEDBACK_GAIN * heading_error_deg

            steering_cmd = steering_ff + steering_cte_fb + steering_heading_fb
            alpha = max(0.0, min(1.0, config.TURN_STEER_SMOOTHING_ALPHA))
            smoothed_steering = smoothed_steering + alpha * (steering_cmd - smoothed_steering)
            steering = max(-config.MAX_STEER, min(config.MAX_STEER, smoothed_steering))

            px.set_dir_servo_angle(-steering)
            px.forward(config.TURN_PWM)
            current_motor_speed = config.TURN_PWM

            # Debug output (throttled to ~2.5Hz)
            if int(time.time() * 5) % 2 == 0:
                print(
                    f"  Elapsed={elapsed:.2f}s, Profile={profile_position:.1f}, CTE={cte_cm:.1f}cm, "
                    f"y_ref={y_ref_cm:.1f}cm → Steer={steering:.1f}° "
                    f"(ff={steering_ff:.1f}, cte_fb={steering_cte_fb:.1f}, hdg_fb={steering_heading_fb:.1f})"
                )

            time.sleep(0.05)  # ~20Hz control loop

        # 5) Timeout — fall back to grayscale scan
        print(f"  Turn timeout at {time.time() - turn_start:.2f}s elapsed")
        success, current_motor_speed = scan_for_line_fallback(px, eyes, mission, pid, current_motor_speed)
        return success, current_motor_speed, stopped
    finally:
        px.set_cam_tilt_angle(0)


def execute_turn(px, eyes, direction, pid, mission, current_motor_speed):
    """Wait for full-width line, then turn until line is reacquired."""
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
            current_motor_speed = config.TURN_POST_SPEED
            break
        time.sleep(config.TURN_SCAN_INTERVAL)

    if not line_found:
        print("Turn failed to re-acquire line.")
        px.stop()
        current_motor_speed = 0
        pid.reset()
        mission.current_state = RobotState.IDLE
        return False, current_motor_speed

    # 3) Stabilize
    pid.reset()
    return True, current_motor_speed


def execute_pivot_turn(px, eyes, direction, pid, mission, current_motor_speed, stopped):
    """Turn in place using direct left/right motor control."""
    print(f"Executing in-place {direction} turn...")

    # Stop and center steering before pivoting.
    time.sleep(0.1)
    px.stop()
    stopped = True
    current_motor_speed = 0
    time.sleep(config.TURN_STOP_HOLD_TIME)
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)

    # Picarx API is indexed: 1=left motor, 2=right motor.
    # Due motor orientation, same signed values produce opposite wheel motion physically.
    pivot_sign = 1 if direction == "right" else -1
    pivot_speed = config.PIVOT_TURN_PWM * pivot_sign
    align_threshold = float(getattr(config, "PIVOT_ALIGN_SENSOR_THRESHOLD", 0.72))
    align_enabled = bool(getattr(config, "PIVOT_ALIGN_ENABLE", True))
    sequence_order = [2, 1, 0] if direction == "right" else [0, 1, 2]
    sequence_index = 0
    require_line_sequence = bool(getattr(config, "PIVOT_REQUIRE_LINE_SEQUENCE", True))
    pivot_max_pre_scan = min(
        float(getattr(config, "PIVOT_SCAN_TIMEOUT", 2.5)),
        float(getattr(config, "PIVOT_MAX_PRE_SCAN_TIME", 1.0)),
    )

    pivot_start = time.time()
    while True:
        px.set_motor_speed(1, pivot_speed)
        px.set_motor_speed(2, pivot_speed)

        elapsed = time.time() - pivot_start
        raw = px.get_grayscale_data()
        if align_enabled and elapsed >= config.PIVOT_ALIGN_MIN_TIME:
            current_sensor = sequence_order[sequence_index]
            current_seen = eyes.color_signal(raw[current_sensor], current_sensor) > align_threshold
            if current_seen:
                sequence_index += 1
                if sequence_index >= len(sequence_order):
                    print(f"Pivot alignment sequence acquired after {elapsed:.2f}s.")
                    break
                print(
                    f"Pivot sequence step reached ({sequence_index}/{len(sequence_order)}), "
                    f"next sensor={sequence_order[sequence_index]}."
                )

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