import csv
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
from turning import execute_pivot_turn, execute_turn, execute_turn_with_camera

# --- GLOBALS ---
stop_flag = False
current_motor_speed = 0
force_line_lost = False
run_calibration_flag = False
no_line_turn = False
stopped = False
no_line_arm_time = 0.0


def _signed_heading_delta_deg(new_heading_deg, old_heading_deg):
    """Return wrapped heading delta in degrees in [-180, 180]."""
    return ((new_heading_deg - old_heading_deg + 180.0) % 360.0) - 180.0


def _normalized_turn_mode():
    """Resolve global turn execution mode with backward compatibility."""
    mode = str(getattr(config, "TURN_EXECUTION_MODE", "")).strip().lower()
    if mode in ("trajectory", "pivot", "classic"):
        return mode

    # Legacy fallback path.
    if bool(getattr(config, "TURN_USE_CAMERA", False)):
        return "trajectory"
    if bool(getattr(config, "TURN_USE_PIVOT", False)):
        return "pivot"
    return "classic"


def _turn_triggered(mode, grayscale_triggered, camera_distance_cm, threshold_cm):
    """Evaluate trigger source mode (grayscale/camera/either)."""
    camera_triggered = camera_distance_cm is not None and camera_distance_cm <= threshold_cm
    trigger_mode = str(mode).strip().lower()
    if trigger_mode == "grayscale":
        return bool(grayscale_triggered)
    if trigger_mode == "camera":
        return bool(camera_triggered)
    return bool(grayscale_triggered or camera_triggered)


def _execute_turn_by_mode(px, eyes, direction, pid, mission, server, current_speed, is_stopped, mode):
    """Execute turn using one unified mode selector."""
    if mode == "trajectory":
        return execute_turn_with_camera(
            px,
            eyes,
            direction,
            pid,
            mission,
            server,
            current_speed,
            is_stopped,
        )
    if mode == "pivot":
        return execute_pivot_turn(
            px,
            eyes,
            direction,
            pid,
            mission,
            current_speed,
            is_stopped,
        )

    success, current_speed = execute_turn(
        px,
        eyes,
        direction,
        pid,
        mission,
        current_speed,
    )
    return success, current_speed, is_stopped


def _roundabout_entry_pivot_nudge(px, direction, pwm, duration_s):
    """Apply a short in-place pivot after roundabout entry stop line."""
    pivot_sign = 1 if direction == "right" else -1
    pivot_speed = int(pwm) * pivot_sign
    start = time.time()
    while (time.time() - start) < duration_s:
        px.set_motor_speed(1, pivot_speed)
        px.set_motor_speed(2, pivot_speed)
        time.sleep(config.TURN_SCAN_INTERVAL)
    px.stop()
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)


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
    global stop_flag, force_line_lost, run_calibration_flag, no_line_turn, no_line_arm_time
    print("Keyboard listener active.")
    print("Commands: s=stop, st=straight, a=approach_stop, l1/l2=left, r=right, idle=idle, cal=calibrate")
    print("          rbe/rbc/rbp/rbx=roundabout entry/circulate/exit_prep/exit_commit")
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
            elif cmd == "rbe":
                mission.current_state = RobotState.ROUNDABOUT_ENTRY
                mission.crossings_seen = 0
                print("Manual State: ROUNDABOUT_ENTRY")
            elif cmd == "rbc":
                mission.current_state = RobotState.ROUNDABOUT_CIRCULATE
                mission.crossings_seen = 0
                print("Manual State: ROUNDABOUT_CIRCULATE")
            elif cmd == "rbp":
                mission.current_state = RobotState.ROUNDABOUT_EXIT_PREP
                mission.crossings_seen = 0
                print("Manual State: ROUNDABOUT_EXIT_PREP")
            elif cmd == "rbx":
                mission.current_state = RobotState.ROUNDABOUT_EXIT_COMMIT
                mission.crossings_seen = 0
                print("Manual State: ROUNDABOUT_EXIT_COMMIT")
            elif cmd == "cal":
                mission.current_state = RobotState.CALIBRATE
                print("Manual State: CALIBRATE")
            elif cmd == "i":
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
                no_line_arm_time = time.time()
                print("Manual State: RIGHT_NO_LINE")
            elif cmd == "lnl_1":
                mission.current_state = RobotState.LEFT_1
                mission.crossings_seen = 0
                no_line_turn = True
                no_line_arm_time = time.time()
                print("Manual State: LEFT_1_NO_LINE")
            elif cmd == "lnl_2":
                mission.current_state = RobotState.LEFT_2
                mission.crossings_seen = 0
                no_line_turn = True
                no_line_arm_time = time.time()
                print("Manual State: LEFT_2_NO_LINE")

        except EOFError:
            break

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
    global stop_flag, current_motor_speed, force_line_lost, run_calibration_flag, no_line_turn, stopped, no_line_arm_time

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
    control_dir = os.path.dirname(__file__)
    project_dir = os.path.dirname(control_dir)
    horn_candidates = [
        os.path.join(control_dir, "testing", "sound", "car-double-horn.wav"),
        os.path.join(project_dir, "sound", "car-double-horn.wav"),
    ]
    horn_file = next((path for path in horn_candidates if os.path.exists(path)), None)
    horn_player = None
    if horn_file is not None:
        try:
            horn_player = Music()
            horn_player.music_set_volume(100)
        except Exception as e:
            print(f"Horn audio unavailable: {e}")
    else:
        print("Horn sound file not found in expected locations.")

    # True while perception reports a duck in view; blocks all motion commands.
    duck_stop_active = False
    duck_resume_state = None

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
    error_buffer_seeded = False
    history = []
    start_time = time.time()
    last_valid_line_time = time.time()
    last_pid_time = time.time()
    no_line_arm_time = 0.0
    last_heading_deg = None
    roundabout_heading_accum_deg = 0.0
    previous_state = mission.current_state
    roundabout_circulate_start_time = None
    roundabout_exit_search_start_time = None
    roundabout_exit_branch_hits = 0

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
            line_distance_cm = server.receive_intersection_distance()
            localization = server.receive_localization()
            error, _, base_speed = eyes.compute_error(raw)
            if not error_buffer_seeded and eyes.last_line_seen:
                error_buffer = [error] * max(1, config.ERROR_BUFFER_LEN)
                error_buffer_seeded = True
            full_cross_triggered = pattern == "CROSS"
            grayscale_turn_triggered = full_cross_triggered

            roundabout_exit_mode = str(getattr(config, "ROUNDABOUT_EXIT_TRIGGER_MODE", "line")).strip().lower()

            if mission.current_state != previous_state:
                if mission.current_state == RobotState.ROUNDABOUT_CIRCULATE:
                    roundabout_circulate_start_time = time.time()
                    last_heading_deg = None
                    roundabout_heading_accum_deg = 0.0
                    print(f"Roundabout circulate entered (exit_mode={roundabout_exit_mode}).")
                elif mission.current_state == RobotState.ROUNDABOUT_EXIT_PREP:
                    roundabout_exit_search_start_time = time.time()
                    roundabout_exit_branch_hits = 0
                    print("Roundabout exit prep entered: searching for branch cue.")
                previous_state = mission.current_state

            if roundabout_exit_mode == "heading":
                if mission.current_state == RobotState.ROUNDABOUT_CIRCULATE and localization is not None:
                    heading_deg = localization.get("heading_deg")
                    if heading_deg is not None:
                        if last_heading_deg is None:
                            last_heading_deg = heading_deg
                        else:
                            delta = _signed_heading_delta_deg(heading_deg, last_heading_deg)
                            if abs(delta) <= 45.0:
                                roundabout_heading_accum_deg += abs(delta)
                            last_heading_deg = heading_deg
                elif mission.current_state != RobotState.ROUNDABOUT_CIRCULATE:
                    last_heading_deg = None
                    roundabout_heading_accum_deg = 0.0

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
                    if mission.current_state != RobotState.IDLE:
                        duck_resume_state = mission.current_state
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
                if duck_resume_state is not None:
                    mission.current_state = duck_resume_state
                    duck_resume_state = None
                else:
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
                    or mission.current_state == RobotState.LEFT_2 or mission.current_state == RobotState.RIGHT
                    or mission.current_state == RobotState.ROUNDABOUT_ENTRY):
                stop_line_trigger_mode = str(getattr(config, "STOP_LINE_TRIGGER_MODE", "grayscale")).strip().lower()
                no_line_trigger_mode = str(getattr(config, "NO_LINE_TRIGGER_MODE", "either")).strip().lower()
                if stop_line_trigger_mode == "camera" or no_line_trigger_mode == "camera":
                    px.set_cam_tilt_angle(0)
                print("Approaching STOP LINE...")
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

                no_line_trigger_mode = str(getattr(config, "NO_LINE_TRIGGER_MODE", "either")).strip().lower()
                trigger_hit = _turn_triggered(
                    no_line_trigger_mode,
                    grayscale_turn_triggered,
                    line_distance_cm,
                    config.MAX_TURN_PROXIMITY,
                )
                timed_out = (time.time() - no_line_arm_time) > config.NO_LINE_TIMEOUT
                should_turn = (
                    turn_dir is not None
                    and (trigger_hit or timed_out)
                )

                if should_turn:
                    px.set_cam_tilt_angle(-30)
                    no_line_turn = False
                    execution_mode = _normalized_turn_mode()
                    # Preserve backward compatibility for legacy no-line mode setting.
                    legacy_no_line_mode = str(getattr(config, "NO_LINE_TURN_MODE", "")).strip().lower()
                    if legacy_no_line_mode in ("camera", "pivot") and not getattr(config, "TURN_EXECUTION_MODE", ""):
                        execution_mode = "trajectory" if legacy_no_line_mode == "camera" else "pivot"

                    print(
                        "No-stop-line turn armed "
                        f"(trigger_mode={no_line_trigger_mode}, trigger_hit={trigger_hit}, timeout={timed_out}, "
                        f"distance_to_line={line_distance_cm})."
                    )
                    print(f"Executing no-stop-line {execution_mode} turn: {turn_dir}")
                    success, current_motor_speed, stopped = _execute_turn_by_mode(
                        px,
                        eyes,
                        turn_dir,
                        pid,
                        mission,
                        server,
                        current_motor_speed,
                        stopped,
                        execution_mode,
                    )

                    if success:
                        no_line_turn = False
                        mission.advance_mission()
                    continue
            
            px.set_cam_tilt_angle(0)
            # Line Lost Failsafe
            if not eyes.last_line_seen:
                if (time.time() - last_valid_line_time) > config.LOST_LINE_TIMEOUT:
                    print(f"!!! FAILSAFE: Line lost for > {config.LOST_LINE_TIMEOUT}s !!!")
                    stop_flag = True
                    break
            else:
                last_valid_line_time = time.time()

            if mission.current_state == RobotState.ROUNDABOUT_CIRCULATE:
                circulate_elapsed = 0.0
                if roundabout_circulate_start_time is not None:
                    circulate_elapsed = time.time() - roundabout_circulate_start_time

                if roundabout_exit_mode == "line":
                    line_triggered = full_cross_triggered
                    if line_distance_cm is not None:
                        line_triggered = line_triggered or (
                            line_distance_cm <= config.ROUNDABOUT_EXIT_LINE_DISTANCE_CM
                        )

                    if circulate_elapsed >= config.ROUNDABOUT_EXIT_MIN_CIRCULATE_TIME and line_triggered:
                        print(
                            "Roundabout exit prep trigger: line detected "
                            f"(full_cross_triggered={full_cross_triggered}, distance_cm={line_distance_cm})"
                        )
                        mission.advance_mission()
                        continue
                elif roundabout_exit_mode == "heading":
                    if roundabout_heading_accum_deg >= config.ROUNDABOUT_EXIT_ACCUM_HEADING_DEG:
                        print(
                            f"Roundabout exit prep trigger: accumulated heading {roundabout_heading_accum_deg:.1f}deg"
                        )
                        mission.advance_mission()
                        continue
                else:
                    print(f"Unknown ROUNDABOUT_EXIT_TRIGGER_MODE='{roundabout_exit_mode}', expected 'line' or 'heading'.")

            if mission.current_state == RobotState.ROUNDABOUT_EXIT_PREP:
                turn_dir = str(getattr(config, "ROUNDABOUT_EXIT_DIRECTION", "right")).strip().lower()
                if turn_dir not in ("left", "right"):
                    turn_dir = "right"

                if bool(getattr(config, "ROUNDABOUT_EXIT_USE_BRANCH_TRIGGER", True)):
                    if roundabout_exit_search_start_time is None:
                        roundabout_exit_search_start_time = time.time()

                    px.set_cam_tilt_angle(-30)
                    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)
                    search_speed = max(0, int(getattr(config, "ROUNDABOUT_EXIT_SEARCH_SPEED", config.TURN_ENTRY_SPEED)))
                    px.forward(search_speed)
                    current_motor_speed = search_speed
                    stopped = False

                    center_threshold = float(
                        getattr(config, "ROUNDABOUT_EXIT_CENTER_THRESHOLD", eyes.LOGIC_DETECT)
                    )
                    center_signal = eyes.color_signal(raw[1], 1)
                    center_active = center_signal > center_threshold
                    left_active, _, right_active = eyes.active_sensor_mask(raw)
                    if turn_dir == "right":
                        branch_detected = center_active and right_active
                    else:
                        branch_detected = left_active and center_active

                    if branch_detected:
                        roundabout_exit_branch_hits += 1
                    else:
                        roundabout_exit_branch_hits = 0

                    if roundabout_exit_branch_hits >= int(getattr(config, "ROUNDABOUT_EXIT_BRANCH_HITS", 3)):
                        print(
                            f"Roundabout branch cue detected ({turn_dir}, hits={roundabout_exit_branch_hits}); executing pivot turn."
                        )
                        success, current_motor_speed, stopped = execute_pivot_turn(
                            px,
                            eyes,
                            turn_dir,
                            pid,
                            mission,
                            current_motor_speed,
                            stopped,
                        )
                        roundabout_exit_search_start_time = None
                        roundabout_exit_branch_hits = 0
                    else:
                        elapsed_search = time.time() - roundabout_exit_search_start_time
                        timeout_s = float(getattr(config, "ROUNDABOUT_EXIT_SEARCH_TIMEOUT", 3.0))
                        if elapsed_search >= timeout_s:
                            print(
                                f"Roundabout branch cue timeout ({elapsed_search:.2f}s); forcing pivot {turn_dir} exit."
                            )
                            success, current_motor_speed, stopped = execute_pivot_turn(
                                px,
                                eyes,
                                turn_dir,
                                pid,
                                mission,
                                current_motor_speed,
                                stopped,
                            )
                            roundabout_exit_search_start_time = None
                            roundabout_exit_branch_hits = 0
                        else:
                            continue
                else:
                    execution_mode = _normalized_turn_mode()
                    success, current_motor_speed, stopped = _execute_turn_by_mode(
                        px,
                        eyes,
                        turn_dir,
                        pid,
                        mission,
                        server,
                        current_motor_speed,
                        stopped,
                        execution_mode,
                    )

                if success:
                    mission.advance_mission()
                continue

            if mission.current_state == RobotState.ROUNDABOUT_EXIT_COMMIT:
                ignore_intersection(px, config.TURN_POST_SPEED)
                mission.advance_mission()
                continue

            if full_cross_triggered and not no_line_turn:
                if mission.current_state == RobotState.STRAIGHT:
                    startup_guard_s = float(getattr(config, "STARTUP_INTERSECTION_GUARD_SEC", 0.8))
                    startup_guard_active = (time.time() - start_time) < startup_guard_s
                    if not startup_guard_active:
                        print("Ignoring full intersection (STRAIGHT mode).")
                        ignore_intersection(px, base_speed)
                        continue
                elif mission.current_state == RobotState.APPROACH_STOP:
                    print("STOP LINE reached.")
                    stop_at_line(px, base_speed)
                    continue
                elif mission.current_state == RobotState.ROUNDABOUT_ENTRY:
                    print("ROUNDABOUT ENTRY stop line reached.")
                    stop_at_line(px, base_speed)

                    if bool(getattr(config, "ROUNDABOUT_ENTRY_PIVOT_ENABLE", True)):
                        entry_dir = str(getattr(config, "ROUNDABOUT_ENTRY_PIVOT_DIRECTION", "right")).strip().lower()
                        if entry_dir not in ("left", "right"):
                            entry_dir = "right"
                        entry_pwm = int(getattr(config, "ROUNDABOUT_ENTRY_PIVOT_PWM", config.PIVOT_TURN_PWM))
                        entry_duration = float(getattr(config, "ROUNDABOUT_ENTRY_PIVOT_DURATION", 0.35))
                        print(
                            f"Applying roundabout entry pivot nudge ({entry_dir}, pwm={entry_pwm}, t={entry_duration:.2f}s)."
                        )
                        _roundabout_entry_pivot_nudge(px, entry_dir, entry_pwm, entry_duration)

                    mission.advance_mission()
                    continue
                elif mission.current_state == RobotState.LEFT_1:
                    execution_mode = _normalized_turn_mode()
                    success, current_motor_speed, stopped = _execute_turn_by_mode(
                        px,
                        eyes,
                        "left",
                        pid,
                        mission,
                        server,
                        current_motor_speed,
                        stopped,
                        execution_mode,
                    )
                    if success:
                        no_line_turn = False
                        mission.advance_mission()
                    continue
                elif mission.current_state == RobotState.LEFT_2:
                    if not full_cross_triggered:
                        continue

                    mission.crossings_seen += 1
                    if mission.crossings_seen >= 2:  # +1 more to account for the stop line
                        execution_mode = _normalized_turn_mode()
                        success, current_motor_speed, stopped = _execute_turn_by_mode(
                            px,
                            eyes,
                            "left",
                            pid,
                            mission,
                            server,
                            current_motor_speed,
                            stopped,
                            execution_mode,
                        )
                        if success:
                            no_line_turn = False
                            mission.advance_mission()
                    else:
                        print(f"Skipping intersection {mission.crossings_seen}/2")
                        ignore_intersection(px, base_speed)
                    continue
                elif mission.current_state == RobotState.RIGHT:
                    if not full_cross_triggered:
                        continue

                    mission.crossings_seen += 1
                    if mission.crossings_seen >= 2:
                        execution_mode = _normalized_turn_mode()
                        success, current_motor_speed, stopped = _execute_turn_by_mode(
                            px,
                            eyes,
                            "right",
                            pid,
                            mission,
                            server,
                            current_motor_speed,
                            stopped,
                            execution_mode,
                        )
                        if success:
                            no_line_turn = False
                            mission.advance_mission()
                    else:
                        print(f"Skipping intersection {mission.crossings_seen}/2")
                        ignore_intersection(px, base_speed)
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
            # Add extra steering authority only in sharp curves to reduce understeer.
            abs_error = abs(smooth_error)
            boost_threshold = float(getattr(config, "CURVE_STEER_BOOST_THRESHOLD", 22.0))
            boost_gain = float(getattr(config, "CURVE_STEER_BOOST_GAIN", 0.75))
            boost_max = float(getattr(config, "CURVE_STEER_BOOST_MAX", 1.7))
            if abs_error > boost_threshold:
                normalized_excess = (abs_error - boost_threshold) / 100.0
                boost = 1.0 + boost_gain * normalized_excess
                boost = min(boost, boost_max)
                steering *= boost
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
