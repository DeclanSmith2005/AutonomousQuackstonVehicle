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

**Time:** 10:00-23:30
**Activity Type:** Implementation, Integration, Configuration  
**Status:** Completed
**Estimated Effort:** 3.0h

### Work Performed

- Worked on tuning the PID parameters
- spoke with professor Matthew about issues that we were having with turning
- Worked on labels for certain edges of the map, labelling cases like r0, l0, l1 turns. These each are turn types that we have designed for an
- R0: right hand turn where there is no stop sign, must use pivot.
- L0: left hand turn when there is no stop line and there is a one way intersecting the street, meaning that there will be a pivot on the first intersection cross it sees
- L1: No stop line but there are two intersecting lines, which means it will stop at the first line it sees then perform a curved arc onto the second intersecting line
- Verified labelling for stop signs
- Realised that there are some other information we need to encode in the map like cross walks
- took 150 more pictures of ducks on the crosswalks and road
- annotated all the pictures
- retrained the model with additional pictures
- created a colour map filter that will reject a bounding box detection if it doesnt contain atleast 30% yellow
- Helped Ishaan create the bounding box area filter that would stop the model from detecting really large things that aren't ducks, this will help filter things that aren't rejected from the colour Ratio filtering.
- Created the Care box
- Tested integration with newly added map information in our graph

### Issues Encountered
- the map only passed a single straight, when going through a node that it wants to go straight on, this is a problem because the way control is working is that it counts intersecting lines using the grayscale to decide when to do something. The problem with only passing one straight is that at a normal decision point with two intersecting lanes where both lanes are two ways, two intersections need to be counted, this means that two straights must be passed. This is of course only for a normal street, but if a one way is intersecting that node then it is fine to pass just one straight.
- The map did not have information for when ti would have to make certain types of turns, this meant that control had no way of knowing when to perform a pivot turn or a curved turn, etc.
- The Control did not know when to stop, so stop line edges needed to be integrated into the map aswell so that control knew at what line to stop at using the counting algorithm mentioned earlier.
- large bounding boxes were being drawn around random objects, this was solved using the bbounding box area filter
- bounding boxes were being drawn over small areas that contained no ducks, this was resolved using the yellow colour ratio to filter these false positives.
### Decisions
- Not relying on object detection for signs, this was something that came up when realising that control needed to know when it would soon see a stop sign. A solution that was suggested was using the model to detect signs, and this would append a stop instruction to the currentlylist of instructions that the control had. the only problem wiht this is that the stop sign detection was unreliable, and one mistake would irreversibly mess up the array of instructions that control had at that moment. So instead, the team decided to hard code these places in the map.

### Next Steps
- Update the map so straight instructions correctly distinguish between cases that require one intersection count and cases that require two.
- Continue integrating added map details such as crosswalks and stop-related information into control testing.
- Test the new turn labels (r0, l0, l1) further to verify that pivot and curved turn behaviors trigger correctly.
- Keep refining duck detection with the new yellow ratio and bounding box area filters during integration tests.
- Validate the retrained duck model on track conditions to see whether the added images improved real performance.

### Reflection

This session highlighted that there were a lot of things that needed to be taken into consideration earlier that only came to light when we started testing on the real track. Some of these things are unavoidable as it is a natural part of testing, one example of a natural test that we did not know about before hand would be the issue with the cross walks. We realised that the sensors would also see the crosswalks as an intersection because of the way they are taped, so we needed to create extra nodes in the map to have the capability to operate though them. However, there were other problems that we could have easily prepared for and dealt with earlier, and this is the ability for the planning code to have different types of turns. This was something that could have been communicated earlier allowing the team more time to deal with other problems, but having it happen like this created a lot of work near the end of the deadline. In future work, we will make sure that all members of the team have information as soon as its available and have syncs at every meeting ensuring that integration parameters is something that is understood and agreed upon by all sides.

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
