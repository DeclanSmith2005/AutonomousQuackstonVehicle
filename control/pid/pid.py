import time
import threading
import matplotlib.pyplot as plt
from picarx import Picarx

# --- CALIBRATION ---
OFFSET_L = 111
OFFSET_M = 95
OFFSET_R = 100

BLUE_MIN = 500
BLUE_MAX = 800

WHITE_MIN = 1000

# Sensitivity: Ignore noise below this threshold
NOISE_GATE = 50 

# --- PID TUNING ---
# If it avoids the line (tracks black), change POLARITY to -1
POLARITY = -1 

# Params
KP = 0.40   # was 0.45
KI = 0.0 
KD = 0.05  

BASE_SPEED = 20    
MAX_STEER = 30
LOOP_INTERVAL = 0.01

stop_flag = False
error_buffer = [0, 0, 0] 
weights = [1, 0, -1]
bias_mode = 'c'
last_line_seen = False

# Branch handling
BRANCH_DETECT = 80
BRANCH_BIAS = 20

def key_listener():
    global stop_flag, bias_mode
    while not stop_flag:
        cmd = input().strip().lower()
        if cmd == 's':
            stop_flag = True
        elif cmd in ('r', 'l', 'c'):
            bias_mode = cmd
            print(f"Mode set to: {bias_mode}")

# Only treat values in the blue range as line signal; ignore white/other colors.
def blue_signal(raw, offset):
    if raw >= WHITE_MIN:
        return 0
    if raw < BLUE_MIN or raw > BLUE_MAX:
       return 0
    return max(0, raw - offset)
    
def get_line_error(px):
    global last_line_seen
    raw_values = px.get_grayscale_data()

    s_l = blue_signal(raw_values[0], OFFSET_L)
    s_m = blue_signal(raw_values[1], OFFSET_M)
    s_r = blue_signal(raw_values[2], OFFSET_R)

    # Noise Gate: If signals are very weak (no blue detected), return 0
    has_line = s_l > NOISE_GATE or s_m > NOISE_GATE or s_r > NOISE_GATE
    if not has_line:
        last_line_seen = False
        return 0.0

    total_signal = s_l + s_m + s_r
    if total_signal == 0:
        return 0.0

    # Weighted Average
    numerator = (s_l * weights[0]) + (s_r * weights[2])

    error = (numerator / total_signal) * 100

    has_left = s_l > BRANCH_DETECT
    has_mid = s_m > BRANCH_DETECT
    has_right = s_r > BRANCH_DETECT
    full_bar = has_left and has_mid and has_right
    was_line = last_line_seen
    last_line_seen = True

    # Bias only when the center line is present (branch scenario)
    if bias_mode == 'r' and has_mid and has_right:
        error -= BRANCH_BIAS
    elif bias_mode == 'l' and has_mid and has_left:
        error += BRANCH_BIAS
    elif bias_mode == 'r' and full_bar and not was_line:
        error -= BRANCH_BIAS
    elif bias_mode == 'l' and full_bar and not was_line:
        error += BRANCH_BIAS

    return error

def clamp(n, minn, maxn):
    return max(minn, min(maxn, n))

def main():
    global stop_flag
    px = Picarx()
    
    last_error = 0
    integral = 0
    
    # Logging
    history_pv = []
    history_steering = []
    
    threading.Thread(target=key_listener, daemon=True).start()

    try:
        while not stop_flag:
            # 1. Get Error
            error = get_line_error(px)

            # 2. Smooth Error (Moving Average)
            error_buffer.pop(0)
            error_buffer.append(error)
            smooth_error = sum(error_buffer) / 3.0
            
            # 3. PID Math
            P = KP * smooth_error
            
            integral += smooth_error
            integral = clamp(integral, -50, 50)
            I = KI * integral
            
            D = KD * (smooth_error - last_error)
            
            # Apply Polarity here
            output = POLARITY * (P + I + D)
            
            last_error = smooth_error
            
            # 4. Motor Control
            steering_angle = clamp(output, -MAX_STEER, MAX_STEER)
            px.set_dir_servo_angle(steering_angle)
            
            # Slow down on turns
            speed_drop = abs(steering_angle) * 0.5
            current_speed = max(BASE_SPEED - speed_drop, 5)
            px.forward(current_speed)
            
            # Log
            history_pv.append(smooth_error)
            history_steering.append(steering_angle)
            
            time.sleep(LOOP_INTERVAL)

    finally:
        px.stop()
        print("Stopped.")

if __name__ == "__main__":
    main()