---
title: "Team Contributions - Team Work Session"
date: 2026-02-10
week: 6
hours: 14.0
tags: Perception, Planning, Data Collection
contributors: Ishaan Grewal, Nolan Su-Hackett, Rafael Costa, Declan Smith
---

## Daily Summary

Provide a brief overview of what the team collectively worked on today. Include the main focus areas, key achievements, and any cross-cutting issues or decisions.

---

## Entry – Ishaan Grewal

**Time:** 14:30-17:30  
**Activity Type:** Research/Planning, Data Collection 
**Status:** Completed/In Progress
**Estimated Effort:** 3.0 h  

### Work Performed & Decisions Made

- **Lane Detection Research & Discussion - Overview:** Researched, discussed, and mapped out (with Nolan) how the Perception team would detect lanes. Key questions that were
  considered in this discussion were: What is being detected (center line, or green tape)? Would we use an object detection model with bounding boxes, or would we
  use frame-by-frame colour segmentation? What is required to implement this functionality? If we were to use an object detection model, what are we training the
  model on?
- **Lane Detection Research & Discussion - Decision:** Upon research and discussion, the Perception team decided that lane detection would be focused on the green tape in the
  center of the lane, since knowing the distance (or offset) from this line would be the most effective and straightforward, in contrast to the lane boundaries, when
  sending inputs to the Control PID loop. We decided that we would not train the object detection model with bounding boxes for this line detection since the boxes
  would be long, and determining distance from the lines would be inaccurate. This is because from the camera's perspective, the line will appear distorted and curved,
  and the scale will vary with distance. Instead, the Perception team defined the following pipeline, which will be implemented on a frame-by-frame basis: For each frame,
  the image will first be undistorted using the camera's intrinsics, then the lane pixels will be masked and filtered out, then a Birds Eye View (BEV) transform will be applied
  using homography, and finally, a polynomial will be fit to the lane curve. Using this fitted polynomial and an experimentally determined look-ahead distance, the pipeline
  will calculate the Cross Track Error (CTE) and send this as a PID input to the Control loop. Using this method, the Coral TPU will be reserved for object detection.
- **Data Collection - Decision:** The Perception team outlined the following object classes: Stop Sign, Yield Sign, One-Way Sign, Do Not Enter Sign, Duck, and Vehicle. For
  each object class, pictures were to be taken at varying distances with the objects at different angles. For the Stop Sign, Yield Sign, Do Not Enter Sign, and Vehicle classes,
  50 images are to be taken (which is consistent with the quantities used in the European Road Sign tutorial). For the One-Way Sign class, since the signs can be pointing in
  two directions, 100 images are to be taken. Lastly, for the Duck class, since the ducks may be facing head-on, backwards, or sideways, and since this is a critical object to detect,
  100 images are to be taken.
- **Data Collection - Work Complete:** In this work session, the Perception team took all the images for the following classes: Stop Sign (50), Yield Sign (50), Do
  Not Enter Sign (50), Duck (100), and One-Way Sign (100). Images were taken at varying fixed distances and angles, which were consistent across all object classes.

### Next Steps

- [ ] Need to finish data collection for the Vehicle class, which requires taking 50 pictures.
- [ ] Once data collection is complete, the Perception team is to move on to annotating in VOC XML format.

### Reflection

This work session, specifically the discussions about how lane detection was to be implemented, highlighted the importance of planning and critical thinking in 
engineering design projects. Initially, the Perception team thought they were going to use the object detection model for the lanes, and never delved (in detail) 
into how this would be used and how it would interface with a Control PID loop. This was always a grey area. Upon conducting this detailed research and critically 
planning out the pipeline, the team was able to develop a clear roadmap and game plan for implementing this feature. Furthermore, discussing with Rafael (the Control Lead)
of the requirements for his PID loop inputs and what he prefers helped ensure that both teams understood how they interfaced with one another. Hence, it is vital
to not only plan out feature implementations in detail, but also to ensure cross-sub-team collaboration to ensure different teams interface smoothly with one another.
Overall, this was a very productive and valuable work session for the Perception team since we were able to create a clear outline for how lane detection was to be
implemented, and completed 87.5% of the data collection.

---

## Entry – Rafael Costa

**Time:** 14:30-17:30 (Feb 10), 16:30-17:30 (Feb 11 follow-up)  
**Activity Type:** Implementation, Testing, Documentation  
**Status:** In progress  
**Estimated Effort:** 4.0 h  

### Work Performed

- Added CSV telemetry logging to the PID controller in `control/pid/pid.py`, recording `time_s`, `error`, `steering_angle`, and `speed`, and generated run logs for post-test analysis.
- Refactored line-sensor interpretation and control flow for readability and maintainability, including clearer signal gating (white border rejection, floor rejection), stop-line handling, and branch-bias behavior.
- Reorganized PID artifacts into structured folders (`control/pid/logs/` and `control/pid/figures/`) and updated log-write paths accordingly.
- Implemented line-loss recovery logic to steer toward the last known line direction, then tuned steering/speed behavior (`MAX_STEER`, smoothing window, turn speed drop, branch speed reduction) based on observed track behavior.
- Performed cleanup to reduce noisy console output by removing redundant debug key-print branches.

### Decisions

- Chose to log controller outputs to CSV each run so PID tuning can be data-driven rather than based only on subjective driving observations.
- Prioritized deterministic handling order in control logic: stop-line detection first, then normal tracking, then line-loss recovery.
- Selected a stronger recovery steer and dynamic speed adjustments on sharp turns/branch bias events to improve reacquisition stability.

### Issues Encountered

- Occasional line loss produced unstable behavior (drift/hesitation) when no explicit recovery direction was available.
- Speed and steering trade-offs required iterative tuning; aggressive steering could destabilize tracking unless speed was reduced on turns.

### Next Steps

- [ ] Continue tuning `KP`, `KD`, `RECOVERY_STEER`, and branch bias under repeatable test conditions.
- [ ] Use generated CSV logs to compare lap segments and quantify tracking error variance before/after each tuning change.
- [ ] Integrate upcoming perception-derived CTE input once available and re-validate controller behavior end-to-end.

### References

- `control/pid/pid.py`
- `control/pid/logs/pid_log_20260210_154830.csv`
- `control/pid/logs/pid_log_20260210_160629.csv`
- `control/pid/logs/pid_log_20260210_160832.csv`
- `control/pid/logs/pid_log_20260210_160922.csv`
- `control/pid/logs/pid_log_20260210_161051.csv`

### Reflection

This session reinforced the value of pairing control-code changes with telemetry and structured artifacts. Adding CSV logging and organizing logs/figures made each test run easier to interpret, and it became much clearer which adjustments improved behavior versus which only felt better subjectively. The follow-up line-recovery and speed/steering tuning on Feb 11 also showed that robustness depends on handling edge cases (especially temporary line loss), not only nominal PID behavior. Overall, this was productive progress toward a more testable and maintainable line-following controller, with remaining work focused on systematic parameter tuning and integration with Perception CTE inputs.



---

## Entry – [Nolan Su-Hackett]

**Time:** 14:30-17:30  
**Activity Type:** Research/Planning, Data Collection 
**Status:** Completed/In Progress
**Estimated Effort:** 3.0 h  

### Work Performed
- Key goals of the meeting for the Perception team are as follows: Determine how lane detection is going to be performed and how this information will interface with the Control loop. Begin taking images of objects for training of the model.
- The Perception team began researching effective ways to interface with a PID loop so that control has an easy time processing the information that perception sends. It was in this search that Cross Track Error (CTE) was discovered. In a bird's eye view x-y plane centered about the vehicle, cross track error is the x delta between the car and the center of the lane at a target y coordinate. CTE will be continuously fed to control and it can be used to create a PID loop to determine how much each factor (Proportional, integral, derivative) should change with respect to CTE.
- After it was decided that CTE would be used, the Perception team began looking into how CTE would be calculated. Tentatively a colour map will be used to filter for the colour of the lanes, this map will be transformed into a birds-eye view perspective. This will generate guidelines on which a function can be fit to the center of the lane at each point, using the function, CTE can be generated for any target y coordinate.
- Took images for stop signs (50), yield signs(50), oneways(100), ducks (100), and do not enter signs (50). The images conform to the standard mention in the Gitbook, having good lighting with a simple background.

### Decisions

- Cross Track Error will be used to interface with control
- Using Colour map and function fit to center of lanes
- using makesense for PASCAL VOC Annotations

### Next Steps
- Finish Image collection (Cars)
- Annotate in Pascal VOC Format

### Reflection
This meeting highlighted the importance of considering interfacing between teams. Instead of having an approach that looks at the easiest way to detect lanes, the perception team first spoke to Rafael (Control) on what he felt might be useful. He had mentioned distances or error of some sort as this can be integrated into PID easily, his insight allowed perception to narrow the scope on our research and will potentially make for an easier integration later down the line. Had Perception not done this, there may have had to have been heavy processing/transformation of the lane detection information to pass to control which could lead to complications.


## Entry – Declan

**Time:** 14:30-17:30
**Activity Type:** [Develeopment]  
**Status:** [In progress]  
**Estimated Effort:** 4 h  

### Work Performed
- Updated the map of Quackston, increasing resolution and fixing small mistakes with node connections accidentally not going both ways. 
- First draft of a Dijkstra-style algorithm to navigate the map.
- Developed a function to identify the road that a new node lies on. 

This is the current state of the map:
<img width="1146" height="874" alt="image" src="https://github.com/user-attachments/assets/6ad21851-e1b8-40f2-90bf-35c4acf7e151" />


### Next Steps
- CONFIRM W/ STAFF ABT ORIENTATION OF CAR WHEN WE START, AND HOW TO GET CURRent POSITION, AND HOW TO GET LIST OF FARES
- INTEGRATE WITH RAPHAEL'S SERVER
- WRITE CODE TO CHOOSE NEXT PASSANGER
- INTERACT WITH VFPS POSITIONING API
- WRITE A FUNCTION THAT CONVERTS THE PATH LIST FROM DIJKSTRA'S TO A LIST OF TURNS / DIRECTIONS

### References

- 

### Reflection


---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Ishaan Grewal | 3.0 h | ✅/⚠️ | Researched and planned lane detection implementation (✅), Outlined data collection process (✅), Collected 87.5% of data (⚠️) |
| Rafael Costa | 4.0 h | ⚠️ | Implemented PID CSV logging (✅), Refactored control logic and artifact structure (✅), Added line-loss recovery and tuning updates (⚠️ ongoing tuning) |
| Nolan Su-Hackett | 3.0 h | ✅/⚠️ | Researched and planned lane detection implementation (✅), Outlined data collection process (✅), Collected Images for training (⚠️) |
| Declan Smith | 4.0 h | ✅/⚠️ | Imporoved map of Quackston to be more accurate (✅), Draft of Dijstra's (⚠️) |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

**Entry completed**: 2026-03-02 20:31
