---
title: "Team Contributions - Team Work Session"
date: 2026-03-23
week: 11
hours: X.X
tags: [Control, Recovery, Configuration, Logs]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

Mar 23 continued refinement of turning parameters, state handling, and server logic. Multiple configuration changes and recovery improvements were added, along with additional run logs (for Mar 22) committed for analysis.

---

## Entry - Rafael Costa

**Time:** 10:00-23:45 (individual work / commits on Mar 23)  
**Activity Type:** Tuning, Refactoring, Logging  
**Status:** Completed / Iterating  
**Estimated Effort:** 5.0 h

### Work Performed

- Tuned turning speeds (e.g., `TURN_ENTRY_SPEED`) and adjusted recovery timeouts to improve maneuverability and line re-acquisition.  
- Added or updated server-side handling for fare status and polling logic, improving mission queue behavior.  
- Increased recovery time and history duration to make line recovery more robust.  
- Committed run logs for Mar 22 to support PID and trajectory tuning.  
- Added DUCK_WAIT configuration and implemented delay for duck detection in the main control loop.

### Decisions

- Increase conservative timeouts for recovery to reduce oscillation during re-acquisition.  
- Add explicit duck-detection wait behavior to reduce false positives during motion.

### Issues Encountered

- Tuning tradeoffs: faster turn entry speeds improve responsiveness but require better recovery handling; moved config toward safer defaults while iterating.

### Next Steps

- Test updated turn-entry speeds and recovery timeouts on track with the new run logs to validate expected improvements.  
- Continue to pare down unused subscription/localization logic to simplify the server code base.

### References (Mar 23 commits)

- `685615d` - Adjust TURN_ENTRY_SPEED for improved maneuverability and comment out unused limit switch logic in main control flow  
- `2a17dd8` - Implement the main robot control program including line following, advanced turning, recovery, and mission management, along with a server export utility for pathing.  
- `cb49106` - Implement the core server logic for automated fare selection, navigation, and ZMQ communication.  
- `01ad602` - Update configuration and server ports for improved communication and performance  
- `4cb38a9` - Increase recovery timeout and history duration for improved line recovery handling  
- `0912fa2` - Refactor fare status handling to improve polling logic and remove unused subscription  
- `79a3e64` - Update robot state handling in main control loop to include IDLE state  
- `ba886b9` - Add run logs for March 22, 2026

### Reflection

Mar 23 was a refinement/tuning pass that made sensible conservative changes to recovery and turning behavior while adding logs to validate future adjustments. The balance between responsiveness and safe recovery remains a tuning goal.

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

**Time:** 19:00-5:30
**Activity Type:** Implementation, Integration, Configuration  
**Status:** Completed
**Estimated Effort:** 10.5h

### Work Performed

- Attempted fixes on ROI filtering, this ROI filtering is used to cut off parts of the frame of the camera to make it so that we don't detect ducks outside of our driving path. It does this by cuttong off the l eft and right sides past the lane markings and will cut off anything past a white boarder at the top of the frame, this is to stop our detection from getting ducks that were inside the white borders where the buildings eventually went.
- Our fixes including getting rid of the left and right borders as we realised we were over engineering, and instead of having those we could just use a trapezoid mask to filter out the direct lane, then just keep the white filtering.
- Helped again with finding correct tuning parameters
- tested integration with VPFS API and car
- fully implemented cross walk code
- implemented stops when arriving at the location of pickup/dropoff
- added roundabout states from map i.e, roundabout_entry, roundabout_circulate, and roundabout_exit.

### Issues Encountered
- Car was not stopping when it was at the dropoff
- car would not stop to begin with at either pickkup or dropoff (this was fixed)
- the ROI filtering would cut out too much of the lane, and had trouble finding the yellow dotted lines which would make the left side filter fit poorly (this was fixed by simplifying the code and just filtering for the white border at the top)
- car still was not turning consistently
- due to the amount of cars online at the same time, the ssh would consistently disconnect
- When car completes the mission state, all functionality stopped and stopped receiving instruction from planning even though it should constantly keep receiving directions
- we needed a roundabout state
### Decisions
- simplifying filtering process
- decided on final parameters for inner wheel PWM, and outer wheel PWM
- Decided on final steering angles for the car
  

### Next Steps
- Test the simplified ROI filtering more to confirm it stays reliable across different lane conditions.
- Fix the mission-complete behavior so the car continues receiving directions from planning after finishing a task.
- Keep testing the final PWM and steering values to verify that turning is consistently stable.
- Validate the new pickup, dropoff, crosswalk, and roundabout states during full integration runs.
- if those couldn't be done before competition then atleast complete the following:
- ensure wire connections to hardware is intact (limit switch, brake lights, signal lights).
- decorate the car as it is well overdue.
### Reflection

This session showed that we have a tendency to overcomplicate situations, and that sometimes a simpler solution can be more effective. Especially considering the hardware limitations, even if the ROI filtering had been good, the amount of image processing that needed to be done on the pi could introduce other problems down the line. A key moment was realising that the left and right filtering was over engineered and that a trapezoid would cut off the majority of the problems, the only thing that it wouldn't be able to deal with would be turns. This was the reason we wanted to do it in the first place, but due to the fact that we haven't programmed the camera to move during turns, the car was never going to detect ducks on a curved turn to begin with. Going forward, we should more deeply consider what is important and what is feasible, we should prioritize reliability and simplicity so that the overall system behaves predictably during full runs.

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
| Rafael Costa | 5.0 h | ✅ | Turning & recovery tuning, server/fare handling, run logs |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | TBD | TBD | To be completed |
| Declan Smith | TBD | TBD | To be completed |

---

**Entry completed**: 2026-03-27
