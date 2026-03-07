---
title: "Team Contributions - Team Work Session"
date: 2026-03-03
week: 8
hours: X.X
tags: [Control, Refactoring, Testing, Logging, Team Sync]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

This team work session centered on stabilizing and cleaning the control stack before deeper CTE integration. Rafael refactored deadband handling into shared configuration, cleaned structure in control modules, expanded log-analysis capability, and collected a large set of run logs for tuning. The team also continued integration planning across subsystems. Teammate sections are left open below so each member can add their own details.

---

## Entry - Rafael Costa

**Time:** 14:30-16:30 (team session), Mar 4 follow-up commits  
**Activity Type:** Implementation, Refactoring, Testing, Documentation  
**Status:** Completed  
**Estimated Effort:** 2.5 h  

### Work Performed

- Refactored deadband usage in the control loop so tuning is driven by `config.DEADBAND` instead of hardcoded values.
- Continued codebase cleanup for readability/maintainability in core control files.
- Updated PID analysis workflow by refactoring `control/analyze_logs.py` and tuning-related values in `control/config.py`.
- Collected and committed many additional `run_log_*.csv` datasets to support data-driven tuning.
- Updated prior week team-contribution logbook files for consistency and detail quality.

### Decisions

- Keep deadband and tuning values centralized in configuration to reduce drift between files.
- Use logged run data as the main input for next PID adjustments instead of ad-hoc on-track tweaks.

### Issues Encountered

- Large parameter surfaces (deadband, thresholds, gains) made one-pass tuning unreliable; this was addressed by organizing more run logs and improving analysis script outputs.

### Next Steps

- [ ] Compare log statistics before/after deadband refactor to validate stability gains.
- [ ] Continue tuning `control/config.py` values using analyzed anomalies.
- [ ] Prepare control-side interfaces for Perception CTE updates.

### References (commits from Mar 3 + Mar 4)

- `0b84708` - Refactor deadband handling to use `config.DEADBAND`
- `ac21aa4` - Refactor code structure for readability/maintainability
- `ea2ce45` - Refactor log analysis and update PID-related config
- `4a28565` - Update previous team-contribution log entries

### Reflection

This session improved the maintainability of the control pipeline and set up cleaner tuning iteration loops. Moving key behavior to shared config and strengthening log-analysis workflows reduced trial-and-error and should make upcoming CTE-control integration safer.

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

**Time:** 14:30-16:30 (team session) 
**Activity Type:** Data Collection, Testing  
**Status:** Completed  
**Estimated Effort:** 2.5 h  

### Work Performed

- Tested Object detection model iteration where the car class only included images of cars from a side view
- Took more images of the duck class (60) with a different background and some images when the duck is on the track to help guide the model.
- Annotated new duck images
- Brainstorm with Control (Rafael) on what he would like from CTE 
- Split work with Ishaan regarding CTE, since Ishaan completed some turn filtering work, I will work on cleaning it up a bit more, and getting y_reference points so they can be passed to control.

### Issues Encountered

- Model still struggles to detect the duck class

### Next Steps

- [ ] Test the new model to see if the duck class improves
- [ ] Finish Development of CTE
- [ ] Discuss with a Professor on issues with duck detection

### Reflection

As the demo day approaches there are still quite a few unfinished tasks/problems that are critical to the success of the project, things like duck detection, CTE, VPFS, and integration. Despite this the team has set clear timelines for when we are expected to have these tasks completed, I think that our continued consistency regarding meeting twice a week is helping the team keep on track and manage our time well. If the duck detection and CTE are completed by next tuesday then I think that perception will be in a great spot to start integrating and helping out other parts of the team. 

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
| Rafael Costa | 2.5 h | ✅ | Control deadband/config refactor, log analysis improvements, run-log collection |
| Ishaan Grewal | [Add] | [Add] | [To be added] |
| Nolan Su-Hackett | 2.5h | ✅ | Data Collection, Annotation |
| Declan Smith | [Add] | [Add] | [To be added] |

---

**Entry completed**: 2026-03-07
