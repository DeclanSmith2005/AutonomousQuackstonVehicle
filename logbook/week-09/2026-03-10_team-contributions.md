---
title: "Team Contributions - Team Work Session"
date: 2026-03-10
week: 9
hours: X.X
tags: [Control, Integration, Testing, Refactoring, Team Sync]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith]
---

## Daily Summary

This session focused on making the control stack easier to test and more reliable during camera-guided turns. Rafael tightened mission-state publishing around the stopped state, improved server-side validation and trajectory timestamp handling, added a mock perception sender to simulate trajectory data without relying on live camera input, collected a large set of run logs, and then refactored turn execution to use snapshot-based trajectory following with velocity calibration. Sections for the remaining team members are left open below for them to document their work from the same session.

---

## Entry - Rafael Costa

**Time:** 14:30-17:30 (team session), Mar 11 follow-up commits  
**Activity Type:** Implementation, Integration, Testing, Refactoring  
**Status:** Completed  
**Estimated Effort:** 3.0 h  

### Work Performed

- Added explicit stopped-state handling to mission-state publishing so the control loop can communicate intersection-stop conditions more clearly during integration.
- Improved distance validation and timestamp handling in `control/server.py` to make trajectory snapshots more reliable and reduce ambiguity around stale data.
- Built `control/test_perception_mock.py` to simulate perception-side trajectory messages over PUB/SUB, which made it possible to test the control path without depending on live track capture.
- Collected and committed a large set of run logs from testing to support comparison between simulated and on-track behavior.
- Refactored camera-guided turn execution in `control/main.py` to use snapshot-based trajectory following instead of continuously assuming a live stream.
- Added velocity calibration support in `control/config.py` so turn behavior can be tuned against measured motion rather than fixed assumptions.

### Decisions

- Treat the stopped state as a first-class mission state so server-side coordination is clearer at intersections.
- Use trajectory snapshots with timestamp checks instead of trusting continuously updated values during turns.
- Keep a mock perception sender in the workflow so control changes can be tested independently from camera availability.

### Issues Encountered

- Testing turn behavior against live perception alone made iteration slow and hard to reproduce, which motivated the mock sender workflow.
- Trajectory freshness and distance validation needed tighter handling to avoid making turn decisions from out-of-date data.
- Camera-guided turns still required calibration support because raw trajectory following was sensitive to actual vehicle speed.

### Next Steps

- [ ] Validate snapshot-based turn following against more intersection cases on the track.
- [ ] Use the new run logs to tune velocity calibration and stopping behavior.
- [ ] Re-test the control stack with live perception after the mock-based workflow confirms baseline stability.

### References (commits from Mar 10 + Mar 11)

- `3f9868d` - Add `stopped` state handling to mission state publishing and improve distance validation in server module
- `5f3a1db` - Merge pull request #43 from `ELEC-392/adding_cte`
- `b6b583b` - Update trajectory timestamp handling in ServerManager
- `4b87014` - Add mock perception sender for testing control system
- `baccc02` - Refactor camera-guided turn implementation to use snapshot-based trajectory following and add velocity calibration

### Reflection

This session moved the control work from basic integration toward something more testable and repeatable. The main improvement was reducing dependence on perfect live perception timing by introducing better state handling, timestamp validation, and a mock trajectory source. That made the turn-control path easier to reason about and set up a cleaner base for the next round of on-track tuning.

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

**Time:** 14:30-17:30 (team session), Mar 11 follow-up commits  
**Activity Type:** Consulting, Brainstorming, Tweaking  
**Status:** Completed  
**Estimated Effort:** 3.0 h   

### Work Performed

- Spoke with Professor Paulo about issues detecting the duck, he mentioned that the object detection model is a bit of a black box but he still offered some pointers: he told us to reconsider the objects that we are training the model on and whether we need them because if not, then the model may be unnecessary clogged by useless information. After deciding which objects we really needed, he said if there still remains a problem, then maybe it could be beneficial to train separate models to be good at detecting certain classes and multiplex the models between an interval of frames.
- Spoke with Professor Matthew also about duck detection and I showed him our images, he said there were too many similar images and suggested taking more with widely different background and also to decrease the work of taking images he suggested taking a bunch, then inverting them to double the image count.
- Aiding Rafael with debugging control + CTE integration problems, like server delay, incosistent trajectory, etc.

### Decisions
- After taking the professors advice into account, we realized that the duck class is the only one that is both critical and has the potential to be reliably detectable. The perception team dropped the car class because it would be hard to classify the wheels correctly, if both our car and others are moving, and there is always the large riske of misclassification which could cause random stops. While the same can be said for ducks, they arem uch more critical because there are more ducks and there is a higher change that our car would run into them without ultrasonic detection due to their small size.
- The signs on the road were unimportant as well, since this is information that can be encoded into our graph with 100% accuracy.


### Issues Encountered
- duck classification unreliable

### Next Steps

- Annotate the extra 60 duck images
- train a model with only ducks then evaluate it performance

### Reflection

This session made me reflect on the importance of critically evaluating a design problem so that we aren't doing unnecessary work, which can overcomplicate the process. After speaking with Professor Paulo and Professor Matthew, we realized that our duck detection issues were not just about model performance, but also about the way we had defined the perception task and collected data. Their feedback helped us recognize that trying to detect too many unnecessary classes was likely hurting the model, and that our duck dataset needed more variety rather than just more of the same images. I think the team made a strong decision by narrowing the model to focus only on ducks, since duck detection is both more critical to safety and more realistically achievable than detecting cars or road signs.

---

## Entry - Declan Smith

**Time:**   14:30-17:30 (team session)
**Activity Type:** Code Writing, Clarification with Teaching Team
**Status:** In-Progress  
**Estimated Effort:** 3 hrs  

### Work Performed
- Discussed with one of the TA's what was going wrong with VPFS. We discovered that I needed to use the team number 0 in order for the dummy VPFS simulation to work, which I hadn't understood from the previously provided documentation. Furthermore, I needed some clarification as to whether we should be using 2 (duclair-2) for our team number, or 11 (our kit number). Between these new pieces of information and the teaching team's work to finalize VPFS, I was able to get a simulation of a fare working.
- While the intermediate nodes between the start and end locations were correct for the fare simulation, I found that sometimes it was inaccurately modelling the start and end locations properly, so some time was spent debugging the path-finding code and trying to make it more accurate.
- Furthermore, and more concerning than the previous step, the algorithm wasn't always correctly categorizing turns properly, so I need to look at the algorithm in more depth and correct it. 

### Decisions
- started using vectors in the "navigate" function to determine the heading of the car to eliminate nodes as options in the adjacency matrix directly behind the heading of the car. 

### Issues Encountered

- Inaccurate turn classification
- Incorrect starting nodes

### Next Steps

- [ ] Now that the VPFS simulation is working correctly, need to continue to test and refine algorithms to get them right

### References

- NA.

### Reflection

The bottleneck coming from issues related to getting VPFS simulations working has been lifted, meaning I have the opportunity to invest as much time as necessary into perfecting my code. It seems to be working most of the way so far, but it no doubt needs lots of tweaking to get it just right. The final step will be making sure that I'm correctly sending off directions to Raphael so that the car itself takes the right path. 

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
| -------- | ------- | -------- | ------------------ |
| Rafael Costa | 3.0 h | ✅ | Stopped-state integration, mock perception testing, snapshot-based turn refactor |
| Ishaan Grewal | TBD | TBD | To be completed |
| Nolan Su-Hackett | 3.0 h | ✅ | Duck Images, Consulting with professors|
| Declan Smith | 3.0h | In-Progress | Continued to improve turn classification and path finding |

---

## Team Notes

Rafael's control-side work in this session centered on making perception-driven turning testable without always requiring full subsystem coordination. Additional notes from the rest of the team can be added here once their entries are completed.

---

**Entry completed**: 2026-03-29
