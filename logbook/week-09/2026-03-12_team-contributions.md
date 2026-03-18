---
title: "Team Contributions - Team Work Session"
date: 2026-03-12
week: 9
hours: X.X
tags: [Control, Testing, Refactoring, Safety, Team Sync]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

This session focused on simplifying the control path, tuning motion behavior through testing, and adding safety behavior for duck detection. Rafael removed unused control logic and legacy trajectory-handling paths, streamlined distance processing in the server interface, adjusted motion parameters and turn timing based on testing, added pivot-turning code, collected an extensive new batch of run logs, and then added duck safety stop and horn behavior with clearer comments in the control code. Sections for the remaining team members are left open below for them to document their own contributions from the same session.

---

## Entry - Rafael Costa

**Time:** 14:30-16:30 (team session), Mar 12 follow-up testing  
**Activity Type:** Refactoring, Testing, Tuning, Safety Integration  
**Status:** Completed  
**Estimated Effort:** 3.0 h  

### Work Performed

- Removed unused integral-related logic from `control/pid_controller.py` and cleaned up legacy distance-key support in `control/server.py` to keep the turn-control path focused on the data that is actually being used.
- Simplified distance handling in `ServerManager` so trajectory data processing is more direct and easier to maintain.
- Updated motion parameters in `control/config.py`, added a delay in turn execution within `control/main.py`, and implemented pivot-turning code to improve real-world turning behavior during testing.
- Ran an extensive testing pass and committed a large number of `run_log_20260312_*.csv` files to capture how the system behaved under repeated trials.
- Added duck safety stop and horn behavior, along with clearer control-flow comments, so obstacle-response behavior is more explicit in the main control loop.
- Updated `control/server.py` to better support the new safety-oriented flow and surrounding control logic.

### Decisions

- Remove dead code and legacy compatibility paths when they no longer match the active trajectory contract.
- Tune motion behavior using repeated log-backed test runs rather than single-pass adjustments.
- Integrate duck-response safety directly into the control loop so stop behavior is deterministic once detection input is available.

### Issues Encountered

- Older unused control paths were making it harder to reason about the active turn pipeline and needed to be removed before more tuning.
- Turn execution still needed timing adjustments to better match the real vehicle response seen during testing.
- Safety behavior had to be added carefully so it would not conflict with existing stop-state and turn-state handling.

### Next Steps

- [ ] Validate duck safety stop behavior end-to-end with live perception detections.
- [ ] Review the Mar 12 run logs to identify whether the added turn delay improved consistency.
- [ ] Continue tuning motion parameters now that the control path is simpler and the safety logic is in place.

### References (commits from Mar 12)

- `f856fbc` - Remove unused integral calculation and legacy distance key support in PIDController and ServerManager
- `b505910` - Refactor distance handling in ServerManager to streamline trajectory data processing
- `ba034bc` - Update motion parameters and add delay in turn execution for improved control
- `d5b8150` - Testing
- `ad4b28c` - Add duck safety stop/horn behavior and improve control comments

### Reflection

This session was mainly about reducing complexity before adding another important behavior. Cleaning up dead paths and simplifying the server interface made the control flow easier to tune, and the large batch of logs gives a much better basis for evaluating those changes. Adding duck safety behavior on top of that work was a useful step because it pushed the control loop closer to competition-relevant behavior instead of only improving internal structure.

---

## Entry - Ishaan Grewal

**Time:** TBD  
**Activity Type:** TBD  
**Status:** TBD  
**Estimated Effort:** TBD  

### Work Performed

- To be completed.

### Decisions

- To be completed.

### Issues Encountered

- To be completed.

### Next Steps

- [ ] To be completed.

### References

- To be completed.

### Reflection

To be completed.

---

## Entry - Nolan Su-Hackett

**Time:** TBD  
**Activity Type:** TBD  
**Status:** TBD  
**Estimated Effort:** TBD  

### Work Performed

- To be completed.

### Decisions

- To be completed.

### Issues Encountered

- To be completed.

### Next Steps

- [ ] To be completed.

### References

- To be completed.

### Reflection

To be completed.

---

## Entry - Declan Smith

**Time:** TBD  
**Activity Type:** TBD  
**Status:** TBD  
**Estimated Effort:** TBD  

### Work Performed

- To be completed.

### Decisions

- To be completed.

### Issues Encountered

- To be completed.

### Next Steps

- [ ] To be completed.

### References

- To be completed.

### Reflection

To be completed.

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
| -------- | ------- | -------- | ------------------ |
| Rafael Costa | 3.0 h | ✅ | Control-path cleanup, pivot-turning update, motion tuning, test-log collection, duck safety stop/horn |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | TBD | TBD | To be completed |
| Declan Smith | TBD | TBD | To be completed |

---

## Team Notes

Rafael's portion of this session was about making the control loop simpler, better tuned, and safer before further subsystem integration. Additional notes from the rest of the team can be filled in once their individual summaries are available.

---

**Entry completed**: 2026-03-12