---
title: "Team Contributions - Weekly Work Session #1"
date: 2026-02-24
week: 7
hours: 8.0
tags: [Perception, Control, Planning, Team Sync]
contributors: [Ishaan Grewal, Nolan Su-Hackett, Rafael Costa, Declan Smith]
---

## Daily Summary

As the first team work session following reading week, the beginning of the session served as a team sync, where each individual shared the progress they made on their tasks
over reading week with the rest of the team. Additionally, the team discussed overall subteam project status and future trajectory. The Perception team engaged in valuable discussions
with Professor Paulo Araujo about their lane detection and CTE implementation, gaining important insights and opinions which led to key decisions being made (as discussed below).
The Perception team also focused on testing the trained object detection model and the distance calculations.

---

## Entry – [Ishaan Grewal]

**Time:** 14:30-16:30  
**Activity Type:** Implementation, Testing, Brainstorming/Team Sync  
**Status:** Complete/In progress  
**Estimated Effort:** 2.0 h  

### Work Performed & Decisions Made:

- **Team Sync:** Shared Perception progress with the rest of the team, specifically regarding the lane detection and cross-track error (CTE) implementation that was
  worked on over reading break. During this team sync, I also took time to understand Rafael's server implementation and how Perception would interface with it.
- **Professor Feedback & Resulting Decisions Made:** At the beginning of the work session, I shared the lane detection and CTE work I had completed over reading week
  with Professor Paulo Araujo, seeking his insights and opinions on the questions I had outlined in the reading week entry. Key points discussed included how the Control
  PID loop would use the CTE alongside the current grayscale sensor implementation and best practices with image processing. The following decisions were made from
  this discussion with Professor Paulo: **(1)** The Control PID loop will use a weighted combination of the CTE and grayscale sensor readings to provide efficiency, reliability,
  and a fail-safe solution. Professor Paulo pointed out that the CTE will be far more valuable than the grayscale readings since it is obtained from image processing, and that we
  should rely more on that. Using this advice, we will weigh the CTE more than the grayscale readings. **(2)**  Professor Paulo pointed out that the grayscale sensor operates at
  a much higher frequency compared to the camera's frame rate, and consequently, recommended that, in between these delays in camera lane detection, we rely on the grayscale sensor.
  Upon discussion with the Control team (Rafael), we decided that this would be the best implementation option for us.  
- **Object Detection Model - Implementation & Testing:** In this work session, Nolan and I tested the object detection model we had trained over reading week to evaluate
  its effectiveness for each object class.
- **Object Detection Distance Calculations - Preliminary Testing:** Alongside testing the object detection accuracy, Nolan and I also evaluated the accuracy of the object distance
  calculations to see if the focal length obtained from camera calibration was accurate. In preliminary testing, we found that the distances have an excellent accuracy
  with an error of ± 1 cm.

### Issues Encountered

- **Vehicle Class Misdetections:** During the object detection model testing, we found that the trained model was identifying far background objects as a "Car", and that
  specifically, objects that were black and rectangular in shape were being falsely classified. We then looked back at the Vehicle class training data and identified a potential
  cause for these misdetections. When we annotated this data, we created one large bounding box around the lower back of the Picar, which was done to include both wheels
  in the box. However, since this included lots of noise and/or pixels that were random and not particularly a wheel, this was contributing to the various misdetections
  we were observing.
- **Potential Solutions:** To solve the Vehicle Class misdetections, Nolan and I have proposed reannotating the images with separate bounding boxes around each wheel,
  since this would ensure that the model is trained only on wheel pixels and minimize noise.

### Next Steps

- [ ] Reannotate the Vehicle object class and retrain the model.
- [ ] Implement and test the retrained model on the track.
- [ ] Brainstorm with Nolan how to handle different cases for lane detection and CTE calculation (straight, right, left, etc.)

### Reflection

This work session highlighted the immense value of seeking feedback and perspectives from professionals, such as Professor Paulo Araujo. By engaging in these discussions, 
not only was the Perception team able to validate that their current lane detection implementation is industry standard and that they were on the right track, but they were 
also able to gain profound insights and answers to the remaining questions they had. The conversation we had with Professor Paulo helped clarify points of confusion and ultimately
helped guide the team in the right direction with regard to its next steps. Hence, it is important to ask questions and seek the opinions of knowledgeable professionals. Additionally,
this session showcased the benefit of having team syncs after breaks like reading week. As a result of the team sync, everyone was able to share the work they completed over the break
and this ensured that everyone was on the same page and understood the project trajectory. Lastly, the issues the Perception team encountered with Vehicle class misdetections
illustrate how certain design decisions that may seem trivial when made (like using one bounding box for two wheels instead of two smaller boxes), can have a large impact on
the results obtained; that is, in this case, the efficiency of object detection models.

---

## Entry – Rafael Costa

**Time:** 14:30–16:30  
**Activity Type:** Implementation, Testing, Team Sync  
**Status:** Completed  
**Estimated Effort:** 2.0 h  

### Work Performed

- **Team Sync:** Shared Control subsystem progress with the team. Explained the server architecture and ZeroMQ-based communication between the hardware bridge and control logic, helping Perception understand how their CTE output would interface with the system.
- **Turn Execution Logic Overhaul:** Refactored `execute_turn()` in `main.py` to use a closed-loop approach—the robot now waits for a full-width line marker (all three grayscale sensors detecting the line) before committing to a turn, then scans until the line is reacquired. Added configurable timeouts (`TURN_ENTRY_TIMEOUT`, `TURN_STOP_HOLD_TIME`) and stop-at-marker behavior before turns.
- **Mission Queue Improvements:** Added `reset_mission_queue()` function and keyboard command (`reset`/`mr`) to restart the mission. Implemented manual mission step advancement via Enter key or `next` command, decoupling state progression from intersection detection.
- **Line Sensor Hysteresis:** Implemented hysteresis thresholds (`LINE_PRESENT_ON`/`LINE_PRESENT_OFF`) in `line_sensor.py` to prevent flickering line detection. Adjusted `RECOVERY_STEER` from 70 to 40 for smoother recovery behavior.
- **Hardware Bridge Enhancements:** Updated calibration parameters in `hardware_bridge.py` (increased turn angle, duration, sample interval). Added backward motion phase to wiggle calibration for more comprehensive min/max sampling. Added proper socket cleanup on exit.
- **PID Data Collection:** Ran multiple test sessions and collected 7 PID log files capturing steering angles, speeds, and error values for data-driven tuning analysis.

### Decisions

- Changed the turn execution model from time-based blind turns to sensor-gated turns, improving reliability at intersections.
- Increased `LOST_LINE_TIMEOUT` from 2.0s to 5.0s to reduce false failsafe triggers during maneuvers.
- Removed automatic `update_mission_state()` calls after turns/intersections; state now advances only via explicit keyboard input or mission logic.

### Issues Encountered

- Initial turn logic was unreliable—the robot would sometimes start turning before reaching the intersection marker, or miss the line entirely during recovery. Solved by gating turn entry on full-width line detection.
- Line detection flickered near threshold boundaries, causing erratic behavior. Addressed with hysteresis logic.

### Next Steps

- [ ] Integrate perception-derived CTE input once available from the Perception team.
- [ ] Analyze collected PID logs to identify optimal `KP`, `KD` values for different track sections.
- [ ] Validate the new turn logic on all intersection types (left, right, straight-through).

### Reflection

This session was productive for both implementation and team alignment. The discussion with Ishaan about how Perception's CTE would feed into Control helped clarify the interface requirements and reinforced the decision (from Professor Paulo's feedback) to use a weighted combination of CTE and grayscale readings. The refactored turn logic using sensor-gated execution is significantly more robust than the previous time-based approach, though it required careful threshold tuning. Collecting extensive log data during testing will enable data-driven PID tuning in future sessions rather than relying on subjective observations.

---

## Entry – [Nolan Su-Hackett]

**Time:** 14:30-16:30  
**Activity Type:** Implementation, Testing, Brainstorming/Team Sync  
**Status:** Complete/In progress  
**Estimated Effort:** 2.0 h 

### Work Performed

- Tested Object detection model on signs, tested what cases the model misclassifies things in.
- Following the testing of object detection, I rewrote some labels to ensure that Ishaan's labels for object distance matched that of the model, this allowed the team to test and validate the distance measurements. A conclusive error test has not been done on the distance measuremenets as of yet. However, with a real distance of 30 cm the distance calculation can vary in either direction by about 1 cm from what was observed.
- Spoke with Professor Paulo Araujo about some problems that were arising with our model and general perspective regarding CTE. A main problem was the overclassification of the car. The Professor said that it may be hard to detect cars, as each car is allowed their own design, this made the team think that car detection may not be crucial and that there may be another better solution.
- Team sync: Rafael suggested a server that each team will send information to, allowing communication between nodes. The server will accept input from each team, and the control loop decides what information to take and when, it then performs control functions based on relevant inputs.
- Retrained model with concatenated oneway class instead of leftway, rightway, and with reannotated car images.

### Decisions
- Reannotate and retrain the model with different bounding boxes which will only capture individual wheels of the car.
### Issues Encountered
- Car overclassification: the model is classifying people, darker backgrounds and objects in the distace as cars. This can be due to the annotation method, originally the bounding boxes were drawn around the wheels and the empty space between them so that each car would be identified as one box. After discussion we decided it might be better if each wheel was bounded individually, and although we might see one car as multiple cars as there are multiple wheels on a car, it is more important that the car class is correctly classified.

### Next Steps


- [ ] Test the new model and check distance calculations for each object
- [ ] discuss with Ishaan how to go about application of CTE, different test cases like turn right, left or stay straight.

### Reflection
This session highlights the importance of decisive bounding boxes in the annotation stage, and also the importance of consultation with those who are more experienced. The conversation with the professor allowed the team to verify the feasibility of our solution. This is important as it allows for checkpoints at which the team will know whether to pivot and cut losses or to continue its path. Consulting those who are more experienced, can also help hint towards unnecessary steps that the team may be taking, like the car detection for example which still needs to be investigated by the perception team.


---

## Entry – Declan Smith

**Time:** 14:30-16:30  
**Activity Type:** Project Management / Software Dev
**Status:** In progress  
**Estimated Effort:** 2.0h  

### Work Performed
- Spent most of the session conferring with other subsystem heads about the optimal way to structure master/slave dynamics between each subsystem and how to decide which files should call/make reference to each other.
- Especially between myself and Raphael, it feels like either piece of software could form the mainloop running on the actual car, so we discussed whether it would make more sense to have a web server running, making calls to other Python files as necessary, or if the server should be a supplemental part of systyem that provides consumer producer processes a convenient method of interaction. So far we have settled on having the latter, but we have agreed that we should try to comnplete development of subsystems before we decide the most efficient way to wire them together. 
- Remaining time was spent refining / trying to fix bugs with existing path-finding algorithms / supporting functions. For example, I realized that I accidentally had included an extra loop in my Dijkstra's implementation that was causing new nodes to be added in an incorrect order. 


### Next Steps
- Complete algorithms for fare selection and vfps so that I can direct more focus towards integrating the pathfinding logic with other team members' contributions. 


### Reflection
The team is well organized and continuing to make good progress towards  the final product. I am hopeful that we will be ready in the next 2 weeks and that we may perform well at the competition. 

---
## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Ishaan Grewal | 2.0 h | ✅/⚠️ | Team Sync & Professor Feedback (✅), Object Detection Model Implementation & Testing (⚠️), Object Detection Distance Testing(⚠️)  |
| Rafael Costa | 2.0 h | ✅ | Turn Logic Overhaul (✅), Mission Queue Improvements (✅), Line Sensor Hysteresis (✅), PID Data Collection (✅) |
| Nolan Su-Hackett | 2.0 h | ✅/⚠️ | Team Sync & Professor Feedback (✅), Object Detection Model Implementation & Testing (⚠️), Object Detection Distance Testing(⚠️)  |
| Declan Smith | 2.0 h | ✅/⚠️ | Team Sync (✅), Code Polishing (⚠️)  |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: 2026-03-03 04:26
