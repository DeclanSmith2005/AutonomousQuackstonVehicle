---
title: "Team Contributions - 2nd Weekly Work Session"
date: 2026-01-22
week: 3
hours: X.X
tags: Perception, Planning, Localization, Control  
contributors: Ishaan Grewal, Nolan Su-Hackett, Rafael Costa, Declan Smith
---

# Team Contributions Log Template

## Daily Summary

In this work session, the Perception Team (Ishaan & Nolan) worked on installing Coral libraries and setting up the Coral to perform the test scripts. Rafael
and Declan worked on their respective sections of the Project Proposal Report. Topics discussed during this work session included: how to spend the budget ($50)
and what additional materials are required, reviewing the Control system architecture/feedback loops, and discussing the team's fare selection algorithm.

---

## Entry – Ishaan Grewal

**Time:** 13:50-17:00  
**Activity Type:** Setup, Testing  
**Status:** Setup (Completed), Testing (Blocked/On Hold)  
**Estimated Effort:** 3.17 h  

### Work Performed

- Installed setup_coral.sh and download_models.sh.
- Attempted to run the Coral test scripts as per the instructions (run_tests.py), however, the Perception team ran into many errors pertaining to Python being unable
  to import various modules (vision, egetpu, and GetRuntimeVersion) from the aiymakerkit. The Perception team attempted to debug these errors (which are discussed in
  the section below), but was unable to resolve them.
- Despite these errors, I successfully ran the SunFounder test script, 7.computer_vision.py, to verify the camera operation.

### Issues Encountered

- **Problem:** As mentioned above, when running run_tests.py, numerous Python errors occurred related to the inability to import the following modules from aiymakerkit:
  vision, egetpu, and GetRuntimeVersion.
- **Attempts to Address the Problem:** First, the Perception team investigated the file structure and organization for all the modules/files that were installed during
  the setup phase. Upon doing so, the team attempted to move files around to help import them since the file structure we observed was different compared to the guide
  given on the class GitBook. However, this did not work. The team then restored the file structure to its original state by uninstalling and reinstalling the
  appropriate modules. After further debugging, the team was unable to resolve the issue.
- **Impact on progress:** This issue has delayed the Perception team since they are unable to run the Coral Test scripts to ensure that the hardware is detected.
  This step is necessary to attempt the demos and begin learning how to train and test image detection and object classification models.
- **Actions Taken:** I have sent an email to Professor Paulo Araujo with a description of our issue and screenshots of our file structure and errors. I have also
  Cc'd the team's TA Eric Godden.

### Next Steps

- [ ] Maintain communication with Professor Paulo Araujo to work on debugging/fixing these issues, preferably resolve the issues before 2026-01-27, so that the
      Perception team can use the in-person lab session to begin experimenting with training and testing the models and receive help from TAs if needed.

### Reflection

The Perception Team's struggles with setting up and testing the Coral TPU reveal the immense importance of completing these setups/tests for all subsystems ASAP
to ensure that any key issues are addressed earlier on in the project. Issues like these can significantly impact progress as they block all next steps and often
require assistance from professors and/or TAs. When performing project scheduling and planning, these aspects should be considered and planned carefully. Additionally,
it would be beneficial to always include buffer space/padding in project schedules to provide appropriate time to debug or ask for help.

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
| Ishaan Grewal | 3.17 h | ✅/⚠️/❌ | Installed necessary modules(✅), successfully ran SunFounder camera test scripts(✅), ran into issues/errors with Coral test scripts(⚠️/❌). |
| Name 2 | X.X h | ✅/⚠️/❌ | Brief description |
| Name 3 | X.X h | ✅/⚠️/❌ | Brief description |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

## Team Notes

The team brainstormed and developed the following preliminary fare selection algorithm: 

---

**Entry completed**: 2026-01-24 HH:MM
