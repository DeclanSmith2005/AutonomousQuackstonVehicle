---
title: "Perception Work Log - Lane Detection & CTE, Server Integration"
date: 2026-03-01
week: 7
hours: 2.25
tags: [Perception, Lane Detection, CTE, Server]
contributors: [Ishaan Grewal]
---

## Objectives

What did you plan to accomplish in this session?
- Modify `lane_detection_and_cte.py` to handle different vehicle states and make the script modular (with functions) and easy to integrate with the PID loop.
- Write and test the code for the STRAIGHT vehicle state in `lane_detection_and_cte.py`.
- Create a new `perception_server_comms.py` file to facilitate communication between the Perception pipeline and the main server.
- Modify `detect_objects.py` to include the lane detection and CTE calculations and send the results to the server.

## Detailed Work Log

### Session 1: [Lane Detection & CTE Modifications, Code for STRAIGHT State, Integration with Detect Objects Script] (2026-02-28, 20:00-21:45)

**Members Present**: [Ishaan Grewal]

**Description**: 
Revamped `lane_detection_and_cte.py` to handle different vehicle states, such as STRAIGHT, LEFT, and RIGHT. As a part of this, I restructured the previous code
into a function `detect_lane_cte(image)`, which takes in a single image and returns the CTE metrics and a visualization of the lane detection. This modularity
allows for `detect_objects.py` to call `detect_lane_cte(image)` within the primary for loop to find the CTE frame by frame. To still enable manual testing, 
I created a "main" block for testing on a sample image. In addition, I wrote the code for filtering the lane pixels for the case where `vehicle_state == "STRAIGHT"`.
The primary purpose of this code is to filter out any intersecting lanes and only focus on the desired straight path in front of the vehicle.

**Calculation #1:** Rather than assuming that the vehicle was always centred on the green lane and that the `lane_center_x` was the camera's center, I first
estimate the lane center from the bottom 20% of the image's pixels. To do this, I filter out these pixels and find the `lane_center_x` using the average of the lane
pixels' x coordinate. The implementation of this is shown in the code snippet below: 

### Code Snippet #1

```python
if vehicle_state == "STRAIGHT":
        # Estimate lane center from bottom region
        bottom_region = bev[int(height * 0.8) : height, :]  # take a horizontal slice of the bottom 20% of the image
        ys_bottom, xs_bottom = np.nonzero(bottom_region)  # get the x and y coordinates of the white pixels in the bottom region
        if len(xs_bottom) > 0:
            lane_center_x = int(np.mean(xs_bottom))  # average x coordinate of white pixels in the bottom region as the lane center
        else:
            lane_center_x = width // 2  # default to center if no pixels detected
```

**Calculation #2:** To filter out any intersecting lanes and only use the desired forward lane, I create a masked region of interest (roi), which captures all pixels
that are within 54 pixels to the left and right of the `lane_center_x`. The width of the lane itself is 54 pixels, so using `roi_half_width = 54` helps provide a 2x
margin of error for colour detection and BEV transform. To create a masked BEV, the `bitwise_and()` operation is used on the original BEV with the `mask_roi` to only
keep the pixels of interest. With this implementation, if there is a lane that intersects the direction of travel, it is filtered out before the polynomial curve is fitted,
which prevents noise in the polynomial generated and yields a more accurate CTE. The complete filtering of lane pixels for `vehicle_state == "STRAIGHT"` is shown in
code snippet below:

### Code Snippet #1

```python
# Filter lane pixels based on vehicle state
    if vehicle_state == "STRAIGHT":
        # Estimate lane center from bottom region
        bottom_region = bev[int(height * 0.8) : height, :]  # take a horizontal slice of the bottom 20% of the image
        ys_bottom, xs_bottom = np.nonzero(bottom_region)  # get the x and y coordinates of the white pixels in the bottom region
        if len(xs_bottom) > 0:
            lane_center_x = int(np.mean(xs_bottom))  # average x coordinate of white pixels in the bottom region as the lane center
        else:
            lane_center_x = width // 2  # default to center if no pixels detected

        roi_half_width = 54  # lane width on a straight is 54 pixels, so this gives 2x margin of error
        mask_roi = np.zeros_like(bev)
        l = max(lane_center_x - roi_half_width, 0)
        r = min(lane_center_x + roi_half_width, width)
        mask_roi[:, l:r] = 255
        bev_roi = cv2.bitwise_and(bev, mask_roi)
        ys, xs = np.nonzero(bev_roi)
```
**Results:** Running the above code on an example image at an intersection where a horizontal lane intersects the direction of travel displays its effectiveness.

The first figure below is of the lane detection output when the old code is used. Clearly, the horizontal lane introduces a significant amount of error since it causes the polynomial to be a quadratic. In regard to CTE, this would lead to highly inaccurate CTE values since the curve is not fit correctly on the lane to travel, which would cause incorrect input into the PID loop.

![Alt Text](/Perception/Lane_Pictures/lane_detection_output_with_old_code.png)

The image below is the output lane detection from the newly revised code, displaying how the horizontal lane is almost entirely filtered out. Although small segments are still present on the left and right of the primary lane, this does not interfere with the polynomial generated due to the dominance of the vertical segment. As seen in the output (red dotted line), the polynomial is now centred on the lane that is intended for travel, resulting in accurate CTE readings.

![Alt Text](/Perception/Lane_Pictures/lane_detection_output_with_new_code.png)

### Full Revised `lane_detection_and_cte.py` Code

```python
import cv2
import numpy as np
from perception_server_comms import get_vehicle_state, send_cte_to_server

#---------------------------------------------------------------CONSTANTS---------------------------------------------------------------------
# Green color range for lane detection in HSV color space
lower_green = np.array([40, 80, 80])  # lower bound for green color
upper_green = np.array([80, 255, 255])  # upper bound for green color

# BEV source points for perspective transformation for each vehicle state (right turn, left turn, or straight)
src_points_straight = np.float32([   # change top and bottom points to change distance that is analyzed
    [200, 300], # top-left, 62.5% of the height, which is 37.5% up from the bottom
    [440, 300], # top-right, 62.5% of the height, which is 37.5% up from the bottom
    [50, 470], # bottom-left
    [590, 470]  # bottom-right
])

# BEV destination points for perspective transformation
dst_points = np.float32([
    [150, 0],   # top-left
    [490, 0],   # top-right
    [150, 480], # bottom-left
    [490, 480]  # bottom-right
])

# BEV transformation matrix for each vehicle state (right turn, left turn, or straight)
M_straight = cv2.getPerspectiveTransform(src_points_straight, dst_points)

# Meters per pixel conversion factor for each vehicle state (right turn, left turn, or straight)
meters_per_pixel_straight = 0.00046296296  # 0.025m/54 pixels

#---------------------------------------------------------------MAIN CODE----------------------------------------------------------------------

def detect_lane_cte(image):
    """Process a single image and return CTE metrics and visualization.

    The vehicle state is determined internally by calling :func:`get_vehicle_state`.

    Parameters
    ----------
    image : np.ndarray
        BGR image from camera or file.

    Returns
    -------
    tuple
        (cte_pixels, cte_meters, output_image) where output_image is a BGR
        visualization showing the lane curve and center lines. If detection
        fails, outputs will be (None, None, None).
    """

    # vehicle_state = get_vehicle_state()
    vehicle_state = "STRAIGHT"  # for testing purposes, hardcode to straight until we have state detection working

    height, width = image.shape[:2]

    # Convert to HSV (Hue = Color, Saturation = Color Intensity, Value = Brightness) color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Green color thresholding for lane segmentation
    mask = cv2.inRange(hsv, lower_green, upper_green)  # white pixels represent green lane, everything else is black

    # Clean green mask
    kernel = np.ones((5, 5), np.uint8)
    # Morphological opening removes small dots from the background by eroding objects smaller than the kernel and then dilating the remaining objects back to their original size.
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    # Morphological closing fills small black holes in white objects by dilating the objects and then eroding them back to their original size.
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # BEV (Bird's Eye View) transformation based on vehicle state
    if vehicle_state == "STRAIGHT":
        bev = cv2.warpPerspective(mask, M_straight, (width, height))
    else:
        return None, None, None    

    # Filter lane pixels based on vehicle state
    if vehicle_state == "STRAIGHT":
        # Estimate lane center from bottom region
        bottom_region = bev[int(height * 0.8) : height, :]  # take a horizontal slice of the bottom 20% of the image
        ys_bottom, xs_bottom = np.nonzero(bottom_region)  # get the x and y coordinates of the white pixels in the bottom region
        if len(xs_bottom) > 0:
            lane_center_x = int(np.mean(xs_bottom))  # average x coordinate of white pixels in the bottom region as the lane center
        else:
            lane_center_x = width // 2  # default to center if no pixels detected

        roi_half_width = 54  # lane width on a straight is 54 pixels, so this gives 2x margin of error
        mask_roi = np.zeros_like(bev)
        l = max(lane_center_x - roi_half_width, 0)
        r = min(lane_center_x + roi_half_width, width)
        mask_roi[:, l:r] = 255
        bev_roi = cv2.bitwise_and(bev, mask_roi)
        ys, xs = np.nonzero(bev_roi)

    if len(xs) == 0 or len(ys) == 0:
        return None, None, None

    poly = np.polyfit(ys, xs, 2) # fit a second degree polynomial of the form x = ay^2 + by + c to the lane pixels
    a, b, c = poly

    # compute CTE at y_ref
    y_ref = int(height * 0.9)
    lane_x = a * y_ref * y_ref + b * y_ref + c
    car_center_x = width // 2
    cte_pixels = float(car_center_x) - lane_x
    if vehicle_state == "STRAIGHT":
        cte_meters = cte_pixels * meters_per_pixel_straight

    # visualization
    output = cv2.cvtColor(bev_roi, cv2.COLOR_GRAY2BGR)
    for y in range(0, height, 5):
        x = int(a * y * y + b * y + c)
        if 0 <= x < width:
            cv2.circle(output, (x, y), 2, (0, 0, 255), -1)
    cv2.line(output, (int(car_center_x), 0), (int(car_center_x), height), (255, 0, 0), 2)
    cv2.circle(output, (int(lane_x), y_ref), 8, (0, 255, 0), -1)

    return cte_pixels, cte_meters, output

if __name__ == "__main__":
    image = cv2.imread("stop_0_.jpg")
    if image is None:
        raise RuntimeError("failed to read test image")
    cte_px, cte_m, vis = detect_lane_cte(image)
    print(f"cte: {cte_px} px, {cte_m} m")
    if vis is not None:
        cv2.imshow("Lane Detection", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
```

## Next Steps

- [ ] Once Nolan writes the lane filtering code for the RIGHT and LEFT turn cases, the next step is to incorporate that into the `detect_lane_cte(image)` function
      and test its use with the Control PID loop. This will require lots of testing to fine-tune the PID and lane detection parameters.

### Session 2: [Perception & Server Integration] (2026-03-01, 16:00-16:30)

**Members Present**: [Ishaan Grewal]

**Description**: Created the `perception_server_comms.py` file to facilitate communication between the Perception pipeline and the server. To implement this, I created
two classes, `_VehicleStateManager` and `_CTESender`, which manage persistent ZMQ connections for receiving and sending data, respectively. By using a persistent socket
and non-blocking checks, receiving and sending data will be fast and blocks or hangs are avoided. The `get_vehicle_state()` and `send_cte_to_server()` functions
enable receiving vehicle state information for the `detect_lane_cte(image)` function and enable sending the frame CTE from `detect_objects.py`.

### `perception_server_comms.py` Code

```python
import zmq
import time

_global_context = zmq.Context()

# Initialize persistent socket once at module load
class _VehicleStateManager:
    """Manages persistent ZMQ connection for low-latency vehicle state updates."""
    
    def __init__(self):
        self.sub_socket = _global_context.socket(zmq.SUB)
        # If running on the same Pi, use 127.0.0.1. 
        # If running on a laptop, use the Pi's IP.
        self.sub_socket.connect("tcp://127.0.0.1:5555")
        self.sub_socket.subscribe("")  # Subscribe to all topics
        self.current_state = None
    
    def update(self):
        """Process all pending messages and update state (non-blocking)."""
        try:
            while True:
                try:
                    msg = self.sub_socket.recv_json(flags=zmq.NOBLOCK)
                    if msg.get("topic") == "MISSION_STATE":
                        self.current_state = msg.get("state")
                except zmq.Again:
                    # No more messages available
                    break
        except Exception as e:
            print(f"Error receiving state: {e}")
    
    def get_state(self):
        """Return the current vehicle state."""
        return self.current_state

class _CTESender:
    """Manages persistent ZMQ connection for sending CTE (Cross-Track Error) data."""
    
    def __init__(self):
        self.pub_socket = _global_context.socket(zmq.PUB)
        # If running on the same Pi, use 127.0.0.1. 
        # If running on a laptop, use the Pi's IP.
        self.pub_socket.connect("tcp://127.0.0.1:5556")
        # Small delay to ensure connection is established before sending
        time.sleep(0.1)
    
    def send_cte(self, cte_meters):
        """Send CTE data to the server (non-blocking)."""
        try:
            msg = {
                "topic": "CTE",
                "cte": cte_meters
            }
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"Error sending CTE: {e}")

_state_manager = _VehicleStateManager()
_cte_sender = _CTESender()

def get_vehicle_state():
    """Return the current vehicle state from the MISSION_STATE topic.
    
    This function uses a persistent socket initialized once at module load,
    so it can be called frame-by-frame with zero latency and no TCP overhead.
    """
    _state_manager.update()
    return _state_manager.get_state()

def send_cte_to_server(cte_meters):
    """Send the CTE in meters to the server.
    
    Uses a persistent socket initialized once at module load for zero latency
    and efficient frame-by-frame sending.
    
    Parameters
    ----------
    cte_meters : float
        Cross-Track Error in meters
    """
    _cte_sender.send_cte(cte_meters)
```

## Next Steps

- [ ] Once the `detect_lane_cte(image)` code is complete and ready to be tested, this code will also be tested simultaneously to see if the vehicle state and CTE are
      retrieved and sent successfully.

## References

- `Perception/lane_detection_and_cte.py` 
- `Perception/perception_server_comms.py`
- `Perception/detect_objects.py`
- Commit `07ab96d`

## Reflection
This weekend's work on improving the lane detection code, making the Perception pipeline modular, and enabling communication between the Perception Pipeline and the
server has placed the Perception team in a strong position to begin testing its lane detection and CTE code on the track. Optimizing the lane detection and PID parameters
will require close collaboration and immense testing with the Control team (Rafael) due to the integration of these two systems and the numerous edge cases that need
to be considered. Although future modifications will be required upon testing, this design process illustrates the importance of having ready-to-go code to maximize
testing and optimization time. Furthermore, it highlights how in complex engineering design projects, there is a large dependency of systems on one another, and consequently,
to fully optimize performance, teams must work together in a timely manner.

---

**Entry completed**: 2026-03-02
