import cv2
import numpy as np
from perception_server_comms import get_vehicle_state, send_cte, send_distance_to_line_to_server

#---------------------------------------------------------------CONSTANTS---------------------------------------------------------------------
# Green color range for lane detection in HSV color space
lower_green = np.array([40, 80, 80])  # lower bound for green color
upper_green = np.array([80, 255, 255])  # upper bound for green color

# BEV source points for perspective transformation for each vehicle state (right turn, left turn, or straight)
src_points_straight = np.float32([   # change top and bottom points to change distance that is analyzed
    [200, 300], # top-left
    [440, 300], # top-right
    [50, 470],  # bottom-left
    [590, 470]  # bottom-right
])

src_points_turn = np.float32([   # change top and bottom points to change distance that is analyzed
    [200, 100], # top-left
    [440, 100], # top-right #
    [50, 470],  # bottom-left
    [590, 470]  # bottom-right

    # [200, 200], # top-left
    # [440, 200], # top-right #
    # [50, 470],  # bottom-left
    # [590, 470]  # bottom-right
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
M_turn = cv2.getPerspectiveTransform(src_points_turn, dst_points)

# Meters per pixel conversion factor
meters_per_pixel_straight = 0.00046296296  # 0.025m/54 pixels (x-direction CTE)
meters_per_pixel_y = 0.00046296296  # Same scale assumption - tune as needed

# Parameters for horizontal line detection when no_line == True
HORIZONTAL_MIN_PIXEL_COUNT = 80  # minimum number of total pixels in the horizontal line
HORIZONTAL_MIN_SPAN_PX = 20  # minimum span in pixels for a horizontal line to be considered
PEAK_ALIGN_TOLERANCE = 50  # tolerance for aligning peaks in horizontal line detection
STOPLINE_MAX_SLOPE = 30  # maximum slope for a line to be considered a stop line
STOPLINE_MAX_MEAN_RESIDUAL_PX = 80  # maximum mean residual in pixels for a line to be considered a stop line

#---------------------------------------------------------------MAIN CODE----------------------------------------------------------------------

def detect_lane_cte(image):
    """
    Detect lane and compute Cross-Track Error (CTE) at multiple lookahead distances.
    
    Returns:
        (cte_meters_list, distance_meters_list, output_image, bev, distance_to_line)
        - cte_meters_list: list of 10 CTE values in meters (+ = lane right of center)
        - distance_meters_list: list of 10 lookahead distances in meters (near to far)
        - output_image: visualization BGR image
        - bev: bird's eye view mask
        - distance_to_line: distance from car to the line that is found for the no_line flag
        If detection fails: (None, None, None, None, None)
    """
    # Get current vehicle state from server (ST, R, L) and no_line/stopped flags
    vehicle_state, no_line, stopped = get_vehicle_state()
    distance_to_line = None

    height, width = image.shape[:2]

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Green color thresholding for lane segmentation
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Clean green mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # BEV transformation based on vehicle state
    if vehicle_state == "ST":
        return None, None, None, None, None # not being implemented for now
        bev = cv2.warpPerspective(mask, M_straight, (width, height))
    elif vehicle_state == "R" or vehicle_state == "L1" or vehicle_state == "L2":
        bev = cv2.warpPerspective(mask, M_turn, (width, height))
    else:
        return None, None, None, None, None

    # When no_line == True, we do not want to find cte, and want to find if there is a horizontal line intersecting our path, and if so,
    # how far away it is. This is used to determine if we are approaching a "stop" line that we need to find.
    if no_line:
        bev = cv2.warpPerspective(mask, M_straight, (width, height)) # when looking for a line, the camera is not tilted down
        bottom_region = bev[int(height * 0.8): height, :]
        ys_bottom, xs_bottom = np.nonzero(bottom_region)

        if len(xs_bottom) > 0:
            lane_center_x = int(np.mean(xs_bottom))
        else:
            lane_center_x = width // 2
              
        # Vertical exclusion zone
        roi_half_width = 54
        l = max(lane_center_x - roi_half_width, 0)
        r = min(lane_center_x + roi_half_width, width)

        # Create a mask that excludes the vertical path 
        # We look to the left and right of the path to find the "arms" of a horizontal line
        mask_horizontal = np.zeros_like(bev)
        mask_horizontal[:, :l] = 255 # Left of path
        mask_horizontal[:, r:] = 255 # Right of path

        # Apply mask and find pixels
        bev_horizontal_only = cv2.bitwise_and(bev, mask_horizontal)
        ys, xs = np.nonzero(bev_horizontal_only)

        if len(ys) > 0:
            left_mask = xs < l # left arm of horizontal line
            right_mask = xs >= r # right arm of horizontal line
            
            has_left = np.any(left_mask)
            has_right = np.any(right_mask)
            
            if has_left or has_right:
                ys_left = ys[left_mask] if has_left else []
                ys_right = ys[right_mask] if has_right else []
                
                hist_left = np.bincount(ys_left, minlength=height) if has_left else np.zeros(height, dtype=int)
                hist_right = np.bincount(ys_right, minlength=height) if has_right else np.zeros(height, dtype=int)

                left_peak_y = int(np.argmax(hist_left)) if has_left else None
                right_peak_y = int(np.argmax(hist_right)) if has_right else None
                
                left_peak_count = int(hist_left[left_peak_y]) if has_left else 0
                right_peak_count = int(hist_right[right_peak_y]) if has_right else 0

                if has_left and has_right:
                    peaks_aligned = abs(left_peak_y - right_peak_y) <= PEAK_ALIGN_TOLERANCE # see if left and right peaks are roughly at the same y value
                    line_y = int((left_peak_y + right_peak_y) / 2)
                elif has_left:
                    peaks_aligned = True
                    line_y = left_peak_y
                elif has_right:
                    peaks_aligned = True
                    line_y = right_peak_y

                line_strong = (left_peak_count + right_peak_count) >= HORIZONTAL_MIN_PIXEL_COUNT # see if there are enough pixels in the overall line

                if peaks_aligned and line_strong:
                    print("peaks aligned and line strong")
                    row_x = np.nonzero(bev_horizontal_only[line_y, :])[0]
                    row_span_ok = len(row_x) > 0 and int(np.max(row_x) - np.min(row_x)) >= HORIZONTAL_MIN_SPAN_PX
                    if row_span_ok:
                        print("row span is ok")
                        # Fit a line to pixels near peak rows and reject curved/noisy structures.
                        band = 40 # Reduced from PEAK_ALIGN_TOLERANCE to avoid including vertical lane lines in the line fitting
                        y_low = max(0, line_y - band)
                        y_high = min(height, line_y + band + 1)
                        ys_band, xs_band = np.nonzero(bev_horizontal_only[y_low:y_high, :])

                        if len(xs_band) >= 25:
                            ys_world = (ys_band + y_low).astype(np.float32)
                            xs_world = xs_band.astype(np.float32)
                            pts = np.column_stack((xs_world, ys_world)).astype(np.float32)
                            vx, vy, x0, y0 = cv2.fitLine(pts, cv2.DIST_L2, 0, 0.01, 0.01)

                            vx = float(vx)
                            vy = float(vy)
                            x0 = float(x0)
                            y0 = float(y0)
                            slope = float("inf") if abs(vx) < 1e-6 else (vy / vx)

                            if abs(slope) <= STOPLINE_MAX_SLOPE:
                                print("line slope is ok")
                                y_pred = y0 + slope * (xs_world - x0)
                                mean_residual = float(np.mean(np.abs(ys_world - y_pred)))
                                if mean_residual <= STOPLINE_MAX_MEAN_RESIDUAL_PX:
                                    print("residual is ok")
                                    distance_to_line = (height - line_y) * meters_per_pixel_straight
                                    send_distance_to_line_to_server(distance_to_line)
        # If no horizontal line was found, send explicit None so control knows
        # perception is actively scanning but hasn't detected a line yet.
        if distance_to_line is None:
            send_distance_to_line_to_server(None)
        return None, None, None, bev, distance_to_line

        # If no horizontal line was found
        # return None, None, None, None, None

    # Filter lane pixels based on vehicle state -- when no_line == False
    if vehicle_state == "ST":
        bottom_region = bev[int(height * 0.8): height, :]
        ys_bottom, xs_bottom = np.nonzero(bottom_region)

        if len(xs_bottom) > 0:
            lane_center_x = int(np.mean(xs_bottom))
        else:
            lane_center_x = width // 2

        roi_half_width = 54
        mask_roi = np.zeros_like(bev)
        l = max(lane_center_x - roi_half_width, 0)
        r = min(lane_center_x + roi_half_width, width)
        mask_roi[:, l:r] = 255

        bev_roi = cv2.bitwise_and(bev, mask_roi)
        ys, xs = np.nonzero(bev_roi)

    elif vehicle_state == "R" or vehicle_state == "L1" or vehicle_state == "L2":
        bottom_region = bev[int(height * 0.8): height, :]
        ys_bottom, xs_bottom = np.nonzero(bottom_region)

        if len(xs_bottom) > 0:
            lane_center_x = int(np.mean(xs_bottom))
        else:
            lane_center_x = width // 2

        roi_half_width = 54

        # Detect intersection row (same logic for LEFT/RIGHT)
        intersection_y = height - 1
        width_threshold = roi_half_width*3

        for y in range(int(height * 0.5), height):
            row_pixels = np.nonzero(bev[y, :])[0]
            if len(row_pixels) > 0:
                row_width = int(np.max(row_pixels) - np.min(row_pixels))
                if row_width > width_threshold:
                    intersection_y = y
                    # print("Intersection found")
                    break

        mask_turn = np.zeros_like(bev)

        # vertical region of intersection (same for LEFT/RIGHT)
        l = max(lane_center_x - roi_half_width, 0)
        r = min(lane_center_x + roi_half_width, width)
        mask_turn[intersection_y:, l:r] = 255

        if vehicle_state == "L1" or vehicle_state == "L2":
            # Fitting code for L turn
            y0 = intersection_y
            y1 = min(intersection_y + int(2.5 * roi_half_width), height)
            mask_turn[y0: y1, l:] = 255
            #Filtering mini squares
            mask_turn[:int(0.8*height), :int(0.7*width) ] = 0
        else:
            # Fitting code for R turn
            y0 = intersection_y
            y1 = min(intersection_y + int(2.5 * roi_half_width), height)
            mask_turn[y0: y1, :r] = 255
            #Filtering mini squares
            mask_turn[:int(0.8*height), int(0.2*width):] = 0

        # mask_turn[:int(0.8*height), :int(0.8*width) ] = 0 #testing
        bev_roi = cv2.bitwise_and(bev, mask_turn)
        ys, xs = np.nonzero(bev_roi)
        # print("filtering done")
    else:
        return None, None, None, None, None

    if len(xs) == 0 or len(ys) == 0:
        return None, None, None, None, None

    # Fit cubic: x = a*y^3 + b*y^2 + c*y + d
    poly = np.polyfit(ys, xs, 3)
    a, b, c, d = poly

    # -------------------- compute 10 CTE values at 10 y_ref points --------------------
    y_min = int(np.min(ys))  # top-most detected lane pixel (smallest y)
    y_max = int(np.max(ys))  # bottom-most detected lane pixel (largest y)

    margin = int(0.02 * height)  # avoid endpoints (noise/sparsity)
    y_top = min(max(y_min + margin, 0), height - 1)
    y_bottom = 0.8 * height
    #y_bottom = min(max(y_max - margin, 0), height - 1)

    if y_bottom <= y_top:
        return None, None, None, None, None
    
    # Check quality of the fit by looking at the y_top point: if top point is too close, likely bad fit
    if y_top > int(height * 0.7):
        return None, None, None, None, None

    y_refs = np.linspace(y_bottom, y_top, 10).astype(int)

    car_center_x = width // 2
    cte_pixels_list = []
    cte_meters_list = []
    distance_meters_list = []  # Physical distance from car (in meters)
    lane_x_list = []

    # meters-per-pixel selection (replace with per-state if needed)
    mpp = meters_per_pixel_straight

    for y_ref in y_refs:
        lane_x = a * (y_ref ** 3) + b * (y_ref ** 2) + c * y_ref + d

        # sign convention: positive means lane is to the RIGHT of car center
        cte_px = float(lane_x) - float(car_center_x)
        cte_m = cte_px * mpp
        
        # Convert y_ref (pixel row) to physical distance from car
        # In BEV: y=height is near the car, y=0 is far away
        # distance = (height - y_pixel) * meters_per_pixel_y
        distance_m = (height - y_ref) * meters_per_pixel_y

        cte_pixels_list.append(cte_px)
        cte_meters_list.append(cte_m)
        distance_meters_list.append(distance_m)
        lane_x_list.append(lane_x)

    # -------------------- visualization --------------------
    output = cv2.cvtColor(bev_roi, cv2.COLOR_GRAY2BGR)

    # draw polynomial curve
    for y in range(0, height, 5):
        x = int(a * (y ** 3) + b * (y ** 2) + c * y + d)
        if 0 <= x < width:
            cv2.circle(output, (x, y), 2, (0, 0, 255), -1)

    # draw car center line
    cv2.line(output, (int(car_center_x), 0), (int(car_center_x), height), (255, 0, 0), 2)

    # draw the 10 sampled y_ref points
    for y_ref, lane_x in zip(y_refs, lane_x_list):
        x = int(lane_x)
        if 0 <= x < width:
            cv2.circle(output, (x, int(y_ref)), 6, (0, 255, 0), -1)
    print("returning results")
    return cte_meters_list, distance_meters_list, output, bev, distance_to_line


if __name__ == "__main__":
    image = cv2.imread("Stop_0_.jpg")
    if image is None:
        raise RuntimeError("failed to read test image")

    cte_m_list, distance_m_list, vis, bev, distance_to_line = detect_lane_cte(image)

    if cte_m_list is None:
        print("CTE detection failed")
    else:
        print("distance (m):", [round(v, 4) for v in distance_m_list])
        print("cte (m):     ", [round(v, 4) for v in cte_m_list])
        print("distance (cm):", [round(v * 100, 2) for v in distance_m_list])
        print("cte (cm):     ", [round(v * 100, 2) for v in cte_m_list])

    if vis is not None:
        cv2.imshow("Lane Detection", vis)
        cv2.imshow("bevOG", bev)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
