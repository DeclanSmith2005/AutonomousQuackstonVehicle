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
| Rafael Costa | 5.0 h | ✅ | Turning & recovery tuning, server/fare handling, run logs |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | TBD | TBD | To be completed |
| Declan Smith | TBD | TBD | To be completed |

---

**Entry completed**: 2026-03-27
