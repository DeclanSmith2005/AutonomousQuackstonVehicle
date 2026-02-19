from aiymakerkit import vision
from aiymakerkit import utils
from pycoral.utils.dataset import read_label_file
import models
import cv2
import os
import time

# Change detector and label names
detector = vision.Detector(models.SIGN_DETECTION_MODEL)
labels = read_label_file(models.SIGN_DETECTION_LABELS)

frame_count = 0
total_processing_time = 0.0

# Define object real heights in meters - note this is the height of the trained portion of the objects
REAL_HEIGHTS = {
    "Stop": 0.05,
    "One-Way": 0.025,
    "Yield": 0.047,
    "DNE": 0.04,
    "Duck": 0.03
} # Need to add construction cones & cars

# Camera focal length in pixels, obtained from camera calibration
fy = 616.13761171

def compute_distance(label, pixel_height): 
    if pixel_height <= 0:
        return None
    
    real_height = REAL_HEIGHTS.get(label, None)
    if real_height is None:
        return None
    
    distance = (real_height * fy) / pixel_height
    return distance


for frame in vision.get_frames(display=False):
    start_time = time.time()
    frame_count += 1
    detected_object_distances = []

    # Get each object
    objects = detector.get_objects(frame, threshold=0.4)

    # Calculate the distance to each object, appending tuples to a list of objects per frame
    for obj in objects:
        label = labels[obj.id]
        bbox = obj.bounding_box
        pixel_height = bbox.ymax - bbox.ymin
        distance = compute_distance(label, pixel_height)

        if distance is not None:
            detected_object_distances.append((label, round(distance,3)))

    print(detected_object_distances)

    # Show the frame after drawing
    vision.draw_objects(frame, objects, labels)
    cv2.imshow('Object Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # Track processing time
    frame_time = time.time() - start_time
    total_processing_time += frame_time

cv2.destroyAllWindows()

print(f"\nProcessed {frame_count} frames total")

if frame_count > 0:
    avg_time = total_processing_time / frame_count
    fps = 1.0 / avg_time if avg_time > 0 else 0
    print(f"Average processing time per frame: {avg_time*1000:.2f} ms")
    print(f"Average FPS: {fps:.2f}")