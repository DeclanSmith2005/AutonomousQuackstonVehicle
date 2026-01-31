---
title: "Team Contributions - 4th Weekly Work Session"
date: 2026-01-29
week: 4
hours: X.X
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
| Rafael Costa | 2.5 h | ⚠️ | Completed on-track speed trials (10%-100% PWM); successfully implemented Tailscale for remote access. |
| Name 2 | X.X h | ✅/⚠️/❌ | Brief description |
| Name 3 | X.X h | ✅/⚠️/❌ | Brief description |

**Legend:** ✅ Completed | ⚠️ In Progress/Blocked | ❌ Issues

---

## Team Notes

Any collective observations, cross-functional issues, or team-level decisions that span multiple individual contributions.

---

**Entry completed**: YYYY-MM-DD HH:MM
