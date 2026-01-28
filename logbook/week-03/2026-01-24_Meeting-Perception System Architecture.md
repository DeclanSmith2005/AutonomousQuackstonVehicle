---
title: "Perception System Architecture Meeting"
date: 2026-01-24
week: 3
hours: 8.0
tags: Perception
contributors: Ishaan Grewal, Nolan Su-Hackett
---

## Meeting Information

**Date:** 2026-01-24  
**Time:** 18:00 – 22:00  
**Duration:** 4.0 hours  
**Location:** Microsoft Teams Call  
**Meeting Type:** Design Review, Sprint Planning

### Attendees

- ✅ Ishaan Grewal - Perception Co-Lead
- ✅ Nolan Su-Hackett - Perception Co-Lead

---

## 📝 Discussion Summary

### 1. Perception Scope & Training Pipeline: Model Data

**Context:**  
This discussion item pertained to discussing what responsibilities fell under the perception team and defined the data section of the training pipeline.

**Key Points Discussed & Decisions Made:**
- Identified that the scope of the perception team was to develop an object detection model to detect: signs (stop, yield, one-way, and do not enter), road markings
  (crosswalks, two-way roads, one-way roads, and intersections/stop lines), ducks, other vehicles, and construction cones. Additionally, the team would be responsible
  to acquire and interpret raw data from ultrasonic and grayscale line following sensors.
- Defined each of the above as unique classes.
- Defined where class training data will be sourced from. For all road signage, this will be a mix of online training data (due to the similarities with North American signage)
  and custom training data. For all other classes, the team will take pictures of these objects using the Raspberry Pi camera module. These pictures will be taken
  under varying lighting conditions, with objects at different angles and distances from the camera to increase diversity in data.
- All classes will be weighted equally to minimize bias.
- Pascal VOC format will be used. To assist with data labelling/annotation, software like Make Sense or Labellmg will be considered.

---

### 2. Training Pipeline: Training and Evaluating the Model

**Context:**  
This discussion item focuses on how train, validation, and test datasets will be created, resources that will be used to train the model, and by what metrics the team
will evaluate the model.

**Key Points Discussed & Decisions Made:**
- The data will be randomly split into training, validation, and testing datasets with a 70%, 20%, and 10% split, respectively.
- The team will use Google Colab to offload training to its GPUs, specifically, T4/L4/A100. The EfficientDet-Lite1 model architecture will be used, rather than Mobilenet
  and MobileDet, since the TensorFlow Lite Model Maker object detection flow is built around EfficientDet-Lite1. Additionally, the team is provided with resources for this.
- YOLO will not be used for simplicity with interfacing with the Coral, and due to the ease of Pascal VOC format.
- The primary metrics for evaluating the model will be mAP (mean average precision) and mAR (mean average recall) at various IoU thresholds (>0.5, 0.5-0.95, >0.75).
- The mAP and mAR will be averaged through all IoU thresholds for a final overall value.
- Based on research, a precision and recall value of 0.8 is widely considered a strong model. However, the team identified that it is important to consider which
  metric matters more for a specific class.
- Each class will have their own target mAR and mAP. A cumulative rating of 1.6 (0.8 base for each metric) will be used.
- The team then defined the following targets for each class, by considering redundancies and where FNs or FPs are more important.
<img width="797" height="132" alt="image" src="https://github.com/user-attachments/assets/d2baefdb-14c1-405d-b798-80fac2e9c36f" />
- Created the following flowchart for the training pipeline and procedure.
<img width="775" height="847" alt="image" src="https://github.com/user-attachments/assets/71778532-c89c-4e00-9a0c-ec0538e0554f" />


**Resources Used**:
https://blog.roboflow.com/mean-average-precision/

---

### 4. Object Detection & Sense Pipelines

**Context:**
Next, the team focused on planning and defining the perception system architecture into object detection and sense pipelines, each with their own sublayers.

**Key Points Discussed & Decisions Made:**
- Separated the object detection pipeline into: data acquisition, perception, and abstraction layers.
- Defined inputs and outputs of each layer, and how they interact with the other.
- Decided that for certain classes (excluding lanes), the system pipeline will check if the object is detected in adjacent frames to help prevent false detections.
- Separated the sense pipeline into data acquisition and abstraction layers.
- Created flowcharts for both pipelines, as shown below.
<img width="904" height="1235" alt="image" src="https://github.com/user-attachments/assets/daa4457f-2107-4850-921b-95b21cc6d949" />
<img width="975" height="227" alt="image" src="https://github.com/user-attachments/assets/8514365a-d6da-404c-b4de-94881c737db2" />

---

---

**Minutes prepared by:** [Note Taker Name]  
**Date submitted:** YYYY-MM-DD  
**Reviewed by:** [Facilitator Name]
