---
title: "Team Contributions - 2nd Weekly Work Session"
date: 2026-01-22
week: 3
hours: 12.17 hrs
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

## Entry – [Rafael Costa]

**Time:** 14:00-17:00  
**Activity Type:** Design / Documentation  
**Status:** In progress
**Estimated Effort:** 3.0 h  

### Work Performed

- Participated in the initial project proposal meeting to define system architecture for perception, localization, planning, and control.

- Researched and proposed a cascaded PID control system for lane keeping, utilizing dual inputs from grayscale sensors (voltage level) and camera data (lateral distance from centerline).

- Investigated speed control strategies, initially considering a constant speed approach with GPS for location redundancy.

- Conducted hardware verification tests on ultrasonic sensors and established basic Raspberry Pi connectivity.

- Identified and sourced 3D printing models for vehicle components, including a front bumper and LED mounts.

- Contributed to the perception strategy by researching monocular camera distance estimation using pixel-to-length calibration and triangle-based distance calculations.

- Delegated proposal report tasks, taking responsibility for the Control system details, Cost Proposal (Section 6), and Deliverables (Section 8).

### Decisions

- Adopted a "black box" interface approach between Planning and Control modules.

- Selected a node-based graph system for pathfinding using Dijkstra’s or A* algorithms.

- Decided to utilize the $50 budget for extra hardware, specifically additional ultrasonic sensors and signaling LEDs.

- Agreed to use Google Colab for CV training to bypass local machine speed limitations.

### Issues Encountered

- Determined that current hardware is insufficient for full functionality; identified the need for two extra ultrasonic sensors and an emergency stop button.

- Acknowledged that limited lab time necessitates a supplemental weekly meeting schedule to ensure progress.

### Next Steps

- [ ] Develop the Control system technical details for Section 3 of the proposal.

- [ ] Draft Section 6 (Cost Proposal and Budget) and Section 8 (Deliverables and Outcomes).

- [ ] Prepare Appendix B (Team Operating Agreement).

- [ ] Test base PID parameters on the PiCar-X during the upcoming Tuesday lab session.

### References

- Tuning Cascade Loops: https://www.controlsoftinc.com/tuning-cascade-loops-2/

- Cascade Control Benefits: https://www.watlow.com/blog/posts/benefits-of-cascade-control

- MathWorks PID Design: https://www.mathworks.com/help/control/ug/designing-cascade-control-system-with-pi-controllers.html

- Robot PID Example: https://projects.raspberrypi.org/en/projects/robotPID/0

- PiCar-X 3D Model Resources: https://mischianti.org/building-and-programming-picar-x-getting-started-with-your-robot-car/

- Sunfounder Bumper Model: https://www.printables.com/model/1288585-sunfounder-picar-x-front-bumper

### Reflection

The initial transition from high-level goals to concrete system architecture highlighted the complexity of integrating diverse sensor inputs. Researching the cascaded PID system confirmed that decoupling the faster grayscale corrections from the slower camera-based environmental analysis is critical for stability. My focus for the upcoming week will be translating these technical research points into a formal proposal while preparing for physical hardware testing to validate our theoretical control model.

---

## Entry – [Nolan Su-Hackett]

**Time:** 13:45–17:00  
**Activity Type:** [Testing/Setup]  
**Status:** [Setup (Completed), Testing(in-Progress)]  
**Estimated Effort:** 3.0 h  

### Work Performed

- Finished downloading setup_coral.sh script file from last session
- Explored coral directory to gain understanding of the file organization
- Attempted to run basic coral tests in the aiy maker kit, discovered that our file organization is slightly different than that described in the gitbook
- ran into errors and tested some solutions, like moving files directly next to the one we wanted to run to try to solve the import problems however this caused more errors as we chanaged the file organization
- Ultimately reinstalled the coral script again from scratch to avoid convolution and to allow us to escalate the problem to TA's/Profs without a disorganized file structure.

### Issues Encountered

- the python file run_tests.py could not seem to find many files that was necessary for its operation. Traceback errors of note were related to importing the vision.py file as well as messages related to libedgetpu. Attempted moving files around and looking for files like vision, which we did find but could not figure out why it had trouble getting imported.

### Next Steps

- Escalated to Professor Araujo, who has kept contact with the team and suggests that there may be a problem with the CORAL TPU, he said to bring the question to the tuesday lab for further debugging.

### Reflection
The issues that the perception team is currently dealing with show the importance of setting things up immediately. Although setup may seem quick and easy there are often problems which MUST be resolved before the actual implementation of the project can even start. This session also taught us a valuable lesson, knowing when to escalate issues to those more experienced and when to spare our time to focus on other parts. After the perception team troubleshooted as much as possible we turned our attention to reading further documentation on the coral and machine learning to gain a headstart on project research while we waited for a response from professors.


---

## Entry – [Declan Smith]

**Time:** 13:45–17:00  
**Activity Type:** [Design / Documentation]  
**Status:** [Design(In progress), Documentation(Completed)]  
**Estimated Effort:** 3 h  

### Work Performed

- Report writing for the project proposal document. I was personally responsible for the section on the problem statement/understanding, as well as a description of the design choices for the planning subsystem and a description of the team's use of GitHub during the project.
- I planned the implementation of a Python script which will output directions for the car to move based on a graph of the map layout. After planning was complete, I began working on the code, which is currently partially complete. 

### Decisions
- Decided to use a sparsely populated graph to model the map environment for wayfinding purposes, as well as to use an implementation of Dijsktra's pathfinding algorithm to provide directions to the car for navigating the map.
- Decided to implement graph design using a Python script reading out of a txt file.
- Decided that the output of the algorithm would be waypoint coordinates to pass to other device subsystems, which the car will directly move toward.


### Next Steps

*Optional section - include if applicable*

- Continue to develop and test the path finding Python script.  

### References
- https://www.geeksforgeeks.org/dsa/dijkstras-shortest-path-algorithm-greedy-algo-7/

### Reflection
The team is working well and making good progress towards the development of the autonomous vehicle. The pathing subsystem feels well thought out for now. It's important to get a strong first attempt working so that integration with the other systems can begin and refinements can be made early in the development cycle to come to a strong finished product. 


---

## Key Team Decisions Made

The team brainstormed and developed the following preliminary fare selection algorithm. The goal behind this algorithm is to identify the true benefit of a certain fare, which is accomplished by considering the cumulative distance between the vehicle's current position and the fare destination. In particular, this was chosen because the vehicle will rarely be close to the fare pickup location, and hence, must travel that distance initially. Furthermore, all distances (current vehicle location to pickup, and pickup to dropoff) are calculated using the team's pathfinding algorithm, which represents the true distance cost of the fare. By computing this distance for each available fare, the team will be able to find the $/distance earned for each fare and select the fare that generates the most profit per unit time. Below is the team's fare selection formula: 

(Base Fare+(Distance Based Fare*Fare Distance))/(Cumulative Distance Between Current Position and Fare Completion)

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Ishaan Grewal | 3.17 h | ✅/⚠️/❌ | Installed necessary modules(✅), successfully ran SunFounder camera test scripts(✅), ran into issues/errors with Coral test scripts(⚠️/❌). |
Rafael Costa|2.5 h|⚠️|Conducted hardware verification on ultrasonic sensors and Pi connectivity ; researched and proposed a cascaded PID control system and discrete state machine for dynamic speed ; delegated proposal report tasks for the control, cost, and deliverables sections.
| Declan Smith | 3.0 h | ✅/⚠️ | worked on navigation python file(⚠️) and wrote project propsoal sections(✅) |
| Nolan | 3.0 h | ✅/⚠️/❌ | Installed Coral and picar setup ✅, ran camera ✅, coral TPU not working as intended, maybe error with TPU or wire? ⚠️/❌|

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

**Entry completed**: 2026-01-27 7:43 PM
