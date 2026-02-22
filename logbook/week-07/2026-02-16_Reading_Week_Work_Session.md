---
title: "Reading Week - Control Refactor, Calibration Pipeline, and Hardware Bridge Integration"
date: 2026-02-16
week: 7
hours: 8.0
tags: [Control, Calibration, Integration, State-Machine, Testing]
contributors: [Rafael Costa]
---

# Reading Week Work Session Log

## Objectives

- Improve robustness of line-following by adding calibration-aware signal processing and safer recovery behavior.
- Refactor the control stack for cleaner architecture and better mission-level behavior at intersections and stop lines.
- Decouple high-level control logic from direct motor/sensor access by introducing a networked hardware bridge.

## Detailed Work Log

### Session 1: Control Logic and Calibration Refactor (2026-02-16, 16:12 - 16:25)

**Members Present**: Rafael Costa

**Description**: 
Refactored the line-following pipeline around better calibration handling and mission control. Added dynamic calibration routines and moved to normalized signal interpretation so thresholds are consistent across sensors. Expanded the control state-machine workflow and improved turn handling from timed-only behavior toward line re-acquisition logic.

**Materials/Tools Used**:
- `control/line_sensor.py`
- `control/main.py`, `control/pid_controller.py`

**Process/Steps**:
1. Added calibration capture and threshold auto-configuration logic in the sensor pipeline.
2. Introduced mission queue/state transitions (`STRAIGHT`, `LEFT_1`, `LEFT_2`, `RIGHT`, `APPROACH_STOP`, `IDLE`) in the main controller.
3. Added smooth speed ramping, line-loss fail-safe timing, and closed-loop turn re-acquisition.

### Session 2: Tuning and Reliability Cleanup (2026-02-21, 15:58 - 16:10)

**Members Present**: Rafael Costa

**Description**:
Refined timing constants for turning/recovery and improved readability of tuning comments and PID documentation to reduce ambiguity during future test sessions. This session focused on stabilization and maintainability rather than new features.

### Session 3: Hardware Bridge Integration (2026-02-22, 11:17 - 12:25)

**Description**:
Implemented and integrated `server/hardware_bridge.py` using ZeroMQ to separate high-level control from direct hardware access. Migrated `control/main.py` to publish motor commands and subscribe to sensor data (`SENSORS`, `CALIBRATION` messages), added startup calibration request/response flow, and updated turn/intersection logic to operate over message passing.

### Session 4: Final Cleanup and Synchronization (2026-02-22, 16:55 - 17:05)

**Members Present**: Rafael Costa

**Description**:
Performed final cleanup and repository synchronization (minor comment clarity updates, workspace/config updates, merge synchronization) to keep branch state aligned before next testing cycle.

## Results & Data

### Measurements/Observations

| Parameter | Expected | Measured | Pass/Fail | Notes |
|-----------|----------|----------|-----------|-------|
| Control architecture | Monolithic script to modular flow | `LineSensor`, `PIDController`, mission-driven `main` | Pass | Improved readability and separation of concerns |
| Calibration pipeline | Static thresholds | Runtime calibration + normalized signal gates | Pass | Reduced dependence on hard-coded ADC assumptions |
| Turn recovery | Blind turn only | Blind + scan + opposite-direction fallback + IDLE fail-safe | Pass | Better safety behavior when line is not reacquired |
| Hardware integration | Direct `Picarx` control in main loop | ZeroMQ bridge (`PUB/SUB`, `PUSH/PULL`) with calibration handshake | Pass | Enables clearer control/perception/hardware boundaries |
| Robustness behavior | Unhandled transient faults | Sensor exception handling + line-loss timeout + stop fallback | Pass | Fewer uncontrolled states |

### Code Snippets

```python
def send_motor_command(push_socket, speed, steer):
	msg = {
		"type": "motor",
		"speed": speed,
		"steer": steer,
	}
	push_socket.send_json(msg)

def request_initial_calibration(push_socket, sub_socket, eyes):
	push_socket.send_json({"type": "calibrate"})
	msg = sub_socket.recv_json()
	if msg.get("topic") == "CALIBRATION" and msg.get("status") == "ok":
		eyes.apply_calibration(msg["cal_min"], msg["cal_max"])
```

### Calculations

Speed command shaping during PID tracking:

$$
v_{cmd} = \max\left(v_{base} - k\cdot |\theta|,\ v_{min}\right)
$$

where $k$ is the steering-to-speed drop gain and $\theta$ is steering output from PID.

## Challenges & Solutions

### Challenge 1: Turn completion without reliable line re-acquisition

**Problem**:
Timed turns alone were not robust across variable track conditions; the robot could miss line reacquisition and drift.

**Debugging Steps**:
1. Added active scan after blind turn using center-sensor signal checks.
2. Added opposite-direction fallback scan when first scan timed out.
3. Added safe failure state (`IDLE`) if reacquisition still failed.

**Solution**:
Implemented a two-stage turn recovery sequence with timeout-based fallbacks and explicit fail-safe transition.

**Lessons Learned**:
Intersection behavior needs event-driven logic and safety boundaries; open-loop timing alone is insufficient.

### Challenge 2: Coupling between control logic and hardware I/O

**Problem**:
Direct motor/sensor calls inside control code made integration and debugging harder.

**Debugging Steps**:
1. Introduced a bridge process to own hardware access.
2. Defined clear message contracts for sensor, motor, and calibration flows.
3. Updated control loop to consume sensor packets and emit command packets only.

**Solution**:
Integrated a ZeroMQ-based `hardware_bridge` and migrated control behavior to networked command/sensor messaging.

**Lessons Learned**:
A clean interface boundary significantly improves maintainability and testability for multi-component robotics systems.

## Next Steps

- [ ] Run repeated track trials to tune `TURN_BLIND_TIME`, `TURN_SCAN_TIMEOUT`, and steering limits.
- [ ] Add logging for bridge-side command latency and dropped-message diagnostics.
- [ ] Validate end-to-end behavior with Perception outputs feeding Control decisions.

## References

- `control/main.py`
- `control/line_sensor.py`
- `control/pid_controller.py`
- `server/hardware_bridge.py`
- Commits: `378cbb1`, `876e9ed`, `356a52d`, `7f40826`, `fbf1fc1`

## Personal Notes

This was a meaningful systems-level week. The biggest improvement was not only tuning values, but reshaping the architecture so calibration, mission behavior, and hardware communication are explicit and modular. For the next cycle, I should prioritize empirical tuning with repeatable test scripts and objective metrics rather than ad-hoc adjustments.

---

**Entry completed**: 2026-02-22 17:25