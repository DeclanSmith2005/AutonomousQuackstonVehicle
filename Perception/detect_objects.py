from aiymakerkit import vision
from aiymakerkit import utils
from pycoral.utils.dataset import read_label_file
import models
import cv2
import os
import time
from perception_server_comms import send_cte, send_distance_to_line, send_duck_detection, send_object_detection
from lane_detection_and_cte import detect_lane_cte
import pandas as pd
from datetime import datetime

# Change detector and label names
detector = vision.Detector(models.PROJECT_DETECTION_MODEL)
labels = read_label_file(models.PROJECT_DETECTION_LABELS)

frame_count = 0
total_processing_time = 0.0
cte_log = []  # List to store CTE data for each frame

# Define object real heights in meters - note this is the height of the trained portion of the objects
REAL_HEIGHTS = {
    "car": 0.065,
    "Stop": 0.05,
    "oneway": 0.025,
    "Yield": 0.047,
    "DNE": 0.04,
    "Duck": 0.03
}

# Camera intrinsics obtained from camera calibration
fy = 616.13761171
fx = 616.00734472
cx = 315.68903815

# 0.22 m is the lane width with upper bound tolerance, a factor of 1.5 is used to account for the car not being centered in the lane
max_lane_width_meters = 0.22 * 1.5

def compute_distance(label, pixel_height): 
    if pixel_height <= 0:
        return None
    
    real_height = REAL_HEIGHTS.get(label, None)
    if real_height is None:
        return None
    
    distance = (real_height * fy) / pixel_height
    return distance

def compute_horizontal_distance(label, bbox):
    lateral_offset = None
    if bbox is None:
        return None
    
    pixel_height = bbox.ymax - bbox.ymin
    distance = compute_distance(label, pixel_height)
    
    if distance is not None:
        bbox_center_x = (bbox.xmin + bbox.xmax) / 2
        lateral_offset = ((bbox_center_x - cx)/fx) * distance
    
    if lateral_offset is not None:
        return lateral_offset
    else:
        return None

for frame in vision.get_frames(display=False):
    start_time = time.time()
    frame_count += 1
    detected_object_distances = []
    detected_duck_data = []

    # ---object detection---
    objects = detector.get_objects(frame, threshold=0.4)
    for obj in objects:
        label = labels[obj.id]
        bbox = obj.bbox
        pixel_height = bbox.ymax - bbox.ymin
        distance = compute_distance(label, pixel_height)

        if label == "Duck":
            horizontal_distance = compute_horizontal_distance(label, bbox)
            if horizontal_distance is not None:
                if abs(horizontal_distance) <= max_lane_width_meters:
                    detected_duck_data.append((label, round(distance, 3), round(horizontal_distance, 3)))
                else:
                    continue
        if distance is not None:
            detected_object_distances.append((label, round(distance, 3)))
    
    # Show the objects detected in frame and print their distances
    # print(detected_object_distances)
    vision.draw_objects(frame, objects, labels)
    cv2.imshow('Object Detection', frame)

    # # Sending duck detections to server
    # for duck in detected_duck_data:
    #     label, distance, horizontal_distance = duck
    #     # print(f"Detected {label} at distance: {distance:.3f} m, horizontal distance: {horizontal_distance:.3f} m")
    #     send_duck_detection_to_server(distance, horizontal_distance)

    # # Sending other object detections to server
    # for obj in detected_object_distances:
    #     label, distance = obj
    #     # print(f"Detected {label} at distance: {distance:.3f} m")
    #     send_object_detection_to_server(label, distance)

    # ---lane processing---
    cte_m_list, distance_m_list, lane_vis, bev, distance_to_line = detect_lane_cte(frame)

    if distance_to_line is not None:
        print(f"Distance to horizontal line: {distance_to_line:.3f} m")
        send_distance_to_line(distance_to_line)
    if cte_m_list is not None and distance_m_list is not None:
        # Send CTE and distance (both in meters) to control server
        # distance_m_list: lookahead distances from car in meters (near to far)
        # cte_m_list: CTE values in meters at each distance
        print(f"CTE(m): {[round(c, 4) for c in cte_m_list[:3]]}... dist(m): {[round(d, 4) for d in distance_m_list[:3]]}...")
        send_cte(cte_m_list, distance_m_list)

    # if distance_to_line is not None:
    #     print(f"Distance to horizontal line: {distance_to_line:.3f} m")
    #     send_distance_to_line_to_server(distance_to_line)

    # if lane_vis is not None:
    #     cv2.imshow('Lane Detection', lane_vis)

    # if bev is not None:
    #     cv2.imshow('BEV', bev)

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