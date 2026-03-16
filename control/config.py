KP = 0.25
KI = 0.0
KD = 0.008
ERROR_BUFFER_LEN = 5
DEADBAND = 5.0

# --- MOTION PARAMETERS ---
BASE_SPEED = 6
MAX_STEER = 30
LOOP_INTERVAL = 0.01  # Main loop period (s), target 100 Hz update rate.
STRAIGHT_ANGLE = 0
MIN_DRIVE_SPEED = 8
SPEED_DROP_GAIN = 0.25  # Reduce speed as steering angle grows.
SPEED_RAMP_RATE = 2.0
CURVE_STEER_BOOST_THRESHOLD = 20.0 # Error magnitude where extra steering authority begins.
CURVE_STEER_BOOST_GAIN = 0.75  # Higher = tighter response on hard curves.
CURVE_STEER_BOOST_MAX = 1.7  # Cap on multiplicative steering boost in sharp curves.

# --- APPROACH & STOP TUNING ---
APPROACH_SPEED = 6
TURN_PWM = 5
STOP_HOLD_TIME = 2.0
STOP_CLEAR_TIME = 0.5
STOP_DELAY = 0.25

# --- TURN TUNING ---
TURN_TIME = 2.0
PASS_TIME = 0.5
TURN_BLIND_TIME = 0.5
TURN_SCAN_TIMEOUT = 5.0
TURN_SCAN_INTERVAL = 0.01
TURN_RECOVERY_PWM = 8
TURN_ANGLE = 31
TURN_STABILIZE_TIME = 0.1
TURN_ENTRY_TIMEOUT = 5.0
TURN_ENTRY_SPEED = 1
TURN_POST_SPEED = 5
TURN_STOP_HOLD_TIME = 3.0
MAX_TURN_PROXIMITY = 10 # in cm

# --- CAMERA-GUIDED TURN TUNING (Snapshot-based) ---
TURN_USE_CAMERA = True           # Enable camera-guided turns (set False to use old blind turn)
TURN_USE_PIVOT = False           # Enable in-place pivot turn using per-motor control when TURN_USE_CAMERA=False
TURN_EXECUTION_MODE = "pivot"  # "trajectory", "pivot", or "classic" for all turn states.
STOP_LINE_TRIGGER_MODE = "either"  # "grayscale", "camera", or "either" for stop-line turn triggers.
SNAPSHOT_WAIT_TIMEOUT = 1.0      # Max time to wait for trajectory snapshot (s)
WHEELBASE_CM = 9.5               # Wheelbase length for bicycle model (cm)
TURN_LOOKAHEAD_MIN_CM = 25.0     # Minimum y_ref used by bicycle model to avoid steering saturation
TURN_CAMERA_TIMEOUT = 3.0        # Max turn duration before fallback (s)
TURN_INITIAL_ROTATION_TIME = 0.3 # Brief initial rotation to point toward exit lane
TURN_PROFILE_DURATION = 1.0     # Time to walk through the captured turn profile (s)
TURN_MIN_LINE_CHECK_TIME = 1.0   # Delay before grayscale can end the turn (s)
TRAJECTORY_TIMEOUT = 0.3         # Freshness window for trajectory points (s)
INTERSECTION_DISTANCE_TIMEOUT = 0.4  # Freshness window for distance_line (s)
TURN_TRAJECTORY_CAMERA_TILT_DOWN = -30  # Camera tilt angle before capturing trajectory.
TURN_FEEDFORWARD_GAIN = 1.0      # Base gain on bicycle-model steering command
TURN_CTE_FEEDBACK_GAIN = 0.45    # Deg per cm of live CTE tracking error
TURN_HEADING_FEEDBACK_GAIN = 0.55  # Gain on heading error inferred from trajectory slope
TURN_STEER_SMOOTHING_ALPHA = 0.30  # Command low-pass: 0=no update, 1=no smoothing

# --- PIVOT TURN TUNING ---
PIVOT_TURN_PWM = 7               # PWM used for in-place pivot turning (0-100)
PIVOT_SCAN_TIMEOUT = 2.5         # Max pivot duration before declaring turn failure (s)
PIVOT_MAX_PRE_SCAN_TIME = 1.0    # Hard cap on pivoting before switching to forward scan/reacquisition.
PIVOT_REQUIRE_LINE_SEQUENCE = True  # If True, keep pivoting until grayscale sequence is detected.
PIVOT_FORWARD_SETTLE_TIME = 0.3  # Time to drive forward before starting line reacquisition.
NO_LINE_TURN_MODE = "camera"      # Legacy no-line turn mode. Prefer TURN_EXECUTION_MODE.
NO_LINE_TRIGGER_MODE = "either"    # "grayscale", "camera", or "either" for no-line turn arming.
NO_LINE_TIMEOUT = 2.5             # Max creep time waiting for no-line turn trigger before forcing turn.
PIVOT_ALIGN_ENABLE = True
PIVOT_ALIGN_MIN_TIME = 0.25      # Minimum pivot time before line-alignment checks can end the turn
PIVOT_ALIGN_MIN_HITS = 2         # Consecutive alignment detections required to finish pivot
PIVOT_ALIGN_SENSOR_THRESHOLD = 0.72

# --- ROUNDABOUT ENTRY PIVOT NUDGE ---
ROUNDABOUT_ENTRY_PIVOT_ENABLE = True
ROUNDABOUT_ENTRY_PIVOT_DIRECTION = "right"  # "left" or "right"
ROUNDABOUT_ENTRY_PIVOT_PWM = 6
ROUNDABOUT_ENTRY_PIVOT_DURATION = 0.35

# --- SENSOR & CALIBRATION ---
OFFSETS = [111, 95, 100]  # Per-sensor grayscale offsets [left, center, right].
LOST_LINE_TIMEOUT = 5.0
CALIBRATION_TIMEOUT = 8.0
OBSTACLE_THRESHOLD = 3.0 # Stop if obstacle closer than 5cm

# --- NETWORK CONFIG ---
BRIDGE_IP = "127.0.0.1"
SENSOR_PORT = 5555
MOTOR_PORT = 5556
MISSION_STATE_HEARTBEAT = 1.0  # Publish mission state at least this often, even without changes.
STARTUP_INTERSECTION_GUARD_SEC = 0.8  # Ignore intersection handling briefly after boot to let sensors/PID settle.

# --- LOCALIZATION / ROUNDABOUT TUNING ---
LOCALIZATION_TIMEOUT = 2.0            # Max age of localization sample before considered stale.
ROUNDABOUT_EXIT_ACCUM_HEADING_DEG = 300.0  # Heading accumulation to start exit preparation.
ROUNDABOUT_EXIT_DIRECTION = "right"    # Exit direction for roundabout maneuver.
ROUNDABOUT_EXIT_TRIGGER_MODE = "line"  # "line" (perception stop line) or "heading" (localization heading accumulation).
ROUNDABOUT_EXIT_MIN_CIRCULATE_TIME = 1.0  # Minimum time in roundabout circulation before allowing exit trigger.
ROUNDABOUT_EXIT_LINE_DISTANCE_CM = 10.0  # Exit trigger threshold from perception distance_to_line.
ROUNDABOUT_EXIT_USE_BRANCH_TRIGGER = True  # In EXIT_PREP, wait for side branch cue on grayscale before turning.
ROUNDABOUT_EXIT_BRANCH_HITS = 3  # Consecutive center+side detections required before committing exit turn.
ROUNDABOUT_EXIT_SEARCH_TIMEOUT = 3.0  # Max time to search for branch cue before forcing exit turn (s).
ROUNDABOUT_EXIT_SEARCH_SPEED = 1  # Forward speed while searching for exit branch cue.
ROUNDABOUT_EXIT_CENTER_THRESHOLD = 0.82  # Stricter center-sensor gate for branch detection to reduce false exits.