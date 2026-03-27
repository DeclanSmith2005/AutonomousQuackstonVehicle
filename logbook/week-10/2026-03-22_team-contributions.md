---
title: "Team Contributions - Team Work Session"
date: 2026-03-22
week: 10
hours: X.X
tags: [Control, Mission, ZMQ, Recovery, Testing]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

Mar 22 focused heavily on implementing the main robot control loop, mission management, and robust recovery/turn strategies. Work included adding an interactive keyboard listener, emergency stop handling, ZeroMQ server support, and telemetry logging to CSV for later analysis. Multiple configuration tweaks and new calibration values were added to support on-track testing.

---

## Entry - Rafael Costa

**Time:** 09:00-23:30 (individual work / many commits)  
**Activity Type:** Implementation, Integration, Testing  
**Status:** Completed (major initial implementation)  
**Estimated Effort:** 8.0 h

### Work Performed

- Implemented main control logic for the Picarx robot including mission management, PID line following, multiple turn strategies, and emergency stop behavior.  
- Added ZeroMQ server for inter-process communication to share mission state, perception data, and telemetry.  
- Introduced on-robot logging of telemetry to CSV and added calibration values for sensors.  
- Implemented line-loss recovery strategies with motion history tracking and intersection handling for straight/left/right/roundabout states.  
- Added debugging conveniences: keyboard listener, interactive testing tools (e.g., `test_audio.py`), and additional configuration tuning entries.

### Decisions

- Use ZeroMQ server for robust inter-module comms and telemetry streaming.  
- Keep recovery fallback behaviors (re-acquire line via grayscale or retrace path) to improve robustness on track.  
- Log telemetry to CSV for offline tuning and PID calibration.

### Issues Encountered

- Large integration required several simultaneous changes to mission, control, and server code which increased merge complexity.  
- Fine-tuning required for turn strategies (trajectory vs pivot) and timing for re-acquisition after line loss.

### Next Steps

- Run a sequence of on-track tests to validate recovery and intersection handling under mission sequencing.  
- Use CSV logs collected to tune PID and motion-history parameters.  
- Continue iterating on configuration numbers and camera-guided turn parameters.

### References (Mar 22 commits + nearby)

- `376646c` - Implement mission management and the main robot control loop with e-stop functionality and an interactive key listener.  
- `d4abbe1` - Establish foundational robot control system with mission management, PID, turning, and server components.  
- `1256dc8` - Implement initial robot main control logic with mission management, PID, line following, turning, and emergency stop.  
- `de881fd` - Create main Picarx control script integrating mission management, PID, line sensor, and various turning strategies with interactive keyboard control.  
- `06c3a8d` - Add main robot control logic, integrating mission management, various turn modes, and line loss recovery.  
- `add7dbe` - Implement ZMQ server for managing robot state, perception, and pathing communication.  
- `f212a34` / `11f3895` / `c931d5a` - Various main control / config commits implementing integration and configuration.  
- `9181756` - feat: Implement camera-guided turning with trajectory following and grayscale line re-acquisition.

### Reflection

Mar 22 was a heavy integration day — a lot of core control and comms infrastructure landed. The robot is now better instrumented for real tests, but tuning and successive on-track validation are required to reach stable behavior.

---

## Entry - Ishaan Grewal

**Time:** TBD  
**Activity Type:** TBD  
**Status:** TBD  
**Estimated Effort:** TBD

### Work Performed

- To be completed.

---

## Entry - Nolan Su-Hackett

**Time:** TBD  
**Activity Type:** TBD  
**Status:** TBD  
**Estimated Effort:** TBD

### Work Performed

- To be completed.

---

## Entry - Declan Smith

**Time:** TBD  
**Activity Type:** TBD  
**Status:** TBD  
**Estimated Effort:** TBD

### Work Performed

- To be completed.

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
| -------- | ------- | -------- | ------------------ |
| Rafael Costa | 8.0 h | ✅ | Main control loop, ZMQ integration, telemetry logging, recovery strategies |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | TBD | TBD | To be completed |
| Declan Smith | TBD | TBD | To be completed |

---

**Entry completed**: 2026-03-27
