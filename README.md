# ELEC 392 - Autonomous Robotic Taxi

A repository for code used in Smith Engineering ELEC 392 design course. This project uses a **Sunfounder PiCar-X** and **Coral USB Accelerator** to develop a robotic taxi capable of operating autonomously in a miniature town populated with rubber duckies (Quackston).

## Features

- **Logbook**: Implements a logbook structure for your team to record progress in accordance to ELEC 392 specifications
- **Utilities**: Provides some basic utilities and to get you started with calibration of your PiCar-X
- **Setup Scripts**: Bash scripts to help you install dependencies and repos needed to use the PiCar-X and Coral USB Accelerator
- **Sample Code**: Ready-to-use examples demonstrating all key features

## Project Structure

```
elec392_project/
├── examples/                                      # Sample code and demonstrations
│   ├── 01_move.py                                 # Basic vehicle control example
│   ├── 02_keyboard_control.py                     # Keyboard vehicle control example
│   ├── 03_sound.py                                # Robot Hat sound examples (use sudo)
│   ├── 04_ultrasonic_obstacle_avoidance.py        # Obstacle avoidance example using ultrasonic sensor
│   ├── 05_line_following.py                       # Line following demonstration
│   └── 06_receive_detections_udp.py               # Receive object detections via UDP from remote detector
├── images/                                        # Folder for project images referenced by logbook
├── logbook/                                       # Folder for log entries 
│   ├── .templates
│   │   └── daily-entry-template.md                # Log entry template
│   ├── week-01/                                   
│   │   └── 2025-01-08_example-circuit-design.md   # Example log entry
│   ├── ...                                        
│   ├── week-12/
│   ├── generate_activity_report.py                # Auto-grader for logbook entries                                  
│   └── README.md                                  # Logbook instructions
├── images/                                        # Sound files (.mp3, .wav)
├── src/                                           # Where your code should go
├── utils/                                         # Autonomous driving utilities
│   ├── __init__.py
│   ├── actuator_calibration.py                    # Motor and servo calibration
│   ├── grayscale_calibration.py                   # Grayscale (line follower) sensor calibration
│   └── servo_zeroing.py                           # Script to zero servos
├── README.md                                      # This file
├── setup_coral.sh                                 # Bash script to install coral repos 
├── setup_picarx.sh                                # Bash script to isntall picar-x repos and dependencies
└── requirements.txt                               # Python dependencies
```

## Hardware Requirements

- Sunfounder PiCar-X robot car
- Raspberry Pi 4B
- Coral USB Accelerator
- Camera module (Pi Camera or compatible)
- Ultrasonic distance sensor
- Line tracking (grayscale) sensors

## Software Requirements

- Python 3.9+
- Raspberry Pi OS (Bookworm)
- See `requirements.txt` for Python dependencies

## Installation
1. Accept the GitHub Classroom assignment to create your personal repository copy

1. Create a development folder:
   ```bash
   cd ~
   mkdir dev
   cd dev
   ```

1. Clone your repository to your Raspberry Pi:
   ```bash
   git clone <your-classroom-repository-url>
   cd elec392_project
   ```

1. Install PiCar-X repos
   ```bash
   bash setup_picarx.sh 
   ```

1. Install Coral repos
   ```bash
   bash setup_coral.sh 
   ```

## Usage

### Running Example Scripts

All example scripts are located in the `examples/` directory. Run them from the repository root:

#### 1. Basic Movement (`01_move.py`)
Tests all motors and servos: forward motion, steering, and camera pan/tilt.

```bash
python examples/01_move.py
```

**What it does:**
- Drives forward briefly
- Sweeps steering servo left and right
- Tests camera pan and tilt servos

#### 2. Keyboard Control (`02_keyboard_control.py`)
Drive the PiCar-X manually using keyboard input.

```bash
python examples/02_keyboard_control.py
```

**Controls:**
- `w` - Forward
- `s` - Backward  
- `a` - Turn left
- `d` - Turn right
- `i/k` - Camera tilt up/down
- `j/l` - Camera pan left/right
- `Ctrl+C` - Exit (press twice)

#### 3. Sound Effects (`03_sound.py`)
Play sound effects and text-to-speech (requires sudo for audio).

```bash
sudo python examples/03_sound.py
```

**Controls:**
- `space` - Play car horn sound
- `c` - Play sound in background thread
- `t` - Text-to-speech greeting
- `q` - Play/stop background music

#### 4. Ultrasonic Obstacle Avoidance (`04_ultrasonic_obstacle_avoidance.py`)
Autonomous obstacle avoidance using the ultrasonic distance sensor.

```bash
python examples/04_ultrasonic_obstacle_avoidance.py
```

**Behavior:**
- Distance > 40cm: Drive straight
- Distance 20-40cm: Turn to avoid
- Distance < 20cm: Reverse and turn

#### 5. Line Following (`05_line_following.py`)
Follow a dark line on a light background using grayscale sensors.

```bash
python examples/05_line_following.py
```

**Note:** Requires grayscale sensor calibration first:
```bash
python utils/grayscale_calibration.py
```

#### 6. UDP Detection Receiver (`06_receive_detections_udp.py`)
Receive object detection data from a remote detector via UDP and control the vehicle based on detections.

```bash
python examples/06_receive_detections_udp.py
```

**What it does:**
- Listens for object detection data over UDP from a remote detector (e.g., Coral TPU inference on another device)
- Displays detection updates to the console
- Controls the steering servo based on whether objects are detected
- Acts as a fail-safe by stopping the car if no detections are received

**Requirements:**
- A remote detector sending detection data in UDP format (see `utils/detection_receiver.py` for protocol details)
- Network connectivity between the Raspberry Pi and the detector

### Calibration Utilities

Before using certain features, calibrate the sensors:

```bash
# Zero all servos to neutral position
python utils/servo_zeroing.py

# Calibrate motor speeds for straight driving
python utils/actuator_calibration.py

# Calibrate grayscale sensors for line following
python utils/grayscale_calibration.py
```

### Logbook Activity Report

Generate an activity report for your logbook entries:

```bash
python logbook/generate_activity_report.py . --output my-report.md
```

### Student Code (src/)

Teams should place all project-specific Python code in the `src/` folder. Keep modules organized by feature and use clear names. A minimal structure example:

```
src/
├── __init__.py
├── controllers/
│   ├── __init__.py
│   └── lane_follower.py
└── sensors/
   ├── __init__.py
   └── ultrasonic.py
```

Import your code from example scripts or your own runners like this:

```python
# in examples/my_demo.py
from src.controllers.lane_follower import LaneFollower
from src.sensors.ultrasonic import UltrasonicSensor

lf = LaneFollower()
sensor = UltrasonicSensor()
```

Guidelines:
- Group related code into subpackages (e.g., `controllers/`, `sensors/`, `planning/`).
- Avoid placing team code in `examples/`; keep `examples/` for runnable demos.
- Write small, testable modules; prefer functions/classes over monolithic scripts.
- Add `__init__.py` in subfolders so imports work reliably.

## Contributing

This is a course project repository. Contributions should follow the course guidelines and be coordinated with the instructor.

## License

See LICENSE file for details.

## Course Information

**Course**: ELEC 392 - Engineering Design and Development
**Institution**: Smith Engineering, Queen's University
**Offering**: Winter 2026 
