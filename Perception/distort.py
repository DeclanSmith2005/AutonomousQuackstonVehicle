# import cv2 as cv
# import numpy as np

# # Load image
# img = cv.imread("PI_CAM_20260205_155219070052.jpg")
# h, w = img.shape[:2]

# # Camera Calibration Results
# # K = np.array([
# #     [fx,  0, cx],
# #     [ 0, fy, cy],
# #     [ 0,  0,  1]
# # ]

# K = np.array([
#     [616.00734472,  0, 315.68903815],
#     [ 0, 616.13761171, 240.13728793],
#     [ 0,  0,  1]
# ], dtype=np.float64)

# dist = np.array([1.68173299e-01, -3.17096292e-01, 1.45129091e-04, 5.91506437e-05, -1.84317820e+00], dtype=np.float64)

# alpha = 0.2

# new_camera_matrix, roi = cv.getOptimalNewCameraMatrix(
#     cameraMatrix=K,
#     distCoeffs=dist,
#     imageSize=(w, h),
#     alpha=alpha,
#     newImgSize=(w, h),
#     centerPrincipalPoint=False
# )

# undistorted = cv.undistort(
#     src=img,
#     cameraMatrix=K,
#     distCoeffs=dist,
#     newCameraMatrix=new_camera_matrix
# )

# x, y, roi_w, roi_h = roi
# undistorted_cropped = undistorted[y:y+roi_h, x:x+roi_w]

# cv.imwrite("calibresult.png", undistorted_cropped)

import cv2 as cv
import numpy as np

# Load image
img = cv.imread("PI_CAM_20260205_155219070052.jpg")
if img is None:
    raise IOError("Image not found")

h, w = img.shape[:2]

# Camera intrinsic matrix
K = np.array([
    [616.00734472, 0, 315.68903815],
    [0, 616.13761171, 240.13728793],
    [0, 0, 1]
], dtype=np.float64)

# Distortion coefficients
dist = np.array([
    1.68173299e-01,
   -3.17096292e-01,
    1.45129091e-04,
    5.91506437e-05,
   -1.84317820e+00
], dtype=np.float64)

# Try multiple alpha values
for alpha in [0.0, 0.2, 1.0]:

    newK, roi = cv.getOptimalNewCameraMatrix(
        cameraMatrix=K,
        distCoeffs=dist,
        imageSize=(w, h),
        alpha=alpha
    )

    undistorted = cv.undistort(
        img, K, dist, None, newK
    )

    # Draw border so black regions are obvious
    cv.rectangle(
        undistorted,
        (0, 0),
        (undistorted.shape[1]-1, undistorted.shape[0]-1),
        (0, 0, 255),
        5
    )

    print(f"alpha={alpha}, roi={roi}")
    cv.imwrite(f"calib_alpha_{alpha}.png", undistorted)
