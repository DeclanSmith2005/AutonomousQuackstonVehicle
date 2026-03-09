---
title: "Team Contributions - Team Work Session"
date: 2026-03-03
week: 8
hours: 8.0
tags: [Control, Refactoring, Testing, Logging, Perception, Team Sync]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

This team work session centered on stabilizing and cleaning the control stack before deeper CTE integration. Rafael refactored deadband handling into shared configuration, cleaned the structure in control modules, expanded log-analysis capability, and collected a large set of run logs for tuning. On the Perception side, Ishaan and Nolan tested a retrained object detection model where the Vehicle class was restricted to side-view wheel images, which reduced previous false positives from track features. They also collected and annotated additional images for the Duck class to improve training data and continued development of the CTE pipeline for turn handling, including lane filtering and generation of reference points to pass to the control system. The team also held a cross-team discussion to clarify what CTE outputs the control loop requires for navigating turns, helping align perception outputs with control integration plans moving forward.

---

## Entry - Rafael Costa

**Time:** 14:30-16:30, Mar 4 follow-up commits  
**Activity Type:** Implementation, Refactoring, Testing, Documentation  
**Status:** Completed  
**Estimated Effort:** 2.0 h  

### Work Performed

- Refactored deadband usage in the control loop so tuning is driven by `config.DEADBAND` instead of hardcoded values.
- Continued codebase cleanup for readability/maintainability in core control files.
- Updated PID analysis workflow by refactoring `control/analyze_logs.py` and tuning-related values in `control/config.py`.
- Collected and committed many additional `run_log_*.csv` datasets to support data-driven tuning.
- Updated prior week team-contribution logbook files for consistency and detail quality.

### Decisions

- Keep deadband and tuning values centralized in configuration to reduce drift between files.
- Use logged run data as the main input for next PID adjustments instead of ad-hoc on-track tweaks.

### Issues Encountered

- Large parameter surfaces (deadband, thresholds, gains) made one-pass tuning unreliable; this was addressed by organizing more run logs and improving analysis script outputs.

### Next Steps

- [ ] Compare log statistics before/after deadband refactor to validate stability gains.
- [ ] Continue tuning `control/config.py` values using analyzed anomalies.
- [ ] Prepare control-side interfaces for Perception CTE updates.

### References (commits from Mar 3 + Mar 4)

- `0b84708` - Refactor deadband handling to use `config.DEADBAND`
- `ac21aa4` - Refactor code structure for readability/maintainability
- `ea2ce45` - Refactor log analysis and update PID-related config
- `4a28565` - Update previous team-contribution log entries

### Reflection

This session improved the maintainability of the control pipeline and set up cleaner tuning iteration loops. Moving key behavior to shared config and strengthening log-analysis workflows reduced trial-and-error and should make upcoming CTE-control integration safer.

---

## Entry - Ishaan Grewal

**Time:** 14:30-16:30  
**Activity Type:** Implementation, Testing, Coding   
**Status:** In Progress, Completed  
**Estimated Effort:** 2.0 h  

### Work Performed

- **Object Detection Model - Implementation & Testing:** Tested the retrained object detection model with Nolan. The major revision in this model's dataset was reducing the Vehicle class to only images of the wheels from the side view (rather than having the front view as well). We found that with this improvement, the model was no longer misclassifying black rectangular shapes or sections of the mat as vehicles. On the contrary, the model still fails to detect ducks.
- **CTE Implementation - Testing & Discussion:** Tested the CTE implementation for straight lines via live camera feed. Discussed with Control (Rafael) what elements of the implemented straight line CTE he wanted to use. Additionally, Nolan, Rafael, and I revisited how the CTE can be helpful for making turns, specifically discussing what exact outputs Rafael is looking for. Decisions made are discussed below.
- **CTE For Turns - Coding/Development:** Modified `lane_detection_and_cte.py` to implement CTE calculations for making right and left turns. Primarily focused on helping Nolan with filtering out unwanted lane pixels based on the different vehicle state scenarios.

### Decisions

- **CTE Implementation On Straight Roads:** After showcasing the CTE implementation to Rafael via live camera feed, we decided that, although this is a helpful feature, given the effectiveness of the current PID loop that has been implemented with the grayscale sensor, the implementation of CTE on straight paths of travel will be set aside for now. The primary reasons behind this decision are (1) the current PID loop handles straights and curves successfully, (2) with the competition 2 weeks away, if we wanted to implement the CTE into the current PID loop to make it more accurate, this would require significant parameter tuning and testing, which is not feasible with only 2 days a week of testing available on the mats, and (3) similar to the previous point, given the testing time constraints, it is project critical to prioritize CTE implementation for turns instead.
- **CTE Implementation for Turns:** The Perception team's discussion with Rafael has clarified that for turns, the Control loop will stop the car briefly at the intersection and send an updated vehicle state command to the server. When the Perception pipeline acknowledges this update, it will compute a curve approximation for the turn, calculate 10 different CTE values along this curve at equally spaced distances, and then output the CTE at each y_ref point and the distance of each y_ref point to the server for the Control loop to read. Using these outputs, the PID loop will be guided through the turns.

### Issues Encountered

- **Object Detection Model:** As mentioned above, the major issue with the current object detection model is that it is unable to detect the Duck class at all. Given this, Nolan and I decided to take more pictures of the ducks on the track in varying lighting conditions and to retrain the model on these images for Thursday's test session.

### Next Steps

- [ ] Test the retrained Object Detection Model to see if it can classify the Duck Class.
- [ ] Worth with Nolan on finishing CTE implementation for turns.

### Reflection

This work session highlighted the importance of aligning perception development with both dataset quality and system-level requirements. Testing the retrained object detection model showed how refining the dataset, specifically limiting the Vehicle class to side-view wheel images, can significantly reduce false positives, reinforcing that dataset design is critical to model performance. On the other hand, the model's inability to detect the Duck class revealed a gap in training data diversity, particularly across lighting conditions, indicating the need for more diverse data collection. Work and discussion on the CTE implementation also illustrated how perception outputs must directly support the control system, and how intertwined these two systems are. Due to limited testing time before competition, the team prioritized implementing CTE for turns rather than integrating it into straight-line control, highlighting how time and validation constraints influence engineering decisions. 

---

## Entry - Nolan Su-Hackett

**Time:** 14:30-16:30 (team session) 
**Activity Type:** Data Collection, Testing  
**Status:** Completed  
**Estimated Effort:** 2.0 h  

### Work Performed

- Tested Object detection model iteration where the car class only included images of cars from a side view
- Took more images of the duck class (60) with a different background and some images when the duck is on the track to help guide the model.
- Annotated new duck images
- Brainstorm with Control (Rafael) on what he would like from CTE 
- Split work with Ishaan regarding CTE, since Ishaan completed some turn filtering work, I will work on cleaning it up a bit more, and getting y_reference points so they can be passed to control.

### Issues Encountered

- Model still struggles to detect the duck class

### Next Steps

- [ ] Test the new model to see if the duck class improves
- [ ] Finish Development of CTE
- [ ] Discuss with a Professor on issues with duck detection

### Reflection

As the demo day approaches there are still quite a few unfinished tasks/problems that are critical to the success of the project, things like duck detection, CTE, VPFS, and integration. Despite this the team has set clear timelines for when we are expected to have these tasks completed, I think that our continued consistency regarding meeting twice a week is helping the team keep on track and manage our time well. If the duck detection and CTE are completed by next tuesday then I think that perception will be in a great spot to start integrating and helping out other parts of the team. 

---

## Entry – Declan Smith

**Time:** 14:30-16:30  
**Activity Type:** Software Dev
**Status:** In progress  
**Estimated Effort:** 2.0 h  

### Work Performed
- Improved and revised the function that converts graph nodes to left / right / straight directions. Now properly accounts for T intersections and generally is more dynamic ( before it broke each direction into a section of angles to be catagorized, whereas now it looks at the releative direction of each possible path to each other.)
- Above changes were made after interaction with team leads on line following to make the the function more compatible with their existing architecture.
- Consulted with TA's on car placement at the beginning of each round of the competition. Once the path following is in progress, its easy to know exactly where the car is/is moving, but before it first moves, it can be ambiguous which way it is pointing, so we need to choose some rule to hard-code so that we know which way it is pointing at the start. Fortunately, we were told that the placement around the start area was up to us, which gives me the flexibility I need to approach the problem.
- Consulted with TA's on the VFPS documentation, which has so far been lacking in depth. They told us that there is a major update coming later in the week, which I look forward to looking over soon. 


### Next Steps
- Complete fare selection
- wait for teaching team to provide necessary resources to include VFPS
- write test cases to ensure exsiting way finding funcitons are working as intended. 


### Reflection
I have almost completely completed work on the wayfinding and fare selection subsystem. I still need to write the algorithm for accepting fares and interact with VFPS to regularly gather my position data, but both tasks are somewhat reliant on updates from the teaching team, so for now there isn't much work to be done. We seem to be on pace for a successful competition in week 11. 

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 2.0 h | ✅ | Control deadband/config refactor, log analysis improvements, run-log collection |
| Ishaan Grewal | 2.0 h | ✅/⚠️ | Testing (✅), CTE Implementation Planning (✅), CTE Turn Implementation(⚠️) |
| Nolan Su-Hackett | 2.0 h | ✅ | Data Collection, Annotation |
| Declan Smith | 2.0 h | ✅ | Conferring with teaching team ✅, update routing algorithm ✅|

---

**Entry completed**: 2026-03-07
