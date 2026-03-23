# --- GLOBAL SETTINGS ---
LOOP_INTERVAL = 0.01  # Main loop period (s), target 100 Hz update rate.
MISSION_STATE_HEARTBEAT = 1.0  # Publish mission state at least this often, even without changes.
STARTUP_INTERSECTION_GUARD_SEC = 0.8  # Ignore intersection handling briefly after boot to let sensors/PID settle.
STRAIGHT_INTERSECTION_DEBOUNCE_FRAMES = 2  # Require this many consecutive CROSS frames before STRAIGHT intersection handling.
STRAIGHT_INTERSECTION_COOLDOWN_S = 0.5  # Minimum time between STRAIGHT intersection events.

DUCK_WAIT = 5

# --- VEHICLE GEOMETRY ---
WHEELBASE_CM = 9.5  # Wheelbase length for bicycle model (cm)
STRAIGHT_ANGLE = 0  # Servo angle for driving straight

# --- PID STEERING CONTROL ---
KP = 0.18           
KI = 0.0            
KD = 0.03           
ERROR_BUFFER_LEN = 2 # Increase from 1 — smooths sensor noise
DEADBAND = 0.5     # Decrease from 5.0 — allows earlier, gentler corrections
STEER_SMOOTH_ALPHA = 1.0  # EMA filter on steering output. Lower = smoother but laggier.

# --- MOTION PARAMETERS ---
BASE_SPEED = 5
MAX_STEER = 30
MIN_DRIVE_SPEED = 1
SPEED_DROP_GAIN = 0.45  # Reduce speed as steering angle grows.
SPEED_RAMP_RATE = 2.0
CURVE_STEER_BOOST_THRESHOLD = 25.0  # Error magnitude where extra steering authority begins.
CURVE_STEER_BOOST_GAIN = 0.3  # Higher = tighter response on hard curves.
CURVE_STEER_BOOST_MAX = 1.2  # Cap on multiplicative steering boost in sharp curves.

# --- EDGE FOLLOWING OFFSETS ---
# 0 = centered. Around +/-50 biases tracking toward center+outer sensor overlap.
EDGE_OFFSET_LEFT_TURN = -0.0
EDGE_OFFSET_RIGHT_TURN = 0.0

# --- SENSOR & OBSTACLE CONFIG ---
OFFSETS = [111, 95, 100]  # Per-sensor grayscale offsets [left, center, right].
LOST_LINE_TIMEOUT = 5.0
CALIBRATION_TIMEOUT = 8.0
OBSTACLE_THRESHOLD = 3.0  # Stop if obstacle closer than 3cm
ULTRASONIC_BUFFER_LEN = 3  # Number of recent distance values to keep for median filtering

# --- APPROACH & STOP TUNING ---
APPROACH_SPEED = 3
STOP_HOLD_TIME = 2.0
STOP_CLEAR_TIME = 0.5
PASS_TIME = 0.35
STOP_DELAY = 0.25

# --- TURN TUNING (Common) ---
# Execution Modes: "trajectory" (camera), "pivot" (differential), "classic" (timed)
TURN_EXECUTION_MODE = "trajectory"
# Trigger Modes: "grayscale", "camera", or "either"
TURN_TRIGGER_MODE = "grayscale"
# Max distance to line (cm) from perception to arm/trigger a turn
MAX_TURN_PROXIMITY = 15

TURN_PWM = [27, 20, 27]  # [left_1, right, left_2]
TURN_OUTER_PWM_MULT = [1.3, 1.9, 1.3]
TURN_INNER_PWM_MULT = [0.6, 0.1, 0.7]
TURN_ENTRY_SPEED = 7
TURN_POST_SPEED = 5
TURN_STOP_HOLD_TIME = 3.0
TURN_BLIND_TIME = 0.5
TURN_SCAN_TIMEOUT = 5.0
TURN_SCAN_INTERVAL = 0.01
TURN_RECOVERY_PWM = 10
TURN_STABILIZE_TIME = 0.1
TURN_ENTRY_TIMEOUT = 5.0

# --- NO-LINE OUTSIDE WHEEL TURN TUNING ---
NO_LINE_TURN_LINE_CHECK_DELAY = 1.75  # seconds before checking grayscale
NO_LINE_OUTSIDE_PWM = [30, 30]
NO_LINE_INNER_PWM = [30, 15]  # Speed of the inner wheel (reverse) to help pivot in place!
NO_LINE_OUTSIDE_TIME = [3.0, 3.0]
NO_LINE_PRE_STOP_DELAY = [0.2, 0.0, 0.3]  # Delay (s) before stopping [left_1, right, left_2]. Allows crossing the line slightly.

# --- CAMERA-GUIDED TURN TUNING (Trajectory-based) ---
SNAPSHOT_WAIT_TIMEOUT = 1.0  # Max time to wait for trajectory snapshot (s)
TURN_LOOKAHEAD_MIN_CM = 18  # Minimum y_ref used by bicycle model to avoid steering saturation
TURN_CAMERA_TIMEOUT = [1.85, 1.65, 1.5]  # Max turn duration before fallback [left_turn, right_turn, left_2] (s)
TURN_INITIAL_ROTATION_TIME = 0.3  # Brief initial rotation to point toward exit lane
TURN_PROFILE_DURATION = [1.85, 1.65, 1.5]  # Time to walk through the captured turn profile [left_turn, right_turn, left_2] (s)
TURN_MIN_LINE_CHECK_TIME = 1.1  # Delay before grayscale can end the turn (s)
TRAJECTORY_TIMEOUT = 0.3  # Freshness window for trajectory points (s)
TURN_TRAJECTORY_MAX_AGE = 0.5  # Max acceptable age of trajectory samples during trajectory turns (s)
INTERSECTION_DISTANCE_TIMEOUT = 1.0  # Freshness window for distance_line (s)
TURN_TRAJECTORY_CAMERA_TILT_DOWN = -35  # Camera tilt angle before capturing trajectory.
TURN_FEEDFORWARD_GAIN = 1.5  # Base gain on bicycle-model steering command
TURN_CTE_FEEDBACK_GAIN = 0.45  # Deg per cm of live CTE tracking error
TURN_HEADING_FEEDBACK_GAIN = 0.8  # Gain on heading error inferred from trajectory slope
TURN_STEER_SMOOTHING_ALPHA = 0.5  # Command low-pass: 0=no update, 1=no smoothing

# --- PIVOT TURN TUNING ---
PIVOT_TURN_PWM = 20  # PWM used for in-place pivot turning (0-100)
PIVOT_SCAN_TIMEOUT = 2.0  # Max pivot duration before declaring turn failure (s)
PIVOT_MAX_PRE_SCAN_TIME = 0.5  # Hard cap on pivoting before switching to forward scan/reacquisition.
PIVOT_REQUIRE_LINE_SEQUENCE = True  # If True, keep pivoting until grayscale sequence is detected.
PIVOT_FORWARD_SETTLE_TIME = 0.3  # Time to drive forward before starting line reacquisition.
PIVOT_ALIGN_ENABLE = True
PIVOT_ALIGN_MIN_TIME = 0.25  # Minimum pivot time before line-alignment checks can end the turn
PIVOT_ALIGN_MIN_HITS = 2  # Consecutive alignment detections required to finish pivot
PIVOT_ALIGN_SENSOR_THRESHOLD = 0.72

# --- ROUNDABOUT TUNING ---
ROUNDABOUT_TURN_LINE_CHECK_DELAY = 1.5  # seconds before checking grayscale
# Entry Blind Turn
ROUNDABOUT_ENTRY_PIVOT_ENABLE = True
ROUNDABOUT_ENTRY_PIVOT_DIRECTION = "right"  # "left" or "right"
ROUNDABOUT_ENTRY_PIVOT_PWM = 15
ROUNDABOUT_ENTRY_PIVOT_DURATION = 0.4
ROUNDABOUT_ENTRY_OUTER_PWM_MULT = 1.8
ROUNDABOUT_ENTRY_INNER_PWM_MULT = 0.2
ROUNDABOUT_ENTRY_LEFT_MOTOR_PWM = 20
ROUNDABOUT_ENTRY_INNER_MOTOR_PWM = 15
ROUNDABOUT_ENTRY_LEFT_MOTOR_TIME = 1.75

# Exit Logic
ROUNDABOUT_CIRCULATE_SPEED = 1
ROUNDABOUT_EXIT_DIRECTION = "right"
ROUNDABOUT_EXIT_TRIGGER_MODE = "line"  # "line" (perception stop line) or "heading" (localization)
ROUNDABOUT_EXIT_ACCUM_HEADING_DEG = 300.0
ROUNDABOUT_EXIT_MIN_CIRCULATE_TIME = 1.0
ROUNDABOUT_EXIT_LINE_DISTANCE_CM = 10.0
ROUNDABOUT_EXIT_USE_BRANCH_TRIGGER = False
ROUNDABOUT_EXIT_BRANCH_HITS = 3
ROUNDABOUT_EXIT_SEARCH_TIMEOUT = 3.0
ROUNDABOUT_EXIT_SEARCH_SPEED = 1
ROUNDABOUT_EXIT_CENTER_THRESHOLD = 0.82
ROUNDABOUT_EXIT_LEFT_MOTOR_PWM = 20
ROUNDABOUT_EXIT_INNER_MOTOR_PWM = 15
ROUNDABOUT_EXIT_LEFT_MOTOR_TIME = 1.0

# --- LOCALIZATION & NETWORK ---
LOCALIZATION_TIMEOUT = 2.0
BRIDGE_IP = "127.0.0.1"
SENSOR_PORT = 5555
MOTOR_PORT = 5556

# --- LEGACY SUPPORT (Deprecated) ---
TURN_USE_CAMERA = True
TURN_USE_PIVOT = False
NO_LINE_TURN_MODE = "camera"
NO_LINE_TIMEOUT = 10

# --- RECOVERY PARAMETERS ---
RECOVERY_ENABLED = True
# Only attempt recovery after line has been lost this long
RECOVERY_TRIGGER_TIMEOUT = 0.25   # seconds
# How much recent motion to remember
RECOVERY_HISTORY_SEC = 1.25
RECOVERY_MIN_SAMPLES = 6
# Reverse motion tuning
RECOVERY_REVERSE_SPEED_SCALE = 0.75
RECOVERY_MAX_REVERSE_SPEED = 22
RECOVERY_STEER_MULTIPLIER = 1.0
# Stop briefly before starting reverse retrace
RECOVERY_SETTLE_TIME = 0.15
# Require line to be seen for this many consecutive checks before declaring success
RECOVERY_LINE_REACQUIRE_FRAMES = 2
# Prevent repeated rapid recovery loops
RECOVERY_COOLDOWN_SEC = 1.0