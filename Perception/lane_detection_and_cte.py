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

# Centimeters per pixel for trajectory output
cm_per_pixel_straight = meters_per_pixel_straight * 100  # ~0.046 cm/pixel

#---------------------------------------------------------------MAIN CODE----------------------------------------------------------------------

def get_trajectory_points(image, num_points=10):
    """Extract CTE at multiple lookahead distances for curve following during turns.
    
    Parameters
    ----------
    image : np.ndarray
        BGR image from camera.
    num_points : int
        Number of trajectory points to sample (default: 10).
    
    Returns
    -------
    list or None
        List of (distance_cm, cte_cm) tuples from near to far, or None if detection fails.
        Positive CTE = lane is to the right of car center.
    """
    height, width = image.shape[:2]
    
    # Convert to HSV and threshold for green
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Clean mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    # BEV transformation
    bev = cv2.warpPerspective(mask, M_straight, (width, height))
    
    # Get all lane pixels
    ys, xs = np.nonzero(bev)
    
    if len(xs) < 50:  # Need enough pixels for reliable fit
        return None
    
    # Fit polynomial: x = ay^2 + by + c
    try:
        poly = np.polyfit(ys, xs, 2)
    except np.linalg.LinAlgError:
        return None
    
    a, b, c = poly
    car_center_x = width // 2
    
    trajectory = []
    # Sample from near (90% height) to far (30% height)
    for i in range(num_points):
        y_frac = 0.9 - (i * 0.06)  # 0.9, 0.84, 0.78, ... ~0.36
        y = int(height * y_frac)
        
        lane_x = a * y * y + b * y + c
        cte_pixels = float(car_center_x) - lane_x
        cte_cm = cte_pixels * cm_per_pixel_straight
        
        # Estimate distance ahead based on BEV position (rough approximation)
        # Bottom of BEV (~y=height) is ~0cm ahead, top (~y=0) is ~30cm ahead
        distance_cm = (0.9 - y_frac) * 50  # Range: 0 to ~30cm
        
        trajectory.append((round(distance_cm, 1), round(cte_cm, 2)))
    
    return trajectory


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
    image = cv2.imread("lanes_1_.jpg")
    if image is None:
        raise RuntimeError("failed to read test image")
    cte_px, cte_m, vis = detect_lane_cte(image)
    print(f"cte: {cte_px} px, {cte_m} m")
    if vis is not None:
        cv2.imshow("Lane Detection", vis)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
