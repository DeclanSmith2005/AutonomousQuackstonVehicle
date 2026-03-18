---
title: "Project Proposal Meeting"
date: 2026-01-18
week: 2
hours: 10.0
tags: [meeting]
contributors: [Rafael Costa, Ishaan Grewal, Nolan Su-Hackett, Declan, Smith]
---

## Meeting Information

**Date:** 2026-01-18  
**Time:** 14:00 – 16:30  
**Duration:** 2.5 hours  
**Location:** In-person
**Meeting Type:** Team Sync / Design Review / Sprint Planning / Status Update / Proposal Planning

### Attendees

- ✅ Rafael
- ✅ Nolan
- ✅ Ishaan
- ✅ Declan

---

## 📋 Agenda

1. Check Inventory & Hardware Testing
2. System Design Overview: Perception, Localization, Planning, and Control
3. Fail-Safe & Safety Mechanisms
4. Proposal Report Task Delegation
6. Determine Weekly Meeting Schedule

---

## 📝 Discussion Summary

### 1. Hardware Inventory & Initial Testing

**Context:** Verification of kit components and basic functionality before designing the system architecture.
**Key Points Discussed:**

- Confirmed ultrasonic sensors are functional after testing.
- Raspberry Pi connected successfully to establish a baseline for software integration.
- Need for additional hardware: 2 ultrasonics (for reversing/passenger detection), an emergency stop button, and 5 extra LEDs for signals/indicators.
**Decisions Made:**

- Purchase or acquire extra sensors and LEDs using the $50 project budget.
- Use Google Colab for CV training, acknowledging a possible monthly cost ($13.99 - $50) for compute units.
---

### 2. System Architecture

**Context:** Defining how the vehicle will perceive its environment and make pathing decisions.


**Key Points Discussed:**

- **Perception:** Camera-based lane detection is the primary. Use OpenCV and potentially Yolo for object detection (ducks/cars)
- **Localization:** Utilize GPS coordinates (updated every 0.2–1s) and QR codes at nodes to confirm position.
- **Path Planning:** Implement a node-based graph system using Dijkstra’s or A* algorithms to calculate the shortest path to fares.
- **Control:** Implement PID loops for lane following. Speed will be dynamic—lowered for turns to improve PID stability and increased on straightaways


**Decisions Made:**

- Adopt a node-based map where nodes have properties like "Max Speed" or "Risk Factor" (e.g., near schools) to influence pathing.
- Use a "black box" approach for interfacing: Planning sends X,Y coordinates, and Control handles the movement.
---

### 3. Safety & Fail-Safes

**Context:** Ensuring the vehicle can recover from errors or off-track scenarios. 


**Key Points Discussed:**

- **Recovery:** If the vehicle goes off-track, it will store the last 1–2 seconds of inputs and reverse the actions to return to the last known node.
- **Obstacle Detection:** Use ultrasonic sensors as a fail-safe to prevent collisions with ducks or other vehicles while reversing.

## ✅ Decisions & Outcomes

### Technical Decisions

| Decision            | Rationale                                   | Impact                          | Alternatives Considered |
|---------------------|----------------------------------------------|----------------------------------|--------------------------|
| Node-Based Map      | Simplifies pathfinding and speed zones       | Simplifies global navigation     | Pure GPS navigation      |
| Dijkstra / A*       | Guaranteed shortest path for fares           | Minimizes travel time            | Fixed routing            |
| PID Speed Control   | Better handling during turns                 | Increases reliability            | Constant speed           |
| Fail-Safe Reverse   | Simple recovery from off-track               | Prevents total mission failure   | Manual reset             |

---
### Project Decisions

| Decision            | Rationale                                   | Impact                         |
|---------------------|----------------------------------------------|--------------------------------|
| Weekly Meetings     | Lab time isn't enough for deep work          | Ensures consistent progress    |
| Git Version Control | Standardizes code management across 4 people | Prevents code conflicts        |
| Colab for Training  | Local machines may be too slow for CV        | Uses budget for compute time   |
---
## 📦 Action Items & Next Steps

### Immediate Actions (This Week)

- ### Immediate Actions (By Friday, Jan 23)

- [ ] **Declan** - Draft the Executive Summary, Write Section 1: Proponent Background and Understanding of the Problem, Design the Pathing, Fare Selection, and Broad Decision-Making logic for Section 3.
- [ ] **Ishaan** - Write the Section 2 Technical Approach description, Develop the Lane Detection details for Section 3, Create the Project Management Plan, including the WBS, Gantt chart, and CPM (Section 4), Define Team Roles, Responsibilities, and Project Scheduling (Sections 4.1 & 4.2).
- [ ] **Rafael** - Develop the Control system details for Section 3, Draft Section 6: Cost Proposal and Budget, Write Section 8: Deliverables and Anticipated Outcomes, Prepare Appendix B: Team Operating Agreement.
- [ ] **Nolan** - Create the High-Level Overview Visio for Section 2, Draft the Perception Overview for Section 3, Write Section 5: Decision-Making and Conflict Resolution, Write Section 7: Risk, Safety, and Ethical Considerations.
- [ ]  **Team** - Collaborate on "Micro-Task Gating" for the Project Management section (e.g., sequencing training before testing).

### Upcoming Actions (Next Week+)

- [ ] **Team** - Review first full draft of the proposal on Sunday night. - **Due:** YYYY-MM-DD
- [ ] **Nolan** - Begin researching/gathering datasets for sign and duck detection. - **Due:** YYYY-MM-DD
- [ ] **Rafael** - Test base PID parameters on the car during Tuesday's lab.
- [ ] **Ishaan** - Research image processing/object detection algorithms/strategies. Set up necessary libraries for Coral and attempt to get Yolo working. Run test code. 
---

## 📊 Project Status

### Overall Progress

- **On Track**

### Milestones

| Milestone                  | Target Date | Status        | Notes                     |
|----------------------------|-------------|---------------|---------------------------|
| Inventory & Pi Setup       | 2026-01-18  | ✅ Complete   | Basic testing done        |
| Proposal First Draft       | 2026-01-23  | ⚠️ In Progress | Internal Friday deadline  |
| Final Proposal Submission  | 2026-01-25  | ⏳ Upcoming   | Due Sunday night          |

---

## 🎯 Next Meeting

**Date:** 2026-01-20 (Tuesday Lab) / 2026-01-22 (Full Team) 
**Time:** 14:30 (Thursday) 
**Location:** On-campus

**Proposed Agenda:**

1.  Review proposal draft progress.
2.  Research on specific areas.
3.  Git learning session.

---

## 📎 Attachments & References

N/A

## 💬 Additional Notes

N/A

---

**Minutes prepared by:** Rafael Costa
**Date submitted:** 2026-01-18
**Reviewed by:** Ishaan Grewal
