KP = 0.25
KI = 0.0
KD = 0.008 
ERROR_BUFFER_LEN = 5
DEADBAND = 3.0

# --- MOTION PARAMETERS ---
BASE_SPEED = 15
MAX_STEER = 30
LOOP_INTERVAL = 0.01  # Main loop period (s), target 100 Hz update rate.
STRAIGHT_ANGLE = 0
MIN_DRIVE_SPEED = 8
SPEED_DROP_GAIN = 0.25  # Reduce speed as steering angle grows.
SPEED_RAMP_RATE = 2.0

# --- APPROACH & STOP TUNING ---
APPROACH_SPEED = 10
TURN_PWM = 7
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
TURN_ENTRY_SPEED = 5
TURN_STOP_HOLD_TIME = 3.0
MAX_TURN_PROXIMITY = 20 # in cm

# --- CAMERA-GUIDED TURN TUNING (Snapshot-based) ---
TURN_USE_CAMERA = True           # Enable camera-guided turns (set False to use old blind turn)
TURN_USE_PIVOT = False           # Enable in-place pivot turn using per-motor control when TURN_USE_CAMERA=False
SNAPSHOT_WAIT_TIMEOUT = 1.0      # Max time to wait for trajectory snapshot (s)
WHEELBASE_CM = 9.5               # Wheelbase length for bicycle model (cm)
TURN_LOOKAHEAD_MIN_CM = 25.0     # Minimum y_ref used by bicycle model to avoid steering saturation
TURN_CAMERA_TIMEOUT = 4.0        # Max turn duration before fallback (s)
TURN_INITIAL_ROTATION_TIME = 0.3 # Brief initial rotation to point toward exit lane
TURN_PROFILE_DURATION = 2.0      # Time to walk through the captured turn profile (s)
TURN_MIN_LINE_CHECK_TIME = 0.9   # Delay before grayscale can end the turn (s)
TRAJECTORY_TIMEOUT = 0.3         # Freshness window for trajectory points (s)
INTERSECTION_DISTANCE_TIMEOUT = 0.4  # Freshness window for distance_line (s)

# --- PIVOT TURN TUNING ---
PIVOT_TURN_PWM = 7               # PWM used for in-place pivot turning (0-100)
PIVOT_SCAN_TIMEOUT = 3.0         # Max pivot duration before declaring turn failure (s)

# --- SENSOR & CALIBRATION ---
OFFSETS = [111, 95, 100]  # Per-sensor grayscale offsets [left, center, right].
LOST_LINE_TIMEOUT = 5.0
CALIBRATION_TIMEOUT = 8.0
OBSTACLE_THRESHOLD = 5.0 # Stop if obstacle closer than 5cm

# --- NETWORK CONFIG ---
BRIDGE_IP = "127.0.0.1"
SENSOR_PORT = 5555
MOTOR_PORT = 5556
MISSION_STATE_HEARTBEAT = 1.0  # Publish mission state at least this often, even without changes.