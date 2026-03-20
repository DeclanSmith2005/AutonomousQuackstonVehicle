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
from io_components import IOComponents

# --- GLOBALS ---
stop_flag = False
current_motor_speed = 0
force_line_lost = False
run_calibration_flag = False
no_line_turn = False
stopped = False
no_line_arm_time = 0.0
io_components = None
emergency_stop_active = False


def _signed_heading_delta_deg(new_heading_deg, old_heading_deg):
    """Return wrapped heading delta in degrees in [-180, 180]."""
    return ((new_heading_deg - old_heading_deg + 180.0) % 360.0) - 180.0


def _normalized_turn_mode():
    """
    Determine the turn execution mode, prioritizing the new 
    TURN_EXECUTION_MODE config while maintaining backward compatibility.
    """
    mode = str(config.TURN_EXECUTION_MODE).strip().lower()
    if mode in ("trajectory", "pivot", "classic"):
        return mode

    # Legacy fallback: check boolean flags if mode is not set
    if bool(config.TURN_USE_CAMERA):
        return "trajectory"
    if bool(config.TURN_USE_PIVOT):
        return "pivot"
    return "classic"


def _turn_triggered(mode, grayscale_triggered, camera_distance_cm, threshold_cm):
    """
    Evaluate if a turn should be triggered based on sensor inputs 
    and the configured trigger mode (grayscale, camera, or either).
    """
    camera_triggered = camera_distance_cm is not None and camera_distance_cm <= threshold_cm
    trigger_mode = str(mode).strip().lower()
    if trigger_mode == "grayscale":
        return bool(grayscale_triggered)
    if trigger_mode == "camera":
        return bool(camera_triggered)
    return bool(grayscale_triggered or camera_triggered)


def _execute_turn_by_mode(px, eyes, direction, pid, mission, server, current_speed, is_stopped, mode):
    """
    Unified entry point for turn execution. Dispatches to the 
    appropriate turn handler based on the selected mode.
    """
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

    # Default to classic timed turn
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
    e: emergency stop (halts processes until 's' is pressed)
    s: start / resume from emergency stop
    q: quit
    st/a/l1/l2/r/idle/cal: manually jump to state
    n: next mission stage
    reset: reset mission
    fl: toggle forced line lost (simulates sensor failure)
    wiggle: run wiggle calibration
    """
    global stop_flag, force_line_lost, run_calibration_flag, no_line_turn, no_line_arm_time, emergency_stop_active
    print("Keyboard listener active.")
    print("Commands: e=e-stop, s=start/resume, q=quit, st=straight, a=approach_stop, l1/l2=left, r=right, idle=idle, cal=calibrate")
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

            if cmd == "q":
                stop_flag = True
            elif cmd == "e":
                emergency_stop_active = True
                print("EMERGENCY STOP ACTIVE. Press 's' to resume.")
            elif cmd == "s":
                emergency_stop_active = False
                print("Resuming from emergency stop.")
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
    global current_motor_speed, io_components
    time.sleep(config.STOP_DELAY)
    px.stop()
    current_motor_speed = 0
    if io_components:
        io_components.update_brakes(current_motor_speed)
    time.sleep(config.STOP_HOLD_TIME)
    # Clear the line
    px.forward(base_speed)
    current_motor_speed = base_speed
    if io_components:
        io_components.update_brakes(current_motor_speed)
    time.sleep(config.STOP_CLEAR_TIME)

def main():
    global stop_flag, current_motor_speed, force_line_lost, run_calibration_flag, no_line_turn, stopped, no_line_arm_time, emergency_stop_active

    global io_components
    # --- SENSORS & ACTUATORS ---
    px = Picarx()
    eyes = LineSensor(config.OFFSETS)
    pid = PIDController(config.KP, config.KI, config.KD, min_out=-config.MAX_STEER, max_out=config.MAX_STEER)
    io_components = IOComponents()

    # --- MISSION ---
    # Current active mission
    initial_mission = [
        RobotState.STRAIGHT,
        RobotState.LEFT_2,
        RobotState.STRAIGHT,
        RobotState.LEFT_2,
        RobotState.STRAIGHT,
        RobotState.RIGHT,
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
    def _turn_allowed():
        """Return True when startup grace period (1s) has elapsed."""
        return (time.time() - start_time) >= 1.0
    last_valid_line_time = time.time()
    last_pid_time = time.time()
    no_line_arm_time = 0.0
    last_heading_deg = None
    roundabout_heading_accum_deg = 0.0
    previous_state = mission.current_state
    roundabout_circulate_start_time = None
    roundabout_exit_search_start_time = None
    roundabout_exit_branch_hits = 0
    camera_tilt_cmd_deg = 0.0
    straight_cross_streak = 0
    last_straight_intersection_time = 0.0
    idle_limit_pressed_time = 0.0

    def _set_cam_tilt(angle_deg):
        """Set camera tilt and keep local command state for behavior gating."""
        nonlocal camera_tilt_cmd_deg
        px.set_cam_tilt_angle(angle_deg)
        camera_tilt_cmd_deg = float(angle_deg)

    def _handle_duck_override():
        """Apply duck-stop safety behavior. Return True when the loop should continue early."""
        nonlocal duck_stop_active, duck_resume_state, last_pid_time, last_valid_line_time
        global current_motor_speed, stopped

        duck_detection_enabled = abs(camera_tilt_cmd_deg) < 0.5
        duck_visible = server.receive_duck_visible() if duck_detection_enabled else False
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
                if io_components:
                    io_components.update_brakes(0)
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
            return True

        if duck_stop_active:
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

        return False

    def _roundabout_exit_trigger_line(circulate_elapsed, full_cross_triggered, line_distance_cm):
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
            return True
        return False

    def _roundabout_exit_trigger_heading(roundabout_heading_accum_deg):
        if roundabout_heading_accum_deg >= config.ROUNDABOUT_EXIT_ACCUM_HEADING_DEG:
            print(
                f"Roundabout exit prep trigger: accumulated heading {roundabout_heading_accum_deg:.1f}deg"
            )
            mission.advance_mission()
            return True
        return False

    def _handle_roundabout_circulate(roundabout_exit_mode, full_cross_triggered, line_distance_cm, roundabout_heading_accum_deg):
        if mission.current_state != RobotState.ROUNDABOUT_CIRCULATE:
            return False

        circulate_elapsed = 0.0
        if roundabout_circulate_start_time is not None:
            circulate_elapsed = time.time() - roundabout_circulate_start_time

        mode_handlers = {
            "line": lambda: _roundabout_exit_trigger_line(circulate_elapsed, full_cross_triggered, line_distance_cm),
            "heading": lambda: _roundabout_exit_trigger_heading(roundabout_heading_accum_deg),
        }
        handler = mode_handlers.get(roundabout_exit_mode)
        if handler is None:
            print(f"Unknown ROUNDABOUT_EXIT_TRIGGER_MODE='{roundabout_exit_mode}', expected 'line' or 'heading'.")
            return False

        return bool(handler())

    def _intersection_straight(base_speed, start_time):
        nonlocal straight_cross_streak, last_straight_intersection_time
        startup_guard_s = float(config.STARTUP_INTERSECTION_GUARD_SEC)
        startup_guard_active = (time.time() - start_time) < startup_guard_s
        if not startup_guard_active:
            print("Ignoring full intersection (STRAIGHT mode).")
            ignore_intersection(px, base_speed)
            last_straight_intersection_time = time.time()
            straight_cross_streak = 0
            mission.advance_mission()
            return True
        return False

    def _intersection_approach_stop(base_speed, _start_time):
        print("STOP LINE reached.")
        stop_at_line(px, base_speed)
        return True

    def _intersection_roundabout_entry(base_speed, _start_time):
        print("ROUNDABOUT ENTRY stop line reached.")
        stop_at_line(px, base_speed)

        if bool(config.ROUNDABOUT_ENTRY_PIVOT_ENABLE):
            entry_dir = str(config.ROUNDABOUT_ENTRY_PIVOT_DIRECTION).strip().lower()
            if entry_dir not in ("left", "right"):
                entry_dir = "right"
            entry_pwm = int(config.ROUNDABOUT_ENTRY_PIVOT_PWM)
            entry_duration = float(config.ROUNDABOUT_ENTRY_PIVOT_DURATION)
            print(
                f"Applying roundabout entry pivot nudge ({entry_dir}, pwm={entry_pwm}, t={entry_duration:.2f}s)."
            )
            _roundabout_entry_pivot_nudge(px, entry_dir, entry_pwm, entry_duration)

        mission.advance_mission()
        return True

    def _intersection_left_1(_base_speed, _start_time):
        global no_line_turn, current_motor_speed, stopped

        if not _turn_allowed():
            print("Turn suppressed during startup grace period.")
            return False

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
        return True

    def _intersection_left_2(base_speed, _start_time):
        global no_line_turn, current_motor_speed, stopped

        mission.crossings_seen += 1
        if mission.crossings_seen >= 2:  # +1 more to account for the stop line
            if not _turn_allowed():
                print("Turn suppressed during startup grace period.")
                return False

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
        return True

    def _intersection_right(base_speed, _start_time):
        global no_line_turn, current_motor_speed, stopped

        if not _turn_allowed():
            print("Turn suppressed during startup grace period.")
            return False
    
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

        return True

    def _handle_intersection_event(base_speed, start_time, full_cross_triggered):
        if no_line_turn:
            return False

        intersection_triggered = full_cross_triggered
        if mission.current_state == RobotState.STRAIGHT:
            required_frames = max(1, int(getattr(config, "STRAIGHT_INTERSECTION_DEBOUNCE_FRAMES", 3)))
            cooldown_s = max(0.0, float(getattr(config, "STRAIGHT_INTERSECTION_COOLDOWN_S", 0.8)))
            in_cooldown = (time.time() - last_straight_intersection_time) < cooldown_s
            intersection_triggered = full_cross_triggered and (straight_cross_streak >= required_frames) and not in_cooldown

        if not intersection_triggered:
            return False

        state_handlers = {
            RobotState.STRAIGHT: _intersection_straight,
            RobotState.APPROACH_STOP: _intersection_approach_stop,
            RobotState.ROUNDABOUT_ENTRY: _intersection_roundabout_entry,
            RobotState.LEFT_1: _intersection_left_1,
            RobotState.LEFT_2: _intersection_left_2,
            RobotState.RIGHT: _intersection_right,
        }
        handler = state_handlers.get(mission.current_state)
        if handler is None:
            return False
        return bool(handler(base_speed, start_time))

    def _handle_no_line_turn(grayscale_turn_triggered, line_distance_cm):
        global no_line_turn, no_line_arm_time, current_motor_speed, stopped

        if not no_line_turn:
            return False

        if not _turn_allowed():
            print("Turn suppressed during startup grace period.")
            return False

        if mission.current_state in (RobotState.LEFT_1, RobotState.LEFT_2):
            turn_dir = "left"
        elif mission.current_state == RobotState.RIGHT:
            turn_dir = "right"
        else:
            turn_dir = None

        no_line_time = time.time()
        turn_trigger_mode = str(config.TURN_TRIGGER_MODE).strip().lower()

        trigger_hit = _turn_triggered(
                        turn_trigger_mode,
                        grayscale_turn_triggered,
                        line_distance_cm,
                        config.MAX_TURN_PROXIMITY,
                    )

        while (time.time() - no_line_time) < config.NO_LINE_TIMEOUT:
            line_distance_cm = server.receive_intersection_distance()
            print(line_distance_cm)
            trigger_hit = _turn_triggered(
                        turn_trigger_mode,
                        grayscale_turn_triggered,
                        line_distance_cm,
                        config.MAX_TURN_PROXIMITY,
                    )
            if trigger_hit:
                break
            # time.sleep(0.1)
        
        # timed_out = (time.time() - no_line_arm_time) > config.NO_LINE_TIMEOUT
        should_turn = (
            turn_dir is not None
            and (trigger_hit)
        )

        if not should_turn:
            return False

        no_line_turn = False
        _set_cam_tilt(-30)        
        execution_mode = _normalized_turn_mode()
        # Preserve backward compatibility for legacy no-line mode setting.
        legacy_no_line_mode = str(config.NO_LINE_TURN_MODE).strip().lower()
        if legacy_no_line_mode in ("camera", "pivot") and not config.TURN_EXECUTION_MODE:
            execution_mode = "trajectory" if legacy_no_line_mode == "camera" else "pivot"

        print(
            "No-stop-line turn armed "
            f"(trigger_mode={turn_trigger_mode}, trigger_hit={trigger_hit}, timeout=, "
            f"distance_to_line={line_distance_cm})."
        )

        # If camera-provided distance is available, print a clear, formatted message.
        if line_distance_cm is not None:
            try:
                print(f"  [Camera] distance to line: {float(line_distance_cm):.1f} cm")
            except Exception:
                print(f"  [Camera] distance to line: {line_distance_cm}")
                print(f"Executing no-stop-line {execution_mode} turn: {turn_dir}")
        else:
            if turn_trigger_mode == "camera":
                print("  [Camera] distance to line: <no reading>")

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
        return True

    def _handle_roundabout_exit_prep(raw):
        nonlocal roundabout_exit_search_start_time, roundabout_exit_branch_hits
        global current_motor_speed, stopped

        if mission.current_state != RobotState.ROUNDABOUT_EXIT_PREP:
            return False

        turn_dir = str(config.ROUNDABOUT_EXIT_DIRECTION).strip().lower()
        if turn_dir not in ("left", "right"):
            turn_dir = "right"

        if bool(config.ROUNDABOUT_EXIT_USE_BRANCH_TRIGGER):
            if roundabout_exit_search_start_time is None:
                roundabout_exit_search_start_time = time.time()

            _set_cam_tilt(-30)
            px.set_dir_servo_angle(config.STRAIGHT_ANGLE)
            search_speed = max(0, int(config.ROUNDABOUT_EXIT_SEARCH_SPEED))
            px.forward(search_speed)
            current_motor_speed = search_speed
            stopped = False

            center_threshold = float(config.ROUNDABOUT_EXIT_CENTER_THRESHOLD)
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

            if roundabout_exit_branch_hits >= int(config.ROUNDABOUT_EXIT_BRANCH_HITS):
                print(
                    f"Roundabout branch cue detected ({turn_dir}, hits={roundabout_exit_branch_hits}); executing pivot turn."
                )
                if not _turn_allowed():
                    print("Roundabout pivot suppressed during startup grace period.")
                    return True

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
                timeout_s = float(config.ROUNDABOUT_EXIT_SEARCH_TIMEOUT)
                if elapsed_search >= timeout_s:
                    print(
                        f"Roundabout branch cue timeout ({elapsed_search:.2f}s); forcing pivot {turn_dir} exit."
                    )
                    if not _turn_allowed():
                        print("Roundabout pivot suppressed during startup grace period.")
                        return True
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
                    return True
        else:
            if not _turn_allowed():
                print("Roundabout pivot suppressed during startup grace period.")
                return True
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
        return True

    def _handle_roundabout_exit_commit():
        if mission.current_state != RobotState.ROUNDABOUT_EXIT_COMMIT:
            return False

        ignore_intersection(px, config.TURN_POST_SPEED)
        mission.advance_mission()
        return True

    def _update_state_transition_trackers(roundabout_exit_mode):
        nonlocal previous_state
        nonlocal roundabout_circulate_start_time
        nonlocal last_heading_deg
        nonlocal roundabout_heading_accum_deg
        nonlocal roundabout_exit_search_start_time
        nonlocal roundabout_exit_branch_hits

        if mission.current_state == previous_state:
            return

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

    def _update_roundabout_heading_accum(roundabout_exit_mode, localization):
        nonlocal last_heading_deg, roundabout_heading_accum_deg

        if roundabout_exit_mode != "heading":
            return

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

    def _handle_state_prechecks(raw, pattern):
        global current_motor_speed, stopped, io_components
        nonlocal idle_limit_pressed_time

        if mission.current_state == RobotState.IDLE:
            px.stop()
            current_motor_speed = 0
            stopped = True
            
            if io_components.is_limit_switch_pressed():
                if idle_limit_pressed_time == 0.0:
                    print("Limit switch pressed! Waiting 5s before advancing from IDLE...")
                    idle_limit_pressed_time = time.time()
                elif (time.time() - idle_limit_pressed_time) >= 5.0:
                    io_components.clear_limit_switch_flag()
                    idle_limit_pressed_time = 0.0
                    mission.request_step()
            else:
                idle_limit_pressed_time = 0.0

            time.sleep(0.5)
            return True

        if mission.current_state == RobotState.CALIBRATE:
            print(f"RAW: {raw} | PATTERN: {pattern}")
            time.sleep(0.5)
            return True

        # In states leading up to a turn or stop line, reduce speed.
        if mission.current_state in (
            RobotState.APPROACH_STOP,
            RobotState.LEFT_1,
            RobotState.LEFT_2,
            RobotState.RIGHT,
            RobotState.ROUNDABOUT_ENTRY,
        ):
            turn_trigger_mode = str(config.TURN_TRIGGER_MODE).strip().lower()
            if turn_trigger_mode == "camera":
                _set_cam_tilt(0)
            print("Approaching STOP LINE...")
            px.forward(config.TURN_ENTRY_SPEED)
            current_motor_speed = config.TURN_ENTRY_SPEED

        return False

    try:
        while not stop_flag:
            loop_start = time.time()
            
            # Process all incoming ZMQ messages once per loop
            server.process_incoming_messages()

            if emergency_stop_active:
                px.stop()
                current_motor_speed = 0
                stopped = True
                if io_components:
                    io_components.update_brakes(0)
                    io_components.signal_hazard()
                time.sleep(0.05)
                continue

            # Check for calibration request
            if run_calibration_flag:
                run_calibration_flag = False
                run_wiggle_calibration(px, eyes)
                continue

            # Evaluate Turn Signals
            if mission.current_state in (RobotState.LEFT_1, RobotState.LEFT_2) or \
               (mission.current_state == RobotState.APPROACH_STOP and len(mission.mission_queue) > 0 and mission.mission_queue[0] in (RobotState.LEFT_1, RobotState.LEFT_2)):
                io_components.signal_left()
            elif mission.current_state == RobotState.RIGHT or \
                 (mission.current_state == RobotState.APPROACH_STOP and len(mission.mission_queue) > 0 and mission.mission_queue[0] == RobotState.RIGHT):
                io_components.signal_right()
            else:
                io_components.signal_off()
                
            # Evaluate Brake Lights dynamically
            if io_components:
                io_components.update_brakes(current_motor_speed)

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
            error, _ = eyes.compute_error(raw)
            base_speed = config.BASE_SPEED

            if not error_buffer_seeded and eyes.last_line_seen:
                error_buffer = [error] * max(1, config.ERROR_BUFFER_LEN)
                error_buffer_seeded = True

            full_cross_triggered = pattern == "CROSS"
            grayscale_turn_triggered = full_cross_triggered

            if mission.current_state == RobotState.STRAIGHT and full_cross_triggered:
                straight_cross_streak += 1
            elif not full_cross_triggered:
                straight_cross_streak = 0

            # Determine how we will exit the roundabout this run
            roundabout_exit_mode = str(config.ROUNDABOUT_EXIT_TRIGGER_MODE).strip().lower()

            # Update transition-dependent timers and heading tracking state.
            _update_state_transition_trackers(roundabout_exit_mode)
            _update_roundabout_heading_accum(roundabout_exit_mode, localization)

            # 3) Handle Mission Stages
            latest_queue = server.receive_mission_queue()
            if latest_queue is not None:
                print(f"Received new mission queue from pathing: {latest_queue}")
                # Override the mission queue with pathing's fresh instructions
                # If no queue is received, the default 'initial_mission' remains unaffected
                mission.mission_queue = list(latest_queue)

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
            # if _handle_duck_override():
            #     continue

            # 4) State-machine prechecks (idle/calibrate/approach behavior)
            if _handle_state_prechecks(raw, pattern):
                continue

            # No-stop-line mode: arm and execute the pending turn when trigger/timeout occurs.
            if _handle_no_line_turn(grayscale_turn_triggered, line_distance_cm):
                continue
            
            _set_cam_tilt(0)
            # Line Lost Failsafe
            if not eyes.last_line_seen:
                if (time.time() - last_valid_line_time) > config.LOST_LINE_TIMEOUT:
                    print(f"!!! FAILSAFE: Line lost for > {config.LOST_LINE_TIMEOUT}s !!!")
                    stop_flag = True
                    break
            else:
                last_valid_line_time = time.time()

            if _handle_roundabout_circulate(
                roundabout_exit_mode,
                full_cross_triggered,
                line_distance_cm,
                roundabout_heading_accum_deg,
            ):
                continue

            if _handle_roundabout_exit_prep(raw):
                continue

            if _handle_roundabout_exit_commit():
                continue

            # 5) Handle intersections (event dispatch by current mission state)
            if _handle_intersection_event(base_speed, start_time, full_cross_triggered):
                continue
                    
            # 6) PID CONTROL
            current_time = time.time()
            dt = current_time - last_pid_time
            last_pid_time = current_time

            # Compute smoothed error using moving average to avoid spiky reading
            error_buffer.append(error)
            error_buffer.pop(0)
            smooth_error = sum(error_buffer) / len(error_buffer)

            # Shift PID target toward an edge while approaching turn states.
            target_error = 0.0
            if mission.current_state in (RobotState.LEFT_1, RobotState.LEFT_2):
                target_error = float(config.EDGE_OFFSET_LEFT_TURN)
            elif mission.current_state == RobotState.RIGHT:
                target_error = float(config.EDGE_OFFSET_RIGHT_TURN)

            tracking_error = target_error - smooth_error

            # Apply deadband to tracking error, not raw line error.
            if abs(tracking_error) < config.DEADBAND:
                tracking_error = 0.0

            # Calculate steering adjustment from the PID controller
            steering = pid.update(tracking_error, dt=dt)
            # Add extra steering authority only in sharp curves to reduce understeer.
            abs_error = abs(tracking_error)
            boost_threshold = float(config.CURVE_STEER_BOOST_THRESHOLD)
            boost_gain = float(config.CURVE_STEER_BOOST_GAIN)
            boost_max = float(config.CURVE_STEER_BOOST_MAX)
            if abs_error > boost_threshold:
                normalized_excess = (abs_error - boost_threshold) / 100.0
                boost = 1.0 + boost_gain * normalized_excess
                boost = min(boost, boost_max)
                steering *= boost
            steering = max(-config.MAX_STEER, min(config.MAX_STEER, steering))

            # Dynamically reduce speed based on severity of the turn to maintain stability
            speed_drop = abs(steering) * config.SPEED_DROP_GAIN
            current_speed = max(base_speed - speed_drop, config.MIN_DRIVE_SPEED)

            # Transmit commands to the motors and steering servo
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
        if io_components:
            io_components.signal_off()
            io_components.brake_off()
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
