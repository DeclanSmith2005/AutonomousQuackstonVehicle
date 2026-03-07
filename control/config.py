# control/config.py

# --- PID TUNING ---
# These should match pid.py's "feel" but account for dt=0.01
# In pid.py, KD was 0.05 without / dt. To match that, KD should be 0.0005 if / dt is used.
# However, if we keep / dt, we can tune it to a new value.
KP = 0.30
KI = 0.0
KD = 0.008  # Adjusted to match pid.py's D-term which was 100x smaller (no / dt)
ERROR_BUFFER_LEN = 5
DEADBAND = 3.0

# --- MOTION PARAMETERS ---
BASE_SPEED = 12
MAX_STEER = 35
LOOP_INTERVAL = 0.01
STRAIGHT_ANGLE = 0
MIN_DRIVE_SPEED = 8
SPEED_DROP_GAIN = 0.25
SPEED_RAMP_RATE = 2.0

# --- APPROACH & STOP TUNING ---
APPROACH_SPEED = 10
TURN_PWM = 3
STOP_HOLD_TIME = 2.0
STOP_CLEAR_TIME = 0.5
STOP_DELAY = 0.25

# --- TURN TUNING ---
TURN_TIME = 2.0
PASS_TIME = 0.5
TURN_BLIND_TIME = 0.5
TURN_SCAN_TIMEOUT = 5.0
TURN_SCAN_INTERVAL = 0.01
TURN_RECOVERY_PWM = 12
TURN_ANGLE = 30
TURN_STABILIZE_TIME = 0.1
TURN_ENTRY_TIMEOUT = 5.0
TURN_ENTRY_SPEED = 10
TURN_STOP_HOLD_TIME = 1.0
MAX_TURN_PROXIMITY = 20 # in cm

# --- CAMERA-GUIDED TURN TUNING (Pure Pursuit / Adaptive Lookahead) ---
TURN_USE_CAMERA = True           # Enable camera-guided turns (set False to use old blind turn)
LOOKAHEAD_DISTANCE_CM = 15.0     # Physical distance ahead to target (Pure Pursuit)
TRAJECTORY_KP = 0.8              # Steering gain per cm of CTE (higher = more aggressive curve following)
TURN_CAMERA_TIMEOUT = 4.0        # Max time for camera-guided turn before fallback
TURN_INITIAL_ROTATION_TIME = 0.3 # Brief initial rotation to point toward exit lane

# --- SENSOR & CALIBRATION ---
OFFSETS = [111, 95, 100]
LOST_LINE_TIMEOUT = 5.0
CALIBRATION_TIMEOUT = 8.0
OBSTACLE_THRESHOLD = 5.0 # Stop if obstacle closer than 15cm

# --- NETWORK CONFIG ---
BRIDGE_IP = "127.0.0.1"
SENSOR_PORT = 5555
MOTOR_PORT = 5556