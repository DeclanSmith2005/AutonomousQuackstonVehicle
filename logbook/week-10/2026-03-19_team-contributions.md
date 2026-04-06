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

**Time:** 14:30-16:30 (team session)
**Activity Type:** Testing Control, Testing Duck Detection, Testing Integration
**Status:** Completed  
**Estimated Effort:** 2.0 h  

### Work Performed

### Issues Encountered

### Decisions

### Next Steps


### Reflection

---

## Entry - Declan Smith

**Time:** 13:00-23:50 (work spanning Mar 19–20 commits)  
**Activity Type:** Finalizing Turn Classification and Path Finding 
**Status:** Completed (initial implementation)  
**Estimated Effort:** 6.0 h

### Work Performed
- fixed bug where adding a temporary graph node for passenger/car was only removing nodes behind the car at that way point ( so in some cases car would go to the nearest intersection and attempt to make a 180 degree turn.
- The subsystem responsible for actually causing the car made a last-minute change request, where instead of only separating out the directions into left, right, straight, we needed to identify a few different particular types of lefts and rights depending on the intersection, and put out a particular number of straights depending on if we were crossing a stop sign and if the intersection crossed a two way or one way road. This was because we needed to give the car instructions at every intersection of the tape, not just at intersections of roads. To accommodate these changes, the existing system of generalized turn classification was basically tossed out the window in favour of specifically classifying each combination of current node, intersection, and the node following the intersection on the map. It's unfortunate that we had to turn to hard-coding at the last minute, but it is what it is, and it was the only feasible solution we could come up with. Fortunatly the base Dijkstra pathing algorithm for identifying the nodes the car needed to travel was still useful in this case. 
- Appended a simple script to duckAPI to be able to cancel the fare the car is currently on to quickly re-run tests on the track
- Finalized the pathfinding code so that it consistently outputs correct list of directions. 
---

### Decisions
- Major change to the method classifying turns to return the correct instructions to the car (as described in work performed)
- Decided that the main loop for controlling movements of the car would be called by a file not in pathing/wayfinding, but instead, I would send directions to an internal server on the Pi that would be read by another file. 

### Issues Encountere
- Several bugs, including the car/passenger nodes snapping to incorrect edges, the car trying to make 180-degree turns, visualization issues with the graph of the car / its turns, and a bug where old edges between nodes now separated by temporary nodes were continuing to exist, which caused a cascade of other bugs down the line. 
### Next Steps

- Integrate turn outputs with the car by sending them to the server, and test the car to make sure it's working overall.

### References (commits from Mar 19 + Mar 20)
NA

### Reflection
I'm happy to have finally completed a 100% working version of the pathing code that consistently outputs the correct turns for the car to make. Now all that's left from my side is integrating the wayfinding with the other parts of the project and putting the whole thing together for a working duck taxi!

## Team Metrics

| Member | Hours | Status | Key Contribution |
| -------- | ------- | -------- | ------------------ |
| Rafael Costa | 9.5 h | ✅ | Perception utilities, run logs, control/mission manager, initial integration |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | TBD | TBD | To be completed |
| Declan Smith | 6.0 h | ✅ | Finalizing turn classification and wayfinding |

---

**Entry completed**: 2026-03-27
