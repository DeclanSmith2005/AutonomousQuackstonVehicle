---
title: "Team Contributions - 4th Weekly Work Session"
date: 2026-01-29
week: 4
hours: 10
tags: Perception, Control, Infrastructure, Planning
contributors: Ishaan Grewal, Nolan Su-Hackett, Rafael Costa, Declan Smith
---

## Daily Summary

This session took place at the Quackston model track, providing the first opportunity for site-specific calibration and hardware testing. The Perception Team (Ishaan & Nolan) and Rafael (Control) focused on model training via Google Colab and color detection on the track. Rafael performed motor characterization tests to establish velocity benchmarks with Ishaan and collaborated with Nolan to implement a secure remote access solution via Tailscale. Declan (Planning) continued the digitization and node mapping of the Quackston environment.

---

## Entry – Rafael Costa

**Time:** 3:30-6:00
**Activity Type:** Software Development / Testing 
**Status:** In progress  
**Estimated Effort:** 2.5 h  

### Work Performed

- Refined and deployed motor characterization code to determine the relationship between PWM duty cycle and physical velocity.

- Conducted controlled speed trials across ten PWM increments (10% to 100%) over a fixed distance on the Quackston track.

- Collaborated with Ishaan and Nolan to calibrate the steering servo center-point and the optimal vertical tilt angle for the pan-tilt camera system.

- Successfully configured and tested Tailscale in collaboration with Nolan, enabling secure peer-to-peer networking and remote SSH access to the Raspberry Pi.

- Verified camera functionality on-track using a real-time color detection script to assess environmental lighting and track contrast.

### Decisions

- Servo Calibration: Established the exact PWM values for "Dead Center" steering to prevent lateral drift during CRUISE states.

- Camera Positioning: Fixed the camera tilt angle at a level that balances long-range sign detection with short-range lane marker tracking.

- Remote Access: Selected Tailscale as the primary VPN solution to bypass local network restrictions and facilitate remote debugging outside of lab hours.

### Issues Encountered

- Data Processing Backlog: While the speed test trials were completed successfully, the formal statistical analysis and motor curve plotting remain outstanding for the next session.

- Traction Variability: Observed slight differences in motor responses, likely due to the uneveness at some parts of the model track surface.

### Next Steps

- [ ] Complete the data analysis of the PWM-to-Velocity trials to finalize the FSM speed constants.

- [ ] Implement the Tailscale configuration across all team laptops to ensure universal remote access.

- [ ] Begin integrating the color detection logic into the preliminary line-following script.

### Reflection

Testing on the actual Quackston track was invaluable for grounding our theoretical models. The successful setup of Tailscale is a significant win; it allows us to move away from being tethered to the car in the lab, enabling a more flexible development workflow. My focus now shifts from "how the car moves" to "how fast it moves," ensuring that our planned arrival times at nodes are mathematically sound based on today's speed data.

---

## Entry – Ishaan Grewal

**Time:** 3:30-6:00  
**Activity Type:** Testing / Prototyping / Perception  
**Status:** In Progress  
**Estimated Effort:** 2.5 h  

### Work Performed

- Followed and completed the following steps of the European Road Sign Detector tutorial on Colab:
    - Set up the virtual environment.
    - Uploaded dataset to runtime.
    - Train the model.
    - Testing the model.
    - Compiling the TFLite Model for Edge TPU.
    - Download the Models
- Reviewed the Python files used in Colab to familiarize myself with the code.
- Working with Rafael, conducted controlled speed trials across ten PWM increments (10% to 100%) over a fixed distance on the Quackston track.
- Collaborated with Rafael and Nolan to calibrate the steering servo center-point and the optimal vertical tilt angle for the camera.
- Tested and verified camera functionality on the track at the calibrated vertical tilt angle using the SunFounder 7. Computer_Vision.py file.
- Experimented with the built-in colour detection and measured its effectiveness in detecting the center blue line.


### Decisions
- **Lane Detection Object Height Filter:** Based on preliminary results observed when tracking the blue center lane, the Perception team decided to include a filter in the Object Detection Pipeline which filters any blue detections that are above the horizon level of the camera. This was decided since we noticed that the camera was detecting background objects of the same colour. Hence, during competition, it may detect certain colours or objects on the buildings or in the background of the environment. By filtering to only consider objects at or below the camera's horizon, we can limit false detections.
- **Camera Positioning:** Fixed the camera tilt angle at a level that balances long-range sign detection with short-range lane marker tracking. Also decided that during operation, we will not adjust the vertical tilt, since this needs to remain constant (also because the focal lengths that would be obtained from calibration are specific to this angle).
- **Servo Calibration:** Established the exact PWM values for "Dead Center" steering to prevent lateral drift during CRUISE states. These are now the new "zero" values.


### Issues Encountered

- **Deploying the Model on the RPi:** When attempting to complete the last step of the European Road Sign Detector tutorial, which is deploying the model to the Raspberry Pi, the Perception team encountered errors. Specifically, we noticed that the tutorial did not specify what to input for certain variables, such as "headless." As a result, we were unable to test the trained sign detection model on the PiCar.
- **Traction Variability:** When assisting Rafael with conducting the controlled speed tests and calibrating the steering servo center-point, we noticed that there will always be some variability in traction, which sometimes causes lateral drift or variable speed. This is due to the wheels slipping and uneven surfaces on the track. The PID loop will help address/counter any impacts from this.
- **Grayscale Sensor Calibration:** The team intended to calibrate the grayscale sensor during this work session, however, we were not given black electrical tape, so we were unable to do this.


### Next Steps

- [ ] Work with Professor Paulo or TA Eric to help resolve the issue with deploying the trained model on the RPi. Once this is resolved, we need to test the model on the Pi by testing its ability to detect the stop signs.
- [ ] Obtain black electrical tape and calibrate the grayscale sensor. Work with Rafael to experiment with this sensor and see what the outputs look like for the road surface, blue line, and white/yellow lane boundaries. Also, finalize with Rafael how he wants this information transmitted to control.
- [ ] Calibrate the camera module to obtain the focal lengths and intrinsic parameters.
- [ ] Implement Tailscale.


### Reflection
Visiting the Quackston setup and seeing the map in person was immensely valuable in understanding key constraints and requirements. The Perception team is on track with their project roadmap. Although we were unable to test the model, going through the rest of the Colab tutorial steps and reading the provided Python scripts helped clarify the next steps for the Perception team, providing a great example framework to follow. I did notice that teams are not informed of which section of the track will be available on each Tuesday and Thursday, and I have mentioned this to a TA. I believe it is valuable for teams to know this because, for example, today there were no crosswalks on the map, and so if a team wants to test a specific part of the map, it would be helpful to know which submap will be out for testing on which day. Once the sensors and cameras are calibrated, we can begin collecting and annotating the data!


---

## Entry – [Nolan Su-Hackett]

**Time:** 3:30-6:00  
**Activity Type:** Testing / Prototyping / Perception  
**Status:** In Progress  
**Estimated Effort:** 2.5 h  

### Work Performed
- Went to in-person Quackston Display in Bain
- Downloaded Tailscale and added the Raspberry pi to list of devices, I can now connect to the Rpi without connecting to the same local Wi-Fi
- Ran Calibration script with Rafael for servo camera tilt and the wheel servo angle. Successfully calibrated wheels so that when zero'd the car drives straight
- Used Sunfounder Video streaming script to create a feedback loop to find the optimal camera angle with the car on the actual road with a placed stop sign
- tested video streaming script to create bounding boxes to detect certain colors, maybe this can be used as a means to do lane detection, as guidelines are blue strips?
- after Ishaan finished training the road sign model from google colab we attempted it but ran into some issues.

### Issues Encountered
- if there is dirt on the ground or dried salt, the wheels will pick it up and lose traction causing the wheels to slip
- after following the steps in the google colab tutorial the model could not run, it said the parameters did not match those that are needed from the script.
- no tape to calibrate grayscale sensor

### Next Steps

- Get black tape to calibrate grayscale sensor
- calibrate grayscale sensor
- Fix model loading issues with professor or TA

### Reflection
It is important to do as much testing and calibration on-site with the Quackston map as possible, as those will be the real conditions of the competition.
It was very valuable to do calibration for the camera tilt there as we could observe from the cameras POV what sign's and ducks on the road would look like, allowing the team to calibrate the servo tilt with an iterative process. Also being in-person with the map allowed the perception team to test different scripts that were downloaded
on setup to see which can be repurposed for some applications like experimenting with the colour deteciton script on the real road. 


---

## Entry – Declan

**Time:** 3:30-6  
**Activity Type:** writing code  
**Status:** In progress
**Estimated Effort:** 5 h  

### Work Performed

- Continued work on developing the virtual graph for the map of Quackston. 
- A first pass of the map is now fully functional, the graph of nodes provided to all teams is now visible using pyPlot.


### Next Steps

- Increasing Graph Resolution.
- Writing Dijkstra's algorithm to navigate the graph.
- Adding additional information to graph nodes, such as stop sign locations, maximum speeds, etc

### References
- https://matplotlib.org/3.5.3/api/_as_gen/matplotlib.pyplot.html

### Reflection

Overall, this was a productive week of work. I expect the development of an informative graph to be the most difficult aspect of my section of the project, so having a solid first draft of at least the points provided to all teams means we are well on our way to accomplishing end goals. A major next step will be integrating the provided navigation Github file structure into my implementation and using the tools provided to go about navigating / route planning. Overall it's going well and the team is on pace for a successful project. 

---

## Team Metrics

| Member | Hours | Status | Key Contribution |
|--------|-------|--------|------------------|
| Rafael Costa | 2.5 h | ⚠️ | Completed on-track speed trials (10%-100% PWM); successfully implemented Tailscale for remote access. |
| Ishaan Grewal | 2.5 h | ✅/⚠️ | Almost complete Google Colab tutorial on European road sign detection (⚠️), completed on-track speed trials (✅), tested camera functionality and colour detection algorithms (✅) |
| Nolan Su-Hackett | 2.5 h | ✅/⚠️ | Almost complete Google Colab tutorial on European road sign detection (⚠️), completed on-track speed trials (✅), tested camera functionality and colour detection algorithms (✅) |
| Declan Smith | 2.5 h | ✅/⚠️ | First Draft of Map Graph Done (✅) | Need to Continue to Extend the Graph and Add Nodes / Functionality. |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

**Entry completed**: 2026-02-01
