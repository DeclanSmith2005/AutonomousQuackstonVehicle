---
title: "Team Contributions - Weekly Work Session #2"
date: 2026-02-26
week: 7
hours: 9.0
tags: [Perception, Planning, Control, Refactoring, Testing, PID]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

XX

---

## Entry – Rafael Costa

**Time:** 15:00–18:00  
**Activity Type:** Implementation, Testing, Refactoring  
**Status:** Completed  
**Estimated Effort:** 3.0 h  

### Work Performed

- **Architecture Refactoring:** Performed major restructuring of the control system, separating concerns into dedicated modules:
  - Created `control/config.py` to centralize all PID tuning parameters, motion parameters, sensor calibration values, and network configuration. This eliminates magic numbers scattered throughout the codebase and makes tuning easier.
  - Created `control/mission_manager.py` with a `MissionManager` class to handle robot state transitions and mission progression. Encapsulates state machine logic (STRAIGHT, LEFT_1, LEFT_2, RIGHT, APPROACH_STOP, IDLE) with clean interfaces for advancing and resetting missions.
- **Log Analysis Tool:** Created `control/analyze_logs.py` (170 lines), a comprehensive script for analyzing PID log data. Features include:
  - Automated log file discovery and chronological sorting
  - Statistical analysis (mean, median error values)
  - Support for both `pid_log_*.csv` and `run_log_*.csv` formats
- **Hardware Bridge Updates:** Simplified `server/hardware_bridge.py` by removing direct control logic and updating it to listen for mission state updates, improving separation of concerns.
- **Line Sensor Refinements:** Updated `control/line_sensor.py` with improved threshold handling and calibration logic.
- **Extensive On-Track Testing:** Conducted 28 test runs on the track, collecting detailed telemetry data including state, error, steering angle, and speed. Log files capture data at 100Hz for post-session analysis.

### Decisions

- Adopted a centralized configuration approach (`config.py`) to make parameter tuning more systematic and reduce the risk of inconsistent values across modules.
- Moved mission state management into a dedicated class to improve testability and make the control loop logic in `main.py` cleaner and more focused on sensor processing and PID updates.
- Chose to keep both `pid_log_*.csv` (older format) and `run_log_*.csv` (new format with state information) supported in the analysis tool for backward compatibility.

### Issues Encountered

- The refactoring required careful migration of parameters that were previously hardcoded in multiple files. Had to ensure all values were moved to `config.py` without introducing regressions.
- Some test runs showed inconsistent behavior during turns, requiring iterative adjustments to `TURN_ENTRY_TIMEOUT` and `TURN_STOP_HOLD_TIME` values.

### Next Steps

- [ ] Use `analyze_logs.py` to identify optimal PID parameters from collected run data.
- [ ] Add deadband for error smoothing to reduce oscillations near zero error.
- [ ] Continue refining turn timing parameters based on logged telemetry.
- [ ] Prepare for integration with Perception team's CTE output.

### References

- Commit: `b45e432` – Major refactor of PID control and mission management system
- Commit: `a2f0b14` – Add log analysis script
- Commit: `3ada5c2` – Add run logs capturing state, error, steer, and speed data
- Commit: `ab7e046` – Additional run logs with detailed telemetry

### Reflection

This was a substantial refactoring session that significantly improved the codebase organization. Moving from scattered constants to a centralized `config.py` immediately made it easier to experiment with different parameter values during testing. The `MissionManager` class abstraction paid off quickly—adding new mission sequences or debugging state transitions is now much more straightforward. The extensive testing generated valuable data that will drive the next round of PID tuning. The modular architecture also sets a better foundation for integrating the Perception team's CTE input when it becomes available.

---

## Entry – Ishaan Grewal

**Time:** 15:00–18:00  
**Activity Type:** Implementation, Testing, Problem Solving
**Status:** In Progress, Completed  
**Estimated Effort:** 3.0 h 

### Work Performed
- **Object Detection Model - Implementation & Testing:** Once Nolan retrained the model with the Vehicle class annotations having separate bounding boxes around each wheel compared to one large box around both, Nolan and I reimplemented and tested the model's object detection effectiveness. In addition to this, we compared this revised model to one where there was no Vehicle class at all to see the effect of the Vehicle class on classifications. Issues encountered and corresponding decisions made are discussed below.
- **CTE Implementation and Camera Tilting Discussion:** Nolan and I discussed how the image processing and CTE calculation would need to vary based on the vehicle states (STRAIGHT, LEFT, RIGHT) because, for example, if the state is STRAIGHT, and there is a green line intersecting the desired path, this would interfere with the polynomial generation and CTE calculation. Conversely, if the state is RIGHT (which is turn right at an intersection), then we would want to ignore irrelevant lanes and change the look-ahead distance accordingly to generate a turning curve. Additionally, Rafael, Nolan, and I discussed when and how to use the camera tilting functionality. Decisions made are discussed below.
- **CTE Implementation & Server Integration Work Split:** Split up the modifications that are to be made to the `lane_detection_and_cte.py` script for the different vehicle states, as well as the required code for integrating the Perception pipelines with the rest of the car via the server. Nolan will work on CTE for left and right turns, and I will work on the CTE for the straight vehicle state and all server integration scripts.
- **Determining Meters Per Pixel:** Experimentally determined the `meters_per_pixel_straight` parameter, which is required to convert the CTE from pixels to meters when outputting to the PID loop. This was done by dividing the real width of the green tape by the pixel width, obtaining a value of 0.00046296296 meters/pixel.
- **Image Collection:** Nolan and I took more pictures of different turns on the map so that the CTE scripts can be tested over the weekend for the different vehicle states.

### Issues Encountered
- **Object Detection Model:** When comparing the revised model with the model with no Vehicle class, we found that the model with no Vehicle class was failing to detect ducks for some reason. On the other hand, the revised model was still occasionally detecting black surfaces as wheels. However, other than these misdetections, it was detecting all object classes, including the Vehicle class, successfully. Hence, the primary issue was the misdetection of black surfaces as wheels.
- **Camera Tilt & Limited Field of View:** When approaching intersections on the track, we found that when the camera is facing straight forward with zero tilt, there was a limited field of view of the actual lanes near it. This is especially an issue when making turns at intersections since the CTE requires a polynomial, which in turn requires a clear view of the lanes.

### Decisions
- **Object Detection Model:** Nolan and I decided that we would proceed with the revised model since it was able to detect all object classes successfully, with the only issue being the misclassifications of black surfaces as wheels. To solve this misclassification, we have decided to retrain the model and only keep images of the side views of the wheels for the Vehicle class, as we figured that the reason for these misclassifications was that some of the trained images were of the front/back of the wheel, which is essentially a black rectangle. Although this means that the model will not detect cars that are straight on in front of us, we have discussed with Rafael and determined that the use of ultrasonic sensors on the front will cover this case. This retraining is important to prevent classifying any black rectangles as wheels, since this would be a critical failure for our application.
- **Camera Tilt & Limited Field of View:** We have decided that when making a turn at an intersection, the camera will tilt fully down, allowing it to get a better view of the lanes for the curve and CTE generation. We have recognized that this will require tuning parameters and implementing different methods for lane filtering based on vehicle state.

## Results
Images for object detection can be found at
[Images stored here](https://github.com/ELEC-392/elec-392-project-duclair_2/tree/main/images/week-07)
### Next Steps
- [ ] Retest the model once it is retrained with only images of the side view of the wheels.
- [ ] Modify `lane_detection_and_cte.py` to handle different vehicle states and make the script modular (with functions) and easy to integrate with the PID loop. Write the code for the STRAIGHT vehicle state.
- [ ] Create a new `perception_server_comms.py` file to facilitate communication from and between the Perception pipeline and the main server.
- [ ] Modify `detect_objects.py` to include the lane detection and CTE calculations and integrate with the server.
- [ ] Test object distance errors in detail.

### Reflection
This work session illustrated the immense importance of practical on-track testing, because it was through testing on the track that the team noticed the misclassifications of the Vehicle class and the limitations of having a straight-facing camera with zero tilt when making turns. By recognizing these edge cases and weaknesses, the team is now able to address them head-on rather than being blindsided in the future as competition nears. The decision to remove straight-on vehicle detection highlights how, in complex engineering systems and projects, one may have to iterate and forego extra features to focus on core reliability. By removing these images from our training pipeline, the model will be far more reliable and accurate, as it will not misclassify black rectangles as wheels. That being said, discussing these changes with Rafael also showcases that when features are removed, backups, in this case, the ultrasonic sensors, must be considered to ensure safety, which, in this case, pertains to reliable vehicle detection in front of the car. 

---

## Entry – Nolan Su-Hackett

**Time:** 15:00–18:00  
**Activity Type:** Implementation, Testing, Refactoring  
**Status:** Completed  
**Estimated Effort:** 3.0 h  

### Work Performed
- Trained Model without Car Class to see how the model performs, compared the carless model with the wheel classification model.
- Discussed CTE work split with Ishaan, Nolan will do the CTE for left turn, right turn, Ishaan will write the code for going straight and dynamically calculating y_ref.
- Discussed when and how to use camera tilting functionality with Ishaan and Rafael.
- Took more pictures of the roads so that CTE can be tested on a larger set of data, these images were taken with a fully downtilted camera

### Decisions
- On each stop line, car will look left and right before any action to detect other nearby cars.
- On a turn the car will perform a full downtilt, this is to get a better angle of the lane guidelines for the CTE calculation.
- Perception decided that the car wheel model will be used as there were issues with the car less model, and do not currently have a feasible alternative or workaround for car detection.

### Issues Encountered
- Carless model fails to detect ducks
- if the camera is facing straight forward, field of view is limited, this causes the following problems: Cannot detect oncoming traffic from left or right sides, and does not have a large enough frame to see lane guidelines for CTE calculations.
- model with wheel classification still detects black surfaces as wheels

### Next Steps

- [ ] Retrain model only with bounding boxes around the wheels when the car is in a side view. this will cause the model to ignore cars when they are driving into it straight on and the car will have to rely on its ultrasonic in this situation. This retraining is to avoid the model classifying all black objects as wheels, which would cause a critical failure for our application.
- [ ] Write CTE Code
- [ ] Test object distances

### Reflection

This session highlights the importance of practical testing, as it was through testing on the actual track that the team identified the weakness in a straight-on camera angle. A straight-on camera angle would introduce many problems in our application as the car would not see oncoming traffic, aswell as the lanes this would disallow the car from properly navigating turns

---

## Entry – Declan Smith

**Time:** 15:00–18:00   
**Activity Type:** Project Management / Software Dev
**Status:** In progress  
**Estimated Effort:** 3.0h  

### Work Performed
- Worked with all team members to decide how to optimally communicate directions from the pathing software to other subsystems (both in terms of the means of communication and the way they are encoded. The team has currently settled on a list of left, right, and straight instructions for simplicity, but it gets quite complicated around certain edge cases to do with one-way streets, roundabouts, and map nodes that aren't placed at intersections. We are still in the process of resolving exactly how to avoid these issues, but our systems for managing regular intersections seems releavtively robust.


### Next Steps
- Speak with TA's / instruction staff about the rules for initial placement of the car at the start of the competition. Much of the pathing logic is dependent on the orientation of the car, which can easily be determined once it has been moving, but we need a way to know what its orientation is when we first set it down to orient the mapping software properly.


### Reflection
Things seem to be coming together very nicely. If the line following and object detection software is complete soon, its possible that we may be able to begin integration testing as soon as next week. 

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 3.0 h | ✅ | Architecture Refactoring (✅), Log Analysis Tool (✅), Extensive On-Track Testing (✅) |
| Nolan Su-Hackett | 3.0 h | ⚠️ | Cross-Track Error (⚠️), Object Detection Model (⚠️) |
| Ishaan Grewal | 3.0 h | ✅/⚠️ | Cross-Track Error F, Object Detection Model (⚠️), Server Integration (⚠️), Meters Per Pixel (✅), Planning CTE Changes (✅) |
| Declan Smith | 3.0 h | ⚠️ | Subsytem coordination(⚠️)|


**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: 2026-03-XX XX:XX
