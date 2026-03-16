# control/mission_manager.py
import threading

class RobotState:
    STRAIGHT = "ST"
    APPROACH_STOP = "STOP"
    LEFT_1 = "L1"
    LEFT_2 = "L2"
    RIGHT = "R"
    ROUNDABOUT_ENTRY = "RB_ENTRY"
    ROUNDABOUT_CIRCULATE = "RB_CIRC"
    ROUNDABOUT_EXIT_PREP = "RB_EXIT_PREP"
    ROUNDABOUT_EXIT_COMMIT = "RB_EXIT_COMMIT"
    CALIBRATE = "CAL"
    IDLE = "IDLE"

class MissionManager:
    def __init__(self, original_mission):
        self.original_mission = list(original_mission)
        self.mission_queue = list(original_mission)
        self.current_state = RobotState.IDLE
        self.crossings_seen = 0
        self.mission_step_requested = threading.Event()
        
        # Preload first stage if mission not empty
        self.advance_mission()

    def advance_mission(self):
        """Advance to next mission state from the queue."""
        if len(self.mission_queue) > 0:
            self.current_state = self.mission_queue.pop(0)
            print(f"MISSION UPDATE: Switched to {self.current_state}")
        else:
            print("MISSION COMPLETE")
            self.current_state = RobotState.IDLE
        
        self.crossings_seen = 0

    def reset_mission(self):
        """Restore the original mission queue and preload first stage."""
        self.mission_queue = list(self.original_mission)
        self.current_state = RobotState.IDLE
        self.crossings_seen = 0
        self.advance_mission()
        print(f"Mission reset. Remaining queued stages: {self.mission_queue}")

    def request_step(self):
        self.mission_step_requested.set()

    def check_step_requested(self):
        if self.mission_step_requested.is_set():
            self.mission_step_requested.clear()
            self.advance_mission()
            return True
        return False
