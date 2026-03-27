---
title: "Team Contributions - Team Work Session"
date: 2026-03-19
week: 10
hours: X.X
tags: [Perception, Control, Logs, Refactoring, Integration]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Entry - Rafael Costa (Mar 19)

**Time:** 13:00-23:50 (work spanning Mar 19–20 commits)  
**Activity Type:** Control Implementation, Mission Management, Perception Integration  
**Status:** Completed (initial implementation)  
**Estimated Effort:** 6.0 h

### Work Performed

- Implemented core control and mission management components, including initial `MissionManager` for sequential mission state handling.  
- Added central `config.py` to house vehicle control and mission parameters and updated other modules to read from it.  
- Implemented perception integration for object and lane detection, added CTE calculation, and hooked up server communication paths for inter-module messaging.  
- Added initial turning strategies (camera-guided, pivot maneuvers) and integrated these into the main control loop.

### Decisions

- Centralize tuning parameters in `config.py` for easier sharing across perception, control and mission logic.  
- Implement mission sequencing (MissionManager) to simplify higher-level navigation and to allow turns and straight-mode behaviors to be reasoned about deterministically.

### Issues Encountered

- Integration required several merges and small refactors to keep perception and control interfaces consistent (multiple merge commits present).  
- Some legacy or unused localization handling was removed from `ServerManager` to avoid confusion and reduce surface area for bugs.

### Next Steps

- Run integrated tests on the vehicle with MissionManager-enabled control loop to evaluate turn strategies.  
- Continue tuning perception→control handoff timing and CTE calculations based on on-track logs.  
- Remove or refactor remaining unused code paths identified during integration.

### References (commits from Mar 19 + Mar 20)

- `8e53052` - Add initial perception and control systems including camera undistortion, object/lane detection, hardware I/O, and inter-module communication.  
- `28c3970` - feat: Implement the main robot control loop, mission management, and comprehensive configuration settings.  
- `6172036` - Logs  
- `dcc94d7` - feat: introduce `config.py` to centralize vehicle control and mission parameters.  
- `f5026f0` - feat: Implement perception module for object and lane detection, CTE calculation, and server communication.  
- `0df5ba8` - feat: Add core control logic, comprehensive configuration, and initial pathing data files for the robotic vehicle.  
- `981d3ff` / `819a93d` / `084d305` / `6334362` / `affb448` - various feature commits implementing control, perception and turning functionality

### Reflection

The Mar 19–20 work established the initial, centralized control surface and mission sequencing necessary for further autonomous runs. There is still tuning and integration work ahead, but the core systems are now in the repo and wired together for iterative testing.

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
| Rafael Costa | 9.5 h | ✅ | Perception utilities, run logs, control/mission manager, initial integration |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | TBD | TBD | To be completed |
| Declan Smith | TBD | TBD | To be completed |

---

**Entry completed**: 2026-03-27