---
title: "Team Contributions - Team Work Session"
date: 2026-03-05
week: 8
hours: X.X
tags: [Control, Perception, Integration, ZMQ, Testing]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

This session focused on subsystem integration between Control and Perception using ZeroMQ and camera-guided turn logic. Rafael implemented mission-state publishing and CTE reception, iterated through a temporary ZMQ disable/enable cycle for testing, introduced camera-guided turn handling, and then refactored the approach to a Pure Pursuit style controller with adaptive lookahead. Follow-up commits on Mar 6 simplified trajectory handling in perception modules and added more run logs from testing. Teammate sections are intentionally left open for individual additions.

---

## Entry - Rafael Costa

**Time:** 15:00-18:00 (team session), Mar 6 follow-up commits  
**Activity Type:** Implementation, Integration, Refactoring, Testing  
**Status:** Completed  
**Estimated Effort:** 3.0 h  

### Work Performed

- Implemented ZMQ mission-state publishing and telemetry support in control flow, including camera CTE reception/handling.
- Temporarily commented out ZMQ server calls in `control/main.py` for controlled testing, then restored and advanced the integration path.
- Added camera-guided turn behavior with trajectory handling.
- Refactored turn implementation to use Pure Pursuit concepts with adaptive lookahead; added `control/server.py` and calibration support (`control/calibration.py`).
- Simplified perception-side trajectory communication by removing unnecessary trajectory handling and keeping CTE communication cleaner.
- Added additional run logs after integration tests.

### Decisions

- Use a server-based integration path (ZMQ) with explicit mission-state publishing to decouple subsystem timing.
- Favor a Pure Pursuit-style turn strategy with adaptive lookahead over previous turn handling for smoother camera-guided maneuvers.
- Reduce perception-side message complexity by simplifying trajectory payload handling when not required.

### Issues Encountered

- Integration complexity required temporary rollback/commenting of server calls during test passes.
- Early trajectory messaging added overhead and ambiguity between control/perception ownership, requiring simplification.

### Next Steps

- [ ] Validate camera-guided turns across more intersection cases.
- [ ] Tune adaptive lookahead and calibration values with on-track data.
- [ ] Lock the final ZMQ contract before full team integration testing.

### References (commits from Mar 5 + Mar 6)

- `702c6ce` - Implement ZMQ server functionality and camera CTE handling
- `c3dde23` - Temporarily disable ZMQ calls in `main.py` for testing
- `38605eb` - Add camera-guided turn with trajectory + ZMQ integration
- `2d4294c` - Refactor to Pure Pursuit + adaptive lookahead, add server/calibration
- `22505d7` - Simplify trajectory handling in perception modules
- `458bc3c` - Add run logs from testing
- `502d6ab` - Additional refactor/log updates

### Reflection

This was a high-impact integration session. Rapid iteration between implementation and controlled rollback allowed risky communication changes to be validated in smaller steps. By the end of the window, the architecture moved toward a cleaner contract boundary and a more robust turn-generation method.

---

## Entry - Ishaan Grewal

**Time:** [Add time]  
**Activity Type:** [Add activity type]  
**Status:** [Add status]  
**Estimated Effort:** [Add hours]  

### Work Performed

- [To be added by Ishaan]

### Decisions

- [To be added by Ishaan]

### Issues Encountered

- [To be added by Ishaan]

### Next Steps

- [ ] [To be added by Ishaan]

### Reflection

[To be added by Ishaan]

---

## Entry - Nolan Su-Hackett

**Time:** [Add time]  
**Activity Type:** [Add activity type]  
**Status:** [Add status]  
**Estimated Effort:** [Add hours]  

### Work Performed

- [To be added by Nolan]

### Decisions

- [To be added by Nolan]

### Issues Encountered

- [To be added by Nolan]

### Next Steps

- [ ] [To be added by Nolan]

### Reflection

[To be added by Nolan]

---

## Entry - Declan Smith

**Time:** [Add time]  
**Activity Type:** [Add activity type]  
**Status:** [Add status]  
**Estimated Effort:** [Add hours]  

### Work Performed

- [To be added by Declan]

### Decisions

- [To be added by Declan]

### Issues Encountered

- [To be added by Declan]

### Next Steps

- [ ] [To be added by Declan]

### Reflection

[To be added by Declan]

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 3.0 h | ✅ | ZMQ integration, camera-guided turns, Pure Pursuit refactor, telemetry logs |
| Ishaan Grewal | [Add] | [Add] | [To be added] |
| Nolan Su-Hackett | [Add] | [Add] | [To be added] |
| Declan Smith | [Add] | [Add] | [To be added] |

---

**Entry completed**: 2026-03-07
