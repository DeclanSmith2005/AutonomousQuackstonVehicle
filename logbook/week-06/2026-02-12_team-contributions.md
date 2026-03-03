---
title: "Team Contributions - Team Work Session"
date: 2026-02-12
week: 6
hours: 9.5
tags: Perception, Planning, Data Collection, Project Management
contributors: Ishaan Grewal, Nolan Su-Hackett, Rafael Costa, Declan Smith
---

## Daily Summary

Provide a brief overview of what the team collectively worked on today. Include the main focus areas, key achievements, and any cross-cutting issues or decisions.

---

## Entry – Ishaan Grewal

**Time:** 14:30-16:30  
**Activity Type:** Planning/Project Management, Data Collection  
**Status:** Complete  
**Estimated Effort:** 2.0 h  

### Work Performed & Decisions Made

- **Data Collection - Work Complete:** In this work session, the Perception team finished the data collection stage, taking 50 pictures for the Vehicle object class.
  Images were taken at varying fixed distances and angles, which were consistent across all object classes.
- **Data Annotation - Decision:** The Perception team experimented with mulitple softwares for labelling and annotating the data, and ended up choosing Makesense AI
  due to its ease of use. Nolan and I then went through a few example annotations to ensure we were both familiar with how we were annotating the objects. For each object
  class, we outlined which section of the object we would cover in the bounding box. Key decisions made here pertained to training the model on only the "board" section
  of the signs rather than the whole sign with the stand and base, since this is common for all signs and would introduce noise/bias from the background around the stand.
  Additionally, we emphasized the importance of outlining the bounding box as close as possible to the object to minimize noise and keep all boxes consistent.
- **Planning/Project Management:** Nolan and I discussed our current progress and divided key tasks each individual will perform over reading week to help ensure that
  the Perception team is on track with its projected timeline.

### Next Steps
Below is a list of the tasks Ishaan has been assigned to complete over reading week:
- [ ] Label and annotate the Stop Sign class (50)
- [ ] Label and annotate the Do Not Enter Sign class (50)
- [ ] Label and annotate the Duck class (100)
- [ ] Develop a Python script to calculate the distance to each detected object per frame
- [ ] Develop a Python script to perform the lane detection pipeline (BEV transform, polynomial fitting, CTE, etc.)
- [ ] Work with Nolan on object detection model validation.

### Reflection

Effective project management within the Perception team is critical to ensuring Nolan and I remain aligned on our objectives over the break. By decomposing high-level goals into granular tasks, we have established a framework that mitigates the risk of task slippage and eliminates redundant effort. In an engineering environment, this level of structured synchronization is essential not just for accountability but as a proactive measure to ensure operational efficiency and the successful delivery of our technical milestones.

---

## Entry – Rafael Costa

**Time:** 14:30-17:00 (Feb 12), 20:30-21:30 (Feb 13 follow-up)  
**Activity Type:** Implementation, Testing, Design  
**Status:** In progress  
**Estimated Effort:** 3.5 h  

### Work Performed

- Implemented a modular control architecture by creating `LineSensor` and `PIDController` classes and integrating them into a new `control/main.py` control loop.
- Added robust line-processing behaviors including stop-line detection, branch biasing, last-seen-direction recovery, moving-average error smoothing, and CSV telemetry logging.
- Implemented a keyboard-driven state machine in `control/main.py` (`STRAIGHT`, `APPROACH_STOP`, `LEFT_1`, `LEFT_2`, `RIGHT`, `CALIBRATE`) with intersection handling helpers for controlled turn execution.
- Refactored line detection logic to use thresholded signal space for pattern detection, added sensor-read exception handling, enabled runtime bias commands, and switched to measured `dt` in PID updates.
- Performed follow-up tuning on Feb 13 (thresholds, base speed, turn steering/PWM behavior, straight-angle compensation) and archived the previous monolithic script as `control/pid/pid.py.bak`.

### Decisions

- Moved from a single-script controller to class-based modules (`line_sensor`, `pid_controller`, `main`) to improve maintainability and testability.
- Adopted an explicit state-machine approach for intersections/stop behavior instead of trying to handle all special cases purely inside continuous PID tracking.
- Reintroduced integral accumulation with anti-windup in `PIDController` and used actual loop `dt` to improve controller stability and derivative behavior.

### Issues Encountered

- Distinguishing intersection crossings versus stop lines required iterative threshold and pattern-logic refinements.
- PID behavior was sensitive to timing assumptions and steering saturation, requiring retuning after state-machine and speed-profile changes.
- Sensor-read reliability required defensive handling to avoid control-loop crashes during transient read failures.

### Next Steps

- [ ] Validate all state transitions on track with repeatable test scripts (especially `LEFT_2` skip-first behavior).
- [ ] Continue tuning `LINE_THRESHOLD`, `WHITE_CUTOFF`, and turn timing (`TURN_TIME`, `PASS_TIME`) using logged runs.
- [ ] Compare class-based controller behavior against archived baseline (`pid.py.bak`) and lock a competition-safe parameter set.

### References

- `control/main.py`
- `control/line_sensor.py`
- `control/pid_controller.py`
- `control/pid/pid.py.bak`

### Reflection

This session was a major structural step forward for the Control pipeline. Breaking the previous monolithic PID script into dedicated sensor, controller, and orchestration modules made the behavior easier to reason about and faster to iterate. The state-machine design was especially useful for handling real track events (stops and intersections) that pure continuous control struggles with. The follow-up tuning work on Feb 13 also reinforced that line-following performance depends heavily on calibration and timing details, so disciplined parameter sweeps and replayable tests will be critical before final integration.



---

## Entry – [Nolan Su-Hackett]

**Time:** 14:30-16:30  
**Activity Type:** Planning/Project Management, Data Collection  
**Status:** Complete  
**Estimated Effort:** 2.0 h  

### Work Performed

- Completed taking pictures for model training, cars (50)
- Discussed where bounding boxes should be drawn, since the pole is common to all signs the perception team thought it best to box the head of the sign instead, as for vehicles the team decided to bound boxes around the wheels as a whole block, as the cars will each look different but it is expected that wheels will look relatively similar.
- Although discussed in last meeting, it was finalized that the perception team will use Makesense to label/annotate images into PASCAL VOC Format.
- divided next steps for the reading week, see next steps for Nolan below.

### Next Steps
-  Annotate the following classes: One way, Yield, Car
-  Train a preliminary model on our annotations (After the team has finished annotations)
-  Collect validation scores (mAP, Loss)
-  Import model to car and test


### Reflection
It is good that the team knows what will be done during the break, and each of the perceptions teams members have a defined scope. Other than this, all went well and as expected. 


---

## Entry – [Declan Smith]

**Time:** 14:30-16:30  
**Activity Type:** [Software Development]  
**Status:** [In progress]  
**Estimated Effort:** 2.0 h  

### Work Performed
- Improved Disktra's Implementation
- Merged local repositiory with team github

### Decisions
- Interacted with line detection team lead and agreed to supply a list of left, right, and straight directions over a series of way points. 

### Next Steps
- WRITE CODE TO CHOOSE NEXT PASSANGER
- INTERACT WITH VFPS API
- INTEGRATE WITH RAPHAEL'S SERVER


### References

- NA

### Reflection
- Pace of project is going well. Everyone is on top of their respective work and we seem well ahead of schedule. 


---
## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Ishaan Grewal | 2.0 h | ✅/⚠️/❌ | Data collection (✅), Discussed work split for reading break (✅)|
| Rafael Costa | 3.5 h | ⚠️ | Implemented modular LineSensor/PIDController/main pipeline (✅), Added state-machine intersection handling and recovery logic (✅), Performed threshold and control tuning follow-up (⚠️ ongoing) |
| Nolan | 2.0 h | ✅/⚠️/❌ | Data collection (✅), Discussed work split for reading break (✅)|
| Declan Smith | 2.0 h | ✅/⚠️ | Improved Disktra's Implementation (✅), Merged local repositiory with team github (✅)|

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

## Team Notes

Any collective observations, cross-functional issues, or team-level decisions that span multiple individual contributions.

---

**Entry completed**: 2026-03-02 20:40
