# control/config.py

# --- PID TUNING ---
# These should match pid.py's "feel" but account for dt=0.01
# In pid.py, KD was 0.05 without / dt. To match that, KD should be 0.0005 if / dt is used.
# However, if we keep / dt, we can tune it to a new value.
KP = 0.28
KI = 0.0
KD = 0.005  # Adjusted to match pid.py's D-term which was 100x smaller (no / dt)
POLARITY = -1
ERROR_BUFFER_LEN = 5

# --- MOTION PARAMETERS ---
BASE_SPEED = 15
MAX_STEER = 35
LOOP_INTERVAL = 0.02
STRAIGHT_ANGLE = 0
MIN_DRIVE_SPEED = 5
SPEED_DROP_GAIN = 0.4
SPEED_RAMP_RATE = 2.0

# --- APPROACH & STOP TUNING ---
APPROACH_SPEED = 10
TURN_PWM = 20
STOP_HOLD_TIME = 2.0
STOP_CLEAR_TIME = 0.5

# --- TURN TUNING ---
TURN_TIME = 0.6
PASS_TIME = 0.5
TURN_BLIND_TIME = 0.5
TURN_SCAN_TIMEOUT = 5.0
TURN_SCAN_INTERVAL = 0.01
TURN_RECOVERY_PWM = 12
TURN_ANGLE = 35
TURN_STABILIZE_TIME = 0.1
TURN_ENTRY_TIMEOUT = 5.0
TURN_ENTRY_SPEED = 10
TURN_STOP_HOLD_TIME = 1.0

# --- SENSOR & CALIBRATION ---
OFFSETS = [111, 95, 100]
LOST_LINE_TIMEOUT = 5.0
CALIBRATION_TIMEOUT = 8.0
OBSTACLE_THRESHOLD = 5.0 # Stop if obstacle closer than 15cm

# --- NETWORK CONFIG ---
BRIDGE_IP = "127.0.0.1"
SENSOR_PORT = 5555
MOTOR_PORT = 5556