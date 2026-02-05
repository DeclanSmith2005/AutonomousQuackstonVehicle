import time
import threading
import matplotlib.pyplot as plt
from picarx import Picarx

# --- CALIBRATION ---
OFFSET_L = 111
OFFSET_M = 95
OFFSET_R = 100
# Sensitivity: Ignore noise below this threshold
NOISE_GATE = 50 

# --- PID TUNING ---
# If it avoids the line (tracks white), change POLARITY to -1
POLARITY = -1 

# Params
KP = 0.45   
KI = 0.0 
KD = 0.05  

BASE_SPEED = 20    
MAX_STEER = 30
LOOP_INTERVAL = 0.01

stop_flag = False
error_buffer = [0, 0, 0] 

def key_listener():
    global stop_flag
    while not stop_flag:
        if input().lower() == 's':
            stop_flag = True

def get_line_error(px):
    raw_values = px.get_grayscale_data()
    
    # Normalize: High Value = Black Line
    s_l = max(0, raw_values[0] - OFFSET_L)
    s_m = max(0, raw_values[1] - OFFSET_M)
    s_r = max(0, raw_values[2] - OFFSET_R)
    
    # Noise Gate: If signals are very weak (all white), return 0
    if s_l < NOISE_GATE and s_m < NOISE_GATE and s_r < NOISE_GATE:
        return 0.0

    total_signal = s_l + s_m + s_r
    if total_signal == 0: return 0.0

    # Weighted Average
    numerator = (s_l * 1.0) + (s_r * -1.0)
    error = (numerator / total_signal) * 100
    
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
            error_buffer.append(error) # <--- FIXED: changed 'raw_error' to 'error'
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