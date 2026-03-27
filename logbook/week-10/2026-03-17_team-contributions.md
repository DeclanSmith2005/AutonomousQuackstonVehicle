---
title: "Team Contributions - Team Work Session"
date: 2026-03-17
week: 10
hours: X.X
tags: [Perception, Control, Logs, Refactoring, Integration]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

This entry covers work performed around Mar 17 (and follow-up on Mar 18) and Mar 19 (with follow-up on Mar 20) by Rafael Costa. Major themes across these days include improving perception utilities and image capture, collecting and adding run logs, refining control/configuration parameters for trajectory and turning behavior, and implementing the initial MissionManager and control/perception integration pieces.

---

## Entry - Rafael Costa (Mar 17)

**Time:** 14:00-22:30 (individual work, multiple commits on Mar 17–18)  
**Activity Type:** Perception, Utilities, Logging, Control Tuning, Refactoring  
**Status:** Completed / Iterating  
**Estimated Effort:** 3.5 h

### Work Performed

- Refactored image capture and detection utilities to improve readability and error handling across `capture_images.py`, `detection_receiver.py`, and `detection_sender.py`.  
- Added and committed run logs for Mar 17 (CSV files capturing vehicle state, error, steer, and speed) to support offline analysis.  
- Tuned configuration parameters affecting trajectory turning and added edge-following offsets and PID tracking adjustments for improved turn accuracy.  
- Follow-up refactors and small feature additions on Mar 18: advanced mission-state handling around intersections, startup grace period for turns, and functionality to advance state after intersections while in STRAIGHT mode.

### Decisions

- Keep run logs in the repo for reproducible analysis and tuning.  
- Centralize and tighten turning / PID offsets in `config` to simplify on-track tuning.  
- Make mission-state transitions more conservative immediately after startup to avoid false-turn triggers.

### Issues Encountered

- Initial capture/detection utilities had inconsistent error handling for socket operations and calibration helpers which slowed iteration.  
- Turn execution remained sensitive to vehicle speed and timing, requiring improved parameterization and logs for tuning.

### Next Steps

- Use the new run logs to tune velocity/steering calibration and PID settings.  
- Validate edge-following offsets and snapshot-based turn behavior on additional runs.  
- Collaborate with control integration testing to ensure mission-state changes are safe during real runs.

### References (commits from Mar 17 + Mar 18)

- `f2deb96` - Add edge following offsets and adjust PID tracking for improved turn accuracy  
- `4ab8b7d` - Add run logs for March 17, 2026  
- `612fbfc` - Updated parameters in config file and improved trajectory turning  
- `563fe88` - Refactor image capture and detection utilities  
- `fda36b8` - Added functionality to advance state after intersection while in STRAIGHT mode.  
- `ddad53d` - Refactor mission states and implement startup grace period for turns  
- `c879a9f` - Adjust motion parameters for improved vehicle control and responsiveness  
- `5263214` - Merge branch 'main'

### Reflection

Focused cleanup of perception utilities and proactive logging made it straightforward to begin tuning control parameters. The logs collected on Mar 17 enabled iterative improvements on Mar 18 to mission handling and turn robustness.

