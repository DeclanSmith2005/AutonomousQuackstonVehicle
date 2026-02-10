import csv
import time
import threading
import matplotlib.pyplot as plt
from picarx import Picarx

# --- CALIBRATION ---
OFFSET_L = 111
OFFSET_M = 95
OFFSET_R = 100

# Anything ABOVE this is a Wall/Border (White) -> Ignore it (return 0)
WHITE_CUTOFF = 1240  

# Anything BELOW this is the Floor (Black) -> Ignore it (return 0)
LINE_THRESHOLD = 800 

# Threshold for "seeing" a line for logic decisions (Stop/Branch)
LOGIC_DETECT = 50 

# Sensitivity: Ignore noise below this threshold
NOISE_GATE = 50 

# --- PID TUNING ---
# If it avoids the line (tracks black), change POLARITY to -1
POLARITY = -1 

# Params
KP = 0.40  
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

def color_signal(raw, offset):
    """
    Returns signal strength ONLY if it falls in the Green/Red range.
    Ignores White (Border) and Black (Floor).
    """
    # 1. Reject White Borders
    if raw > WHITE_CUTOFF:
        return 0.0
        
    # 2. Reject Black Floor
    if raw < LINE_THRESHOLD:
        return 0.0
        
    # 3. Return Signal (High Value = Strong Line)
    # We subtract offset (Black) to get magnitude
    return max(0, raw - offset)

def get_line_error(px):
    global last_line_seen
    raw_values = px.get_grayscale_data()

    # 1. Convert raw readings to signal strength
    s_l = color_signal(raw_values[0], OFFSET_L)
    s_m = color_signal(raw_values[1], OFFSET_M)
    s_r = color_signal(raw_values[2], OFFSET_R)

    # 2. STOP LINE CHECK (Priority #1)
    # If ALL THREE sensors see a line, it is a RED STOP LINE.
    # (Green branches usually only trigger 2 sensors at once).
    if s_l > LOGIC_DETECT and s_m > LOGIC_DETECT and s_r > LOGIC_DETECT:
        print("!!! STOP LINE DETECTED !!!")
        px.stop()
        time.sleep(2.0) # Wait 2 seconds
        
        # ESCAPE MANEUVER: Drive blind to clear the red line
        print("Clearing line...")
        px.forward(BASE_SPEED)
        time.sleep(0.1) # Adjust this time if it doesn't fully clear the line
        return 0.0

    # 3. Normal Line Tracking
    has_line = s_l > NOISE_GATE or s_m > NOISE_GATE or s_r > NOISE_GATE
    if not has_line:
        last_line_seen = False
        return 0.0

    total_signal = s_l + s_m + s_r
    if total_signal == 0: return 0.0

    # Weighted Average Error
    numerator = (s_l * weights[0]) + (s_r * weights[2])
    error = (numerator / total_signal) * 100

    # 4. Branch Biasing (Priority #2)
    # We only check this if we didn't Stop.
    has_left = s_l > LOGIC_DETECT
    has_mid = s_m > LOGIC_DETECT
    has_right = s_r > LOGIC_DETECT

    # Update state
    was_line = last_line_seen
    last_line_seen = True

    # Apply Bias for Branches
    # Note: We removed 'full_bar' because that is now handled by the Stop Check above.
    
    # Right Branch Bias: Middle + Right are high
    if bias_mode == 'r' and has_mid and has_right:
        error -= BRANCH_BIAS
        
    # Left Branch Bias: Middle + Left are high
    elif bias_mode == 'l' and has_mid and has_left:
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
    history = []
    start_time = time.time()
    
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
            
            # Apply Polarity
            output = POLARITY * (P + I + D)
            
            last_error = smooth_error
            
            # 4. Motor Control
            steering_angle = clamp(output, -MAX_STEER, MAX_STEER)
            px.set_dir_servo_angle(steering_angle)
            
            # Slow down on turns
            speed_drop = abs(steering_angle) * 0.3
            current_speed = max(BASE_SPEED - speed_drop, 5)
            px.forward(current_speed)
            
            # Log
            history.append((time.time() - start_time, smooth_error, steering_angle, current_speed))
            
            time.sleep(LOOP_INTERVAL)

    finally:
        px.stop()

        if history:
            log_name = f"logs/pid_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                with open(log_name, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["time_s", "error", "steering_angle", "speed"])
                    writer.writerows(history)
                print(f"Wrote log to {log_name}")
            except OSError as exc:
                print(f"Failed to write log: {exc}")

        print("Stopped.")

if __name__ == "__main__":
    main()