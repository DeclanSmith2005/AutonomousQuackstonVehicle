---
title: "Perception System Architecture Meeting"
date: 2026-01-24
week: 3
hours: X.X
tags: Perception
contributors: Ishaan Grewal, Nolan Su-Hackett
---

## Meeting Information

**Date:** 2026-01-24  
**Time:** HH:MM – HH:MM  
**Duration:** X.X hours  
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
- Pascal VOC format will be used. To assist with data labelling/annotation, softwares like Make Sense or Labellmg will be considered.

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

**Resources Used**:
https://blog.roboflow.com/mean-average-precision/

---

### 4. Object Detection & Sense Pipelines

**Context:**
Next, the team focused on planning and defining the perception system architecture into object detection and sense pipelines, each with their own sublayers.

**Key Points Discussed & Decisions Made:**
- 
- 

---

## ✅ Decisions & Outcomes

### Technical Decisions

| Decision | Rationale | Impact | Alternatives Considered |
|----------|-----------|--------|------------------------|
| Choice made | Why this was chosen | What it affects | Other options |
| | | | |

### Project Decisions

| Decision | Rationale | Impact |
|----------|-----------|--------|
| | | |

---

## 📦 Action Items & Next Steps

### Immediate Actions (This Week)

- [ ] **[Name 1]** - Task description with specific deliverable - **Due:** YYYY-MM-DD
- [ ] **[Name 2]** - Another specific task - **Due:** YYYY-MM-DD
- [ ] **[Name 3]** - Yet another task - **Due:** YYYY-MM-DD

### Upcoming Actions (Next Week+)

- [ ] **[Name]** - Future task - **Due:** YYYY-MM-DD
- [ ] **[Team]** - Collaborative task - **Due:** YYYY-MM-DD

### Blocked Items

- ⛔ **[Name]** - Task description - **Blocker:** What's preventing progress
- ⛔ **[Name]** - Another blocked item - **Blocker:** Dependency or issue

---

## 🅿️ Parking Lot

Items that need follow-up but are not immediate priorities:

- Item 1 - Discussed briefly, needs deeper investigation
- Item 2 - Good idea but out of scope for current sprint
- Item 3 - Question that requires research before deciding

---

## 📊 Project Status

### Overall Progress

- **On Track** / **At Risk** / **Behind Schedule**
- Brief explanation if not on track

### Milestones

| Milestone | Target Date | Status | Notes |
|-----------|-------------|--------|-------|
| Milestone 1 | YYYY-MM-DD | ✅ Complete | |
| Milestone 2 | YYYY-MM-DD | ⚠️ In Progress | |
| Milestone 3 | YYYY-MM-DD | ⏳ Upcoming | |

---

## 🎯 Next Meeting

**Date:** YYYY-MM-DD  
**Time:** HH:MM  
**Location:** [TBD]  

**Proposed Agenda:**
1. Review action items from this meeting
2. Topic 1
3. Topic 2

---

## 📎 Attachments & References

- [Link to design doc](URL)
- [Link to GitHub issue](URL)
- [Reference material](URL)
- Images or diagrams: ![Description](../../images/week-XX/filename.jpg)

---

## 💬 Additional Notes

Any other observations, concerns, or information that doesn't fit into the above categories.

---

**Minutes prepared by:** [Note Taker Name]  
**Date submitted:** YYYY-MM-DD  
**Reviewed by:** [Facilitator Name]
