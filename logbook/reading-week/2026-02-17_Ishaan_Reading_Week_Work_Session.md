---
title: "Reading Week Work Session Log - Perception: Data Annotation, Object Detection Distance Calculations, Lane Detection"
date: 2026-02-17
week: Reading-week
hours: 6.0
tags: [Perception, Data Annotation, Object Detection, Lane Detection]
contributors: [Ishaan Grewal]
---

# Reading Week Work Session Log: Summary of All Work Completed During Reading Week

## Objectives

- Label and annotate the Stop Sign class (50), Do Not Enter Sign Class (50), and Duck Class (100) using MakeSense AI
- Develop a Python script to calculate the distance to each detected object per frame
- Develop a Python script to perform the lane detection pipeline (color thresholding/masking, BEV transform, polynomial fitting, CTE, etc.)
- Work with Nolan on object detection model validation

## Detailed Work Log

### Session 1: [Data Annotation] (2026-02-17, 17:00 - 19:00)

**Members Present**: [Ishaan Grewal]

**Description**: Labelled and annotated the following object classes using MakeSense AI (numbers indicate quantity of images): Stop Sign class (50), 
Do Not Enter Sign Class (50), and Duck Class (100). Ensured all bounding boxes were as close to the object as possible. Completed in Pascal VOC ZML format.

**Materials/Tools Used**:
- MakeSense AI: https://www.makesense.ai/

**Process/Steps**:
1. Downloaded all images for each object class onto local machine from the PiCar.
2. Loaded all of the images into MakeSense AI, selected "object detection", and created appropriate labels list.
3. Created rectangular bounding boxes around each object, ensuring the box was as close to the object as possible to minimize background noise.
4. Selected the appropriate label from the list.
5. Once complete all labels and annotations, exported them in Pascal VOC ZML format in a zip file.
6. Uploaded all 3 zip files to the repository to share with Nolan: `Perception/Annotations`

**Documentation**:
- `Perception/Annotations/DNE_Annotations.zip`
- `Perception/Annotations/Duck_Annotations.zip`
- `Perception/Annotations/Stop_Annotations.zip`

### Session 2: [Object Detection Distance Calculations] (2026-02-18, 23:25 - 24:00)

**Members Present**: [Ishaan Grewal]

**Description**: Modified the provided *detect_objects.py* file to calculate the distance to each object that is detected in each frame. Defined necessary real world
object heights, create a *compute_distance* function, and added necessary code to the primary loop.

**Calculations:** Calculated the distance to each object using the following formula: 
$$Distance = \frac{Real\ Height\ of\ Object \times f_y}{Pixel\ Height\ of\ Object}$$

**Code Snippets:**

```python
# Define object real heights in meters - note this is the height of the trained portion of the objects
REAL_HEIGHTS = {
    "Stop": 0.05,
    "One-Way": 0.025,
    "Yield": 0.047,
    "DNE": 0.04,
    "Duck": 0.03
}

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
```
**References:**
- `Perception/detect_objects.py`
- Commits: `6a58326`

**Next Steps:**
- [ ] Need to use this script to experimentally determine/test the accuracy and error ranges of the distance calculations.
- [ ] If error in distance calculations are large, then perhaps recalibrate camera to obtain a more accurate y focal length.

### Session 3: [Lane Detection] (2026-02-21, 19:00 - 22:30)

**Members Present**: [Ishaan Grewal]

**Description**: Developed a *lane_detection_and_cte.py* script to implement complete lane detection and Cross Track Error (CTE) calculations. Currently, the script
is using images of the lanes that were taken at the track for development and testing purposes. Once the Perception and Control teams review the outputs from the script
and its potential integration with the Control PID loop, the script will be modularized into key functions and integrated into the *detect_objects.py* file for real 
time frame by frame processing. 

**High Level Pipeline Description:** Load in image, convert to HSV, complete green color thresholding, clean green mask, BEV (Bird's Eye View) transform, lane pixel
extraction and polynomial fitting, CTE calculation, and visualization.

**Code:**
```python
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
```
**Calculations:**
A second degree polynomial was fit to the lane pixels, plotting x as a function of y. Plugging the reference/look ahead y value into this formula returns the x location of the lane: 
$$x = ay^2 + by + c$$

The following formulas were used to calculate the CTE in pixels, and then convert to meters: 
$$cte_{pixels} = \text{float}(car_{center\_x}) - lane_x$$
$$cte_{meters} = cte_{pixels} \cdot meters\_per\_pixel$$

**Results:**
The above code was tested using the images that were taken on the track, which are found at `Perception/Lane_Pictures`. In the results shown below, there are five images.
- "Original" is the image from the camera
- "HSV" is the original image converted to the HSV color space
- "Green Mask" displays the filtered green color thresholding for the lane pixels
- "BEV" displays the computed Bird's Eye View transform
- "Lane Detection" displays from a BEV perspective, the following: The blue line is the center of the car/camera, the dotted red curve is the lane fitted curve, and the
  green dot represents the y reference/look ahead point from which the CTE is being calculated.

Below is a screenshot of the results for `Perception/Lane Pictures/lanes_1_.png`:
![Alt Text](/Perception/Lane_Pictures/lanes1_test.png)

Below is a screenshot of the results for `Perception/Lane Pictures/lanes_2_.png`:
![Alt Text](/Perception/Lane_Pictures/lanes2_test.png)

**Discussion of Results & Next Steps:**
Overall, the preliminary lane detection script is able to successfully isolate and identify the green center tape, complete a BEV transform, fit an accurate polynomial to the curve, and compute a CTE.

Once the Perception and Control teams review these results, both teams will need to discuss/test the following key points/questions:
- What the output to the Control loop will be (CTE in meters, most likely)
- How the Control loop will use the CTE. Will it be a weighted combination with the grayscale sensor? If so, what are the weights? Or will CTE be used in sections of the track where grayscale is known to have issues or fail?
- Whether the camera will be rotated left or right during operation. This is not ideal for lane detection since the image center would no longer represent the vehicle's forward direction, and we would lose lateral reference. 
- Need to experimentally determine the *meters_per_pixel*
- Need to discuss and test the most optimal *y_ref* distance. Do we want to dynamically change this based on location? For example, reduce the look-ahead for a curve? This is recommended since on a sharp curve, the point may be far or not even on the curve, which can cause a large CTE. A suggested solution is that from the polynomial, we can find the curvature (a coefficient) and threshold *y_ref* for varying values. Or, we can use continuous adaptation, which changes the *y_ref* based on the curvature.

**References:**
- `Perception/Lane_Pictures`
- `Perception/lane_detection_and_cte.py`

## Reflection
This week's progress has placed the Perception team in a strong position relative to our reading week and overall project milestones, transitioning from data labelling to a functional, quantitative perception pipeline. This work has highlighted the software's reliability on physical calibration, such as the sensitivity of distance calculations to the focal length. This realization, and the planned next steps, reveal the need for intensive cross-team testing between Perception and Control. We have reached a point where software can no longer be developed in isolation. Clear constraints, such as whether the camera mount remains fixed or pans, how the *y_ref* distance is determined, and how Perception and Control interface are crucial to define. The next phase will focus on defining the above topics of discussion, determining how the PID loop interprets these CTE values, and iteratively testing these interactions to ensure the car's "vision" translates to smooth and efficient steering.

---

**Entry completed**: 2026-02-23
