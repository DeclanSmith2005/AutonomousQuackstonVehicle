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
| Ishaan Grewal | 2.0 h | ✅/⚠️ | Debugged Coral TPU issue (✅), set up FileZilla (✅), tested SunFounder object detection (✅), started Colab sign detection tutorial (⚠️)  |
| Name 3 | X.X h | ✅/⚠️/❌ | Brief description |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: YYYY-MM-DD HH:MM
