---
title: "Team Contributions - 3rd Weekly Work Session"
date: 2026-01-27
week: 4
hours: 12.0
tags: Perception, Planning, Control, Hardware
contributors: Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith
---

# Team Contributions Log Template

> **Instructions**: Use this template when multiple team members work on the same day and you want to track individual contributions. Save as: `logbook/week-XX/YYYY-MM-DD_team-contributions.md`

## Daily Summary

In this session, the group focused on hardware troubleshooting and specific subsystem development. The Perception Team (Ishaan & Nolan) collaborated with Professor Paulo and Matthew to resolve persistent Coral TPU connectivity issues, which were ultimately traced to a faulty cable. Rafael (Control) developed and refined test scripts for steering and speed control, though environmental conditions in the studio prevented data collection. Declan (Planning) focused on the modeling of the Quackston map.

---

## Entry – [Rafael]

**Time:** 14:30-17:30 
**Activity Type:** [Software Development / Testing]  
**Status:** [In progress]  
**Estimated Effort:** 3.0 h

### Work Performed

- Developed and modularized test code to facilitate precise calibration of the steering servo angles.

- Implemented software hooks to allow for incremental increases and decreases in motor PWM speed during live testing.

- Conducted preliminary maneuverability assessments on the studio floor to evaluate vehicle handling.

- Investigated the impact of environmental surface conditions on tire traction and lateral slip.

### Decisions

- Postponement of Turning Radius Data Collection: It was decided to delay formal data collection for the steering-to-radius lookup table. The studio floor conditions (dust and salt) were unrepresentative of the competition track, and data collected would likely lead to inaccurate PID tuning and localization errors.

- Incremental Control: Opted for a "step-increment" approach for speed and steering tests to allow for safer debugging before full autonomous state transitions are implemented.

### Issues Encountered

- Problem: Environmental surface contamination (dust/salt) caused significant tire slippage during high-angle turns.

- Mitigation: Testing was shifted toward verifying software logic and servo responsiveness rather than recording physical displacement metrics.

### Next Steps

- [ ] Execute formal turning radius trials on a clean surface (ideally the Quackston track) to populate the geometric lookup table.

- [ ] Integrate the new precise servo control logic into the CORNER state of the main Finite State Machine (FSM).

### Reflection

This session highlighted how physical environment variables like surface friction can invalidate theoretical models. While the lack of data collection was a minor setback, the time was effectively used to refine the underlying control code.

---

## Entry – [Team Member Name 2]

**Time:** HH:MM–HH:MM  
**Activity Type:** [Implementation / Testing / Design / Documentation / Project Management / Hardware]  
**Status:** [Completed / In progress / Blocked / On hold]  
**Estimated Effort:** X.X h  

### Work Performed

- 
- 

### Decisions

*Optional section - include if applicable*

- 

### Issues Encountered

*Optional section - include if applicable*

- 

### Next Steps

*Optional section - include if applicable*

- [ ] 

### References

- 

### Reflection



---

## Entry – [Team Member Name 3]

**Time:** HH:MM–HH:MM  
**Activity Type:** [Implementation / Testing / Design / Documentation / Project Management / Hardware]  
**Status:** [Completed / In progress / Blocked / On hold]  
**Estimated Effort:** X.X h  

### Work Performed

- 
- 

### Decisions

*Optional section - include if applicable*

- 

### Issues Encountered

*Optional section - include if applicable*

- 

### Next Steps

*Optional section - include if applicable*

- [ ] 

### References

- 

### Reflection



---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 3.0 h | ⚠️ | Developed precise servo and speed control test scripts; evaluated environmental impacts on traction. |
| Name 2 | X.X h | ✅/⚠️/❌ | Brief description |
| Name 3 | X.X h | ✅/⚠️/❌ | Brief description |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

## Team Notes

Any collective observations, cross-functional issues, or team-level decisions that span multiple individual contributions.

---

**Entry completed**: YYYY-MM-DD HH:MM
