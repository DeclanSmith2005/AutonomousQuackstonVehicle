import time
import sys
from pathlib import Path
# Add parent directory to path so we can import utils module
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.detection_sender import UdpDetectionSender

# Example list of detections: [class_id, [x1, y1, x2, y2]]
objects = [[0, [0, 0, 10, 10]], [1, [20, 20, 40, 40]]]

if __name__ == "__main__":
    sender = UdpDetectionSender()
    frame_id = 0
    while True:
        print(f"Sending detections: {objects} (frame_id={frame_id})")
        sender.send(objects, frame_id)
        frame_id += 1
        time.sleep(1)
