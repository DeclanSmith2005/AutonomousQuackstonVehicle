import cv2
import numpy as np

# Read the image
image = cv2.imread("lanes_2_.jpg")
height, width = image.shape[:2] # in pixels, width should be 640 and height should be 480, (0, 0) is top-left

# Convert to HSV (Hue = Color, Saturation = Color Intensity, Value = Brightness) color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Green color thresholding for lane segementation
lower_green = np.array([40, 80, 80])  # lower bound for green color
upper_green = np.array([80, 255, 255])  # upper bound for green color
mask = cv2.inRange(hsv, lower_green, upper_green) # white pixels represent green lane, everything else is black

# Clean green mask
kernel = np.ones((5, 5), np.uint8)
# Morphological opening removes small dots from the background by eroding objects smaller than the kernel and then dilating the remaining objects back to their original size.
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
# Morphological closing fills small black holes in white objects by dilating the objects and then eroding them back to their original size.
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

# BEV (Bird's Eye View) transformation
src_points = np.float32([   # change top and bottom points to change distance that is analyzed
    [200, 300], # top-left, 62.5% of the height, which is 37.5% up from the bottom
    [440, 300], # top-right, 62.5% of the height, which is 37.5% up from the bottom
    [50, 470], # bottom-left
    [590, 470]  # bottom-right
])

dst_points = np.float32([
    [150, 0],   # top-left
    [490, 0],   # top-right
    [150, 480], # bottom-left
    [490, 480]  # bottom-right
])

M = cv2.getPerspectiveTransform(src_points, dst_points) # transformation matrix
bev = cv2.warpPerspective(mask, M, (width, height))

# Extract lane pixels
ys, xs = np.nonzero(bev)

# Fit polynomial to lane pixels
if len(xs) > 0 and len(ys) > 0:
    poly = np.polyfit(ys, xs, 2)  # Fit a second degree polynomial, x as a function of y: x = a*y^2 + b*y + c
    print("Polynomial coefficients:", poly)
a, b, c = poly

# Calculate Cross Track Error (CTE)
y_ref = int(height * 0.8)  # reference point at 80% of the image height, which is 20% up from the bottom and where we want to be centered on the lane
meters_per_pixel = 0.1  # need to experimentally determine this by dividing real lane width by pixel lane width in the image
lane_x = a*y_ref*y_ref + b*y_ref + c
car_center_x = width // 2
cte_pixels = float(car_center_x) - lane_x
cte_meters = cte_pixels * meters_per_pixel
print("Cross Track Error (pixels):", cte_pixels)
print("Cross Track Error (meters):", cte_meters)

# Add visualization
output = cv2.cvtColor(bev, cv2.COLOR_GRAY2BGR)
# Red points for lane curve
for y in range(0, height, 5):
    x = int(a*y*y + b*y + c)
    if 0 <= x < width:
        cv2.circle(output, (x, y), 2, (0, 0, 255), -1)

# Blue center line
cv2.line(output, (int(car_center_x), 0), (int(car_center_x), height), (255, 0, 0), 2)

# Green point at reference
cv2.circle(output, (int(lane_x), y_ref), 8, (0, 255, 0), -1)

cv2.imshow("Original", image)
cv2.imshow("HSV", hsv)
cv2.imshow("Green Mask", mask)
cv2.imshow("BEV", bev)
cv2.imshow("Lane Detection", output)
cv2.waitKey(0)
cv2.destroyAllWindows()