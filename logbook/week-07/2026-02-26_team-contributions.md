---
title: "Team Contributions - Weekly Work Session #2"
date: 2026-02-26
week: 7
hours: 3.0
tags: [Control, Refactoring, Testing, PID]
contributors: [Rafael Costa]
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

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 3.0 h | ✅ | Architecture Refactoring (✅), Log Analysis Tool (✅), Extensive On-Track Testing (✅) |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: 2026-03-XX XX:XX
