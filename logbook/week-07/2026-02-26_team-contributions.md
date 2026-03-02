---
title: "Team Contributions - Weekly Work Session #2"
date: 2026-02-26
week: 7
hours: 3.0
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

This session highlights the importance of practical testing, as it was through testing on the actual track that the team identified the weakness in a straight-on camera angle. A straight-on camera angle would introduce many problems in our application as the car would not see oncoming traffic, aswell as the lanes this would disallow the car from properly navigating turns

### Reflection

This session highlights the importance of practical testing, as it was through testing on the actual track that the team identified the weakness in a straight-on camera angle. A straight-on camera angle would introduce many problems in our application as the car would not see oncoming traffic, aswell as the lanes this would disallow the car from properly navigating turns

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 3.0 h | ✅ | Architecture Refactoring (✅), Log Analysis Tool (✅), Extensive On-Track Testing (✅) |
| Nolan Su-Hackett | 3.0 h | ⚠️ | Cross-Track Error (⚠️), Object Detection Model (⚠️) |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: 2026-03-XX XX:XX
