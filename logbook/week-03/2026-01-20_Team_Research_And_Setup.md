---
title: "Team Contributions - [Research and Setup Session]"
date: 2025-01-20
week: 3
hours: 2.0
tags: [teamwork]
contributors: [Nolan Su-Hackett, Ishaan Grewal, Rafael Costa, Declan Smith]
---

## Daily Summary

Control:
Research on PID, finding out key information that might be necessary for implementation.

Planning:
Researching: path finding algorithm and potential implementation with given map.

Perception:
Figuring out what setup needs to be completed on perceptions side, Coral software, virtual environment ETC

---

## Entry – [Nolan Su-Hackett]

**Time:** 14:30–16:30  
**Activity Type:** [Setup]  
**Status:** [In Progress]  
**Estimated Effort:** 2.0 h  

### Work Performed

- read through some Coral Documentation provided on the gitbook link
- created ssh key for Raspberry Pi
- cloned github repo onto Pi
- performed setup_picarx.sh and attempted the setup_coral.sh however perception subteam ran out of time

### Issues Encountered

- Issue: realised that Raspberry Pi needs its own ssh key, perception ran into issues as the ssh key was made for a personal workstation and not the Pi. 
- Impact: took some time to debug and realise that the Pi required its own key.

### Next Steps

- Finish downloading the setup script for coral onto the Pi
- testing some camera scripts using Coral

### References

-N/A

### Reflection

- After cloning the repo, setup seems to be going smoothly, highly optimistic for testing camera scripts.

---

## Entry – [Ishaan Grewal]

**Time:** 14:30–16:30  
**Activity Type:** [Setup]  
**Status:** [In Progress]  
**Estimated Effort:** 2.0 h  

### Work Performed

- read through some Coral Documentation provided on the gitbook link
- created ssh key for Raspberry Pi
- cloned github repo onto Pi
- performed setup_picarx.sh and attempted the setup_coral.sh however perception subteam ran out of time

### Issues Encountered

- Issue: realised that Raspberry Pi needs its own ssh key, perception ran into issues as the ssh key was made for a personal workstation and not the Pi. 
- Impact: took some time to debug and realise that the Pi required its own key.

### Next Steps

- Finish downloading the setup script for coral onto the Pi
- testing some camera scripts using Coral

### References

-N/A

### Reflection

- N/A

---

## Entry – [Rafael Costa]

**Time:** 14:30–16:30  
**Activity Type:** [Research & Planning]  
**Status:** [In Progress]  
**Estimated Effort:** 2.0 h 

### Work Performed

Research on PID:

PID
Things to control:
1.	Keeping in lane
  a.	Use gray-scale sensor (voltage level) + camera (distance from middle line) inputs.
  b.	Cascaded system one PID looping feeding into the other. 
    i.	https://stackoverflow.com/questions/50911973/how-to-program-a-pid-control-of-one-variable-with-two-variable-inputs 
2.	Speed
  a.	Car goes full speed all the time roughly. Can do experiments to test the speed (not very fast). Use GPS to confirm location, but should be only for redundancy. 

Insight/Idea: Speed can be approximated using how fast the pixels of a certain object increase on the camera?

### Issues Encountered

- How to measure current speed?

### References

-N/A

### Reflection

- N/A

---

## Entry – [Declan Smith]

**Time:** 14:30–16:30  
**Activity Type:** [Research & Planning]  
**Status:** [In Progress]  
**Estimated Effort:** 2.0 h 

### Work Performed
Brainstorming Key Questions that must be solved for Path-Finding

- How many nodes to create
  - how many nodes can be processed?
- Where to Place Nodes
- Algorithm? all-Pairs-shortest path?
- How to overlay a directed graph of nodes on the given map without manual graph creation

### Next Steps

- create sample functions that assume given inputs like (x,y) coordinates or information from perception like an object

### References

- N/A

### Reflection

- N/A

---


## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Nolan Su-Hackett | 2.0 h | ⚠️ | Coral Setup |
| Ishaan Grewal | 2.0 h | ⚠️ | Coral Setup |
| Rafael Costa | 2.0 h | ⚠️ | Control Research |
| Declan Smith | 2.0 h | ⚠️ | Mapping/Path-Finding Research |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

## Team Notes

N/A

---

**Entry completed**: 2025-01-20 19:19
**Reviewed By**: 