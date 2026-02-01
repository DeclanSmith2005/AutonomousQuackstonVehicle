---
title: "Team Contributions - 3rd Weekly Work Session"
date: 2026-01-27
week: 4
hours: 12.0
tags: Perception, Planning, Control, Hardware
contributors: Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan Smith
---

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

## Entry – Ishaan Grewal

**Time:** 14:30-16:30  
**Activity Type:** Hardware Debugging / Implementation / Perception  
**Status:** Completed/In Progress  
**Estimated Effort:** 2.0 h  

### Work Performed
- Worked with Professor Paulo and Matthew to debug and resolve the TPU connectivity issues. The issue was found to be the use of the incorrect cable. TPU is now connected.
- Set up FileZilla for file transfer to and from the Raspberry Pi.
- Tested SunFounder object detection algorithm/code on a water bottle as an example.
- Read through and familiarized myself with the Google Colab model training process.
- Partially completed the European Road Sign Detector Tutorial in Colab since we ran out of time to train the model (it takes 20 minutes to train and another 20 minutes to test).


### Next Steps

- [ ] Complete the European Road Sign Detector Tutorial in Colab, and run the trained model on the Raspberry Pi.
- [ ] Calibrate and test the grayscale sensor.
- [ ] Calibrate and determine the optimal camera tilt angle on the track.
- [ ] Visit the Quackston map in person


### Reflection
This session illustrated how small things (such as using the incorrect USB-C to USB-A) cable can cause large issues in development and testing. In the previous week, the Perception team spent many hours attempting to debug the errors they were getting when running object detection models on the Coral. During this debugging, the team was focused on software-related errors, while the true error was a minor hardware cable issue. Hence, a key takeaway from this session is that it is important to look at the complete picture of a problem. In retrospect, in the case of the TPU issue, the team should have checked to see if the TPU was connected properly/being recognized by the Pi first, rather than diving into the software issues in front of them. Additionally, the team did not know that there was a Python script to detect connected TPUs. Thus, it is important to explore all the provided debugging scripts since this would have revealed that the TPU wasn't being recognized and would have enabled quick identification of the cable issue. Going forward, these are key lessons/tips to keep in the back of our minds.


---

## Entry – [Nolan Su-Hackett]

**Time:** 14:30-16:30  
**Activity Type:** Hardware Debugging / Implementation / Perception  
**Status:** Completed/In Progress  
**Estimated Effort:** 2.0 h   

### Work Performed

- Identified and corrected issue with Coral, after attempting another coral TPU it was identified that the new coral was not detected. This meant that the
issue was not with the coral but with something else, so the Professor tried multiple cables and found the correct one, this was the problem.
- Tested run_tests.py and classify_image.py while connecting to the classroom monitors through HDMI. Tested pretrained model on various objects like hands, water bottles and cans.
- Read through and attempted Google Colab tutorial for road sign detection, however it was noted that it would take too much time to train the model on the spot so the team will continue this in the following session.
- downloaded filezilla to assist in downloading road sign files and for future file transfers.

### Next Steps

- Complete the Road sign detector, boot model onto coral and attempt it on the stop sign
- Calibrate grayscale sensor
- Calibrate camera
- Visit the Quackston map in person to get an idea of the actual competition.

### Reflection
There are many tools and pograms that are downloaded onto the picar with its setup, it is important that all members familiarize themselves with all tools provided as
these scripts can greatly assist in debugging. An example of this was the list_tpus.py script that shows whether a coral tpu is connected or not, this could have helped 
in figuring out the core issue. There are also other scripts in the car which provide useful code that the team can repurpose and modify to fit the needs of the project.


---

## Entry – Declan

**Time:** 14:30-16:30  
**Activity Type:** Software Writing
**Status:** In Progress
**Estimated Effort:** 3 h

### Work Performed
- Used Nodebook ++ to extend the current graph document to write more nodes and increase graph resolution for the map of Quackston. 
- Map needs to be of high enough density that the robot can navigate to all points without crossing any road boundaries, which will require substantially more nodes than those provided by default to all teams. 


### Reflection
Overall, work on the graph is going well and improvements are being made. I need to continue to add graph nodes as well start to work on navigation algorithms and integrating the provided navigation Github resources from the other project repository the course administrators have given us access to. Work is going steadily, ideally I plan to have a fully fleshed out graph completed before end of reading week, as well as preliminary navigation algorithms and some integration with the wifi module for determining current position.

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 3.0 h | ⚠️ | Developed precise servo and speed control test scripts; evaluated environmental impacts on traction. |
| Ishaan Grewal | 2.0 h | ✅/⚠️ | Debugged Coral TPU issue (✅), set up FileZilla (✅), tested SunFounder object detection (✅), started Colab sign detection tutorial (⚠️)  |
| Nolan Su-Hackett | 2.0 h | ✅/⚠️ | Debugged Coral TPU issue (✅), set up FileZilla (✅), tested SunFounder object detection (✅), started Colab sign detection tutorial (⚠️)  |
| Declan Smith | 2 h | ⚠️ | Continue to Improve and Extend Map Graph|

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: 2026-02-01
