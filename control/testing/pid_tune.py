import time
import csv
from picarx import Picarx

# CONFIG
TEST_SPEED = 20      # Must match the speed you intend to run PID at!
STEP_ANGLE = 20      # Step input magnitude (degrees)
DURATION = 2.0       # Seconds to record

# CALIBRATION (Use your values)
OFFSET_L = 111
OFFSET_M = 95
OFFSET_R = 100
OFFSETS = [OFFSET_L, OFFSET_M, OFFSET_R]

def get_error(px):
    raw_values = px.get_grayscale_data()
    
    # LOGIC FLIP: 
    # We want "Signal" to represent "How much LINE do I see?"
    # If Line is BRIGHTER than background, Signal = Raw - Background
    
    s_l = max(0, raw_values[0] - OFFSET_L)
    s_m = max(0, raw_values[1] - OFFSET_M)
    s_r = max(0, raw_values[2] - OFFSET_R)
    
    total_signal = s_l + s_m + s_r
    
    # Noise Gate: If we see nothing brighter than the floor, we are lost
    if total_signal < 100:
        return 0.0

    # The rest of the PID logic remains exactly the same!
    # Left is still Left.
    numerator = (s_l * 1.0) + (s_r * -1.0)
    error = (numerator / total_signal) * 100
    
    return error

def main():
    px = Picarx()
    data = [] # List to store [time, input_u, output_y]
    
    print("Place car on line. Press Enter to start STEP RESPONSE test.")
    input()
    
    print("Running...")
    px.forward(TEST_SPEED)
    px.set_dir_servo_angle(0)
    
    start_time = time.time()
    
    # Phase 1: Drive Straight for 1s (Establish baseline)
    while (time.time() - start_time) < 1.0:
        now = time.time() - start_time
        err = get_error(px)
        data.append([now, -13.9, err]) # Input is -13.9
        time.sleep(0.01)
        
    # Phase 2: THE STEP (Turn wheels to 20 degrees)
    px.set_dir_servo_angle(STEP_ANGLE)
    
    while (time.time() - start_time) < DURATION:
        now = time.time() - start_time
        err = get_error(px)
        # Important: If line is lost, stop recording or mark it?
        # For now, just record everything. MATLAB can trim it.
        data.append([now, STEP_ANGLE, err]) 
        time.sleep(0.01)
        
    px.stop()
    print("Test Complete. Saving CSV...")
    
    with open('step_response.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'Input_u', 'Output_y'])
        writer.writerows(data)
    print("Saved to step_response.csv")

if __name__ == "__main__":
    # Add your get_error implementation above!
    main()