---
title: "Team Contributions - Weekly Work Session #1"
date: 2026-02-24
week: 7
hours: 8.0
tags: [Perception, Control, Planning, Team Sync]
contributors: [Ishaan Grewal, Nolan Su-Hackett, Rafael Costa, Declan Smith]
---

## Daily Summary

As the first team work session following reading week, the beginning of the session served as a team sync, where each individual shared the progress they made on their tasks
over reading week with the rest of the team. Additionally, the team discussed overall subteam project status and future trajectory. The Perception team engaged in valuable discussions
with Professor Paulo Araujo about their lane detection and CTE implementation, gaining important insights and opinions which led to key decisions being made (as discussed below).
The Perception team also focused on testing the trained object detection model and the distance calculations.

---

## Entry – [Ishaan Grewal]

**Time:** 14:30-16:30  
**Activity Type:** Implementation, Testing, Brainstorming/Team Sync  
**Status:** Complete/In progress  
**Estimated Effort:** 2.0 h  

### Work Performed & Decisions Made:

- **Team Sync:** Shared Perception progress with the rest of the team, specifically regarding the lane detection and cross-track error (CTE) implementation that was
  worked on over reading break. During this team sync, I also took time to understand Rafael's server implementation and how Perception would interface with it.
- **Professor Feedback & Resulting Decisions Made:** At the beginning of the work session, I shared the lane detection and CTE work I had completed over reading week
  with Professor Paulo Araujo, seeking his insights and opinions on the questions I had outlined in the reading week entry. Key points discussed included how the Control
  PID loop would use the CTE alongside the current grayscale sensor implementation and best practices with image processing. The following decisions were made from
  this discussion with Professor Paulo: **(1)** The Control PID loop will use a weighted combination of the CTE and grayscale sensor readings to provide efficiency, reliability,
  and a fail-safe solution. Professor Paulo pointed out that the CTE will be far more valuable than the grayscale readings since it is obtained from image processing, and that we
  should rely more on that. Using this advice, we will weigh the CTE more than the grayscale readings. **(2)**  Professor Paulo pointed out that the grayscale sensor operates at
  a much higher frequency compared to the camera's frame rate, and consequently, recommended that, in between these delays in camera lane detection, we rely on the grayscale sensor.
  Upon discussion with the Control team (Rafael), we decided that this would be the best implementation option for us.  
- **Object Detection Model - Implementation & Testing:** In this work session, Nolan and I tested the object detection model we had trained over reading week to evaluate
  its effectiveness for each object class.
- **Object Detection Distance Calculations - Preliminary Testing:** Alongside testing the object detection accuracy, Nolan and I also evaluated the accuracy of the object distance
  calculations to see if the focal length obtained from camera calibration was accurate. In preliminary testing, we found that the distances have an excellent accuracy
  with an error of ± 1 cm.

### Issues Encountered

- **Vehicle Class Misdetections:** During the object detection model testing, we found that the trained model was identifying far background objects as a "Car", and that
  specifically, objects that were black and rectangular in shape were being falsely classified. We then looked back at the Vehicle class training data and identified a potential
  cause for these misdetections. When we annotated this data, we created one large bounding box around the lower back of the Picar, which was done to include both wheels
  in the box. However, since this included lots of noise and/or pixels that were random and not particularly a wheel, this was contributing to the various misdetections
  we were observing.
- **Potential Solutions:** To solve the Vehicle Class misdetections, Nolan and I have proposed reannotating the images with separate bounding boxes around each wheel,
  since this would ensure that the model is trained only on wheel pixels and minimize noise.

### Next Steps

- [ ] Reannotate the Vehicle object class and retrain the model.
- [ ] Implement and test the retrained model on the track.
- [ ] Brainstorm with Nolan how to handle different cases for lane detection and CTE calculation (straight, right, left, etc.)

### Reflection

This work session highlighted the immense value of seeking feedback and perspectives from professionals, such as Professor Paulo Araujo. By engaging in these discussions, 
not only was the Perception team able to validate that their current lane detection implementation is industry standard and that they were on the right track, but they were 
also able to gain profound insights and answers to the remaining questions they had. The conversation we had with Professor Paulo helped clarify points of confusion and ultimately
helped guide the team in the right direction with regard to its next steps. Hence, it is important to ask questions and seek the opinions of knowledgeable professionals. Additionally,
this session showcased the benefit of having team syncs after breaks like reading week. As a result of the team sync, everyone was able to share the work they completed over the break
and this ensured that everyone was on the same page and understood the project trajectory. Lastly, the issues the Perception team encountered with Vehicle class misdetections
illustrate how certain design decisions that may seem trivial when made (like using one bounding box for two wheels instead of two smaller boxes), can have a large impact on
the results obtained; that is, in this case, the efficiency of object detection models.

---

## Entry – [Team Member Name 2]

**Time:** HH:MM–HH:MM  
**Activity Type:** [Implementation / Testing / Design / Documentation / Project Management / Hardware]  
**Status:** [Completed / In progress / Blocked / On hold]  
**Estimated Effort:** X.X h  

### Work Performed

- 
- 

### Decisions

*Optional section - include if applicable*

- 

### Issues Encountered

*Optional section - include if applicable*

- 

### Next Steps

*Optional section - include if applicable*

- [ ] 

### References

- 

### Reflection



---

## Entry – [Team Member Name 3]

**Time:** HH:MM–HH:MM  
**Activity Type:** [Implementation / Testing / Design / Documentation / Project Management / Hardware]  
**Status:** [Completed / In progress / Blocked / On hold]  
**Estimated Effort:** X.X h  

### Work Performed

- 
- 

### Decisions

*Optional section - include if applicable*

- 

### Issues Encountered

*Optional section - include if applicable*

- 

### Next Steps

*Optional section - include if applicable*

- [ ] 

### References

- 

### Reflection



---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Ishaan Grewal | 2.0 h | ✅/⚠️ | Team Sync & Professor Feedback (✅), Object Detection Model Implementation & Testing (⚠️), Object Detection Distance Testing(⚠️)  |
| Name 2 | X.X h | ✅/⚠️/❌ | Brief description |
| Name 3 | X.X h | ✅/⚠️/❌ | Brief description |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: YYYY-MM-DD HH:MM
