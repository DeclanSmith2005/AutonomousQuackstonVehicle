---
title: "[Descriptive Title of Your Work]"
date: 2026-02-03
week: 5
hours: 8.0
tags: [Perception, Object Detection, Camera Testing]
contributors: [Nolan Su-Hackett, Ishaan Grewal]
---

# Daily Logbook Entry Template

## Objectives
- Attempt the European Road Sign Detection git colab tutorial
- Test the european road sign model on the stop sign because its dataset includes it.
- Get the camera intrinsics 

## Detailed Work Log

### Session 1: [Object Detection Model] (14:30 - 16:30)

**Members Present**: [Nolan Su-Hackett, Ishaan Grewal]

**Description**: 
Downloaded Dataset files and model training files and followed through with the Git Colab tutorial on the model. Following the creation of the model the perception team used FileZilla to port the model to the car. When attempting to use the model using the guide in the git colab the team ran into some issues. The team tried to run the following command: 
cd ~/dev/elec392_project
python projects/object_detector_visual.py \
    --model efficientdet-lite-road-signs_edgetpu.tflite \
    --labels road-signs-labels.txt \
    --confidence 0.5
This was the command that was featured in the git colab tutorial but the team ran into problems with the way the flags were being passed. Since this was the in-lab session 
the team asked Professor Paulo and he stated that the gitbook was a bit outdated and that they were working on updating it. The Professor gave the team some direction and some supporting code to help draw the bounding boxes and it was after his support that the european road sign model started working on the stop sign.

**Materials/Tools Used**:
- Git Colab
- GitBook
- Filezilla

**Documentation**:
[Object Detection Image](https://github.com/ELEC-392/elec-392-project-duclair_2/tree/main/images/week-05)
If the hyperlink doesnt work, the image is located in images/week-05, and it is a image of a successful bounding box being drawn around the stop sign live from the car.

### Session 2: [Activity Name] (14:30 - 16:30) (Thursday February 5, 2026)

**Members Present**: [Nolan Su-Hackett, Ishaan Grewal]

**Description**:
Getting Camera Intrinsics and applying the undistortoin algorithm if distortion coefficients are large enough. The team downloaded the 8x8 chessboard, printed it and taped it to a surface with a clear background in good lighting then took pictures at different angles using the car camera. Following this the perception team ran the provided code in the gitbook to generate the camera intrinsics and ended up with the matrix shown in the results and data section.
## Results & Data

Intrinsic Matrix (K):
[[616.00734472   0.         315.68903815]
[  0.         616.13761171 240.13728793]
[  0.           0.           1.        ]]
Distortion Coefficients:
[[ 1.68173299e-01 -3.17096292e-01  1.45129091e-04  5.91506437e-05
  -1.84317820e+00]]
Total Re-Projection Error (Pixels): 0.05300225203845394

### Measurements/Observations
Total re-projection error was 0.05 which is the average pixel arror between observed chessboard corners and the projected corners from the calibration model. This is an acceptable error and means that it would not be worth the extra computation to undistort images at every frame.

## Challenges & Solutions

### Challenge 1: [Git Colab Instructions Outdated]

**Problem**: 
The instructions on the git colab notebook were outdated
**Debugging Steps**:
1. Attempted searching up the error message 
2. Consulted Professor Paulo

**Solution**:
Professor Paulo provided the missing code that allowed the team to generate bounding boxes around detected images. He also provided insight on the python file to run and how to make it so that models and labesl can be interchanged at will.


**Lessons Learned**: 
These sessions highlighted the importance of using all resources at your disposal including researching tools aswell as consulting those with more experience. Professor Paulo helped us greatly as he was able to confirm that we were not on the wrong track as he tested his bounding box code on his computer with our model. His insights spared the team debugging time and helped lead us in the correct direction. Something that was learned in the second session was that it is important to double check intrinsics and parameters even if things seem to be fine. Checking camera distortion and intrinsics can save the team time later with narrowing down sources of error, as we can discard distortion as a source of error. 
## Next Steps

- [ ] Take images of objects so that the team can create an object detection model

**Entry completed**: 2026-03-03 00:29
