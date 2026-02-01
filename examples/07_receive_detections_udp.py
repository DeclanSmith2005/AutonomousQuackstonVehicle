import sys
from pathlib import Path
# Add parent directory to path so we can import utils module
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.detection_receiver import DetectionReceiver
from picarx import Picarx
import time
import pprint

car = Picarx()
detector = DetectionReceiver()

last_print = 0.0
PRINT_PERIOD = 0.5  # seconds

while True:
    detector.update()
    detections = detector.get_latest()

    now = time.time()
    if now - last_print > PRINT_PERIOD:
        print("\n--- Detection update ---")
        if detections is None:
            print("No detections (missing or stale)")
        else:
            pprint.pprint(detections)
        last_print = now

    if detections is None:
        car.stop()  # fail-safe
    else:
        objects = detections["objects"]
        if objects:
            car.set_dir_servo_angle(-10)
        else:
            car.set_dir_servo_angle(0)

    time.sleep(0.05)