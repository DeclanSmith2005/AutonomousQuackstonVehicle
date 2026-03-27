---
title: "Team Contributions - Team Work Session"
date: 2026-03-20
week: 10
hours: X.X
tags: [Control, Perception, Integration]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

Work on Mar 20 (with follow-up commits on nearby dates) focused on adding the initial control surface, perception integrations, and configuration to centralize tuning. This included mission management scaffolding, camera/lane/object perception hooks, and multiple turning strategies integrated into the main control loop.

---

## Entry - Rafael Costa

**Time:** 10:00-23:50 (individual work / multiple commits)  
**Activity Type:** Implementation, Integration, Configuration  
**Status:** Completed (initial implementation)  
**Estimated Effort:** 6.0 h

### Work Performed

- Implemented initial robot control logic and perception module integration, including object and lane detection and CTE calculation.  
- Added `MissionManager` scaffolding and mission sequencing to allow deterministic handling of straight/turn states.  
- Centralized parameters into `config.py` to simplify cross-module tuning.  
- Added multiple turning strategies (camera-guided, pivot) and integrated them into the main loop.  
- Cleaned up unused localization handling in server code and removed stale logs.

### Decisions

- Centralize runtime tuning in `config.py`.  
- Expose mission sequencing via `MissionManager` to simplify higher-level navigation logic.  
- Prefer explicit perception→control handoff points to reduce ambiguity during turns.

### Issues Encountered

- Several merges were required to align perception and control interfaces, which triggered iterative refactors.  
- Turn execution remains sensitive to timing and requires on-track tuning for velocity/CTE interplay.

### Next Steps

- Run integrated on-track tests to tune turning parameters and CTE handling.  
- Continue cleaning unused server/localization paths and validate `MissionManager` behavior under intersection cases.

### References (Mar 20 commits + nearby)

- `981d3ff` - feat: Implement initial robot control logic, perception modules, and various turning functionalities.  
- `819a93d` - feat: Implement initial robot control system including mission management, turning logic, and configuration.  
- `084d305` - feat: Introduce configuration and logic for various turn types, including camera-guided and pivot maneuvers.  
- `6334362` - feat: Introduce MissionManager for sequential robot mission state management.  
- `affb448` - feat: implement initial robot control system including line following, mission management, turning strategies, and pathfinding components.  
- `0df5ba8` - feat: Add core control logic, comprehensive configuration, and initial pathing data files for the robotic vehicle.  
- `f5026f0` - feat: Implement perception module for object and lane detection, CTE calculation, and server communication.  
- `dcc94d7` - feat: introduce `config.py` to centralize vehicle control and mission parameters.  
- `28c3970` - feat: Implement the main robot control loop, mission management, and comprehensive configuration settings.  
- `8e53052` - Add initial perception and control systems including camera undistortion, object/lane detection, hardware I/O, and inter-module communication.

### Reflection

Mar 20 consolidated many control and perception ideas into an initial, runnable control surface. There is clear progress toward integrated testing, but significant tuning remains before robust on-track performance.

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
| Rafael Costa | 6.0 h | ✅ | Perception & control integration, MissionManager, config |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | TBD | TBD | To be completed |
| Declan Smith | TBD | TBD | To be completed |

---

**Entry completed**: 2026-03-27
