import json
import os
import time
import config

# Default calibration values (updated from calibration session)
DEFAULT_CAL_MIN = [50, 50, 50]   # Floor values (off-line)
DEFAULT_CAL_MAX = [1455, 1315, 1383]  # Peak values (on-line)

# Calibration file path (persists across reboots)
CALIBRATION_FILE = os.path.join(os.path.dirname(__file__), "calibration.json")


def load_calibration():
    """Load calibration from file, or return defaults if file doesn't exist."""
    try:
        if os.path.exists(CALIBRATION_FILE):
            with open(CALIBRATION_FILE, 'r') as f:
                data = json.load(f)
                cal_min = data.get('min', DEFAULT_CAL_MIN)
                cal_max = data.get('max', DEFAULT_CAL_MAX)
                print(f"Loaded calibration from {CALIBRATION_FILE}")
                return cal_min, cal_max
    except Exception as e:
        print(f"Error loading calibration file: {e}")
    
    print("Using default calibration values...")
    return DEFAULT_CAL_MIN.copy(), DEFAULT_CAL_MAX.copy()


def save_calibration(cal_min, cal_max):
    """Save calibration to file for persistence across reboots."""
    try:
        data = {'min': cal_min, 'max': cal_max}
        with open(CALIBRATION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Calibration saved to {CALIBRATION_FILE}")
        return True
    except Exception as e:
        print(f"Error saving calibration: {e}")
        return False


def run_wiggle_calibration(px, eyes):
    """Execute wiggle calibration directly on hardware.
    
    Parameters
    ----------
    px : Picarx
        The Picarx robot instance.
    eyes : LineSensor
        The line sensor instance to apply calibration to.
    
    Returns
    -------
    bool
        True if calibration completed successfully.
    """
    print("Starting wiggle calibration...")
    cal_min = [4095, 4095, 4095]
    cal_max = [0, 0, 0]
    
    # Calibration parameters
    CAL_TURN_ANGLE = 25
    CAL_TURN_SPEED = 10
    CAL_DURATION = 0.8
    CAL_INTERVAL = 0.05

    def collect_samples(duration_s):
        start = time.time()
        while (time.time() - start) < duration_s:
            sample = px.get_grayscale_data()
            for i in range(3):
                cal_min[i] = min(cal_min[i], sample[i])
                cal_max[i] = max(cal_max[i], sample[i])
            time.sleep(CAL_INTERVAL)

    # Wiggle Left
    px.set_dir_servo_angle(CAL_TURN_ANGLE)
    px.forward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)
    px.backward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)

    # Wiggle Right
    px.set_dir_servo_angle(-CAL_TURN_ANGLE)
    px.forward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)
    px.backward(CAL_TURN_SPEED)
    collect_samples(CAL_DURATION)

    px.stop()
    px.set_dir_servo_angle(config.STRAIGHT_ANGLE)
    time.sleep(0.2)

    print(f"Calibration Complete: min={cal_min}, max={cal_max}")
    eyes.apply_calibration(cal_min, cal_max)
    save_calibration(cal_min, cal_max)
    return True
