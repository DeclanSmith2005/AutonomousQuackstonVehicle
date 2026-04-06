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

---

## Entry - Nolan Su-Hackett

**Time:** 14:30-16:30 (team session)
**Activity Type:** Testing Control, Testing Duck Detection, Testing Integration
**Status:** Completed  
**Estimated Effort:** 2.0 h  

### Work Performed

- Testing Duck only object detection model after making it the sole focus of the training.
- Testing More Turns using CTE and Control, with an emphasis on the find line functionality.
- Debugging issues and thinking of solutions for issues that arose in the process, detailed in the issues section


### Issues Encountered

- Turns are weak, as if one of the wheels are not touching the ground on a turn, this can't be a battery problem like we thought last week because when we tested today the car was fresh and was on full charge.
- Wheels would turn correctly but didn't have enough traction to direct the car correctly on the turn, would drift, and would sometimes even go in the direction opposite of the front turned wheels.
- Server delays from when CTE detects the line and when control receives it. it may not be due to CTE sending side, as testing with prints in the terminal confirmed that they sent and received close to the same time, the issue is with the car actually reacting to this sent signal fast enough.
- Detection would draw bounding boxes around other things that aren't duck, so misclassification happens often, despite this, duck detection it self is pretty reliable.

### Decisions
- Tried taping the wheel brackets together so that the wheel will be closer to the ground
- Tried putting Rubber Bands around the wheel that was having difficulty touching the ground, to add more width to the wheel aswell as add traction potentially.
- Tried the keyboard_control.py file to see if the issue was with the car or with some parameter in our code, and it turned out that the car could drive much better on the keyboard control file. We checked the parameters and realised that the PWM that was used in the keyboard control file was much higher than our turning PWM. After increasing our PWM the issue was resolved for the most part, atleast for the turning, but there still remained the problem of the delays.

### Next Steps

- Tune PWM and steering further using the updated working range.
- Measure the delay at each stage of the system to find where response time is being lost.
- Improve duck detection by reducing false positives through dataset or filtering changes.
- Run more tests with the updated PWM to confirm turning is consistently reliable.

### Reflection

This session showed that the issue with the turning was not only the battery level but may have been a mix of that paired with other parametric issues. It is odd that the PWM we used last time worked fine and that now it is having problems but that goes to show again that hardware is not always reliable and that as engineers, we need to work inside a tolerance. The most important moment was figuring out how we can isolate the issue, and this was done by running the keyboard control program. It goes to show the importance of having a structured debugging approach, like trying things that we've known to work in the past instead and comparing it to the problem we are facing instead of trying new solutions. In the future we should first test out software and parameter assumptions against a baseline software that we have been provided with like the sunfounder code, then move to hardware changes if those fail as a debugging tool.



---
