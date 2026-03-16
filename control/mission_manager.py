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
    """
    Manages the robot's high-level mission state and sequential execution of stages.
    """
    def __init__(self, original_mission):
        """
        Initialize the MissionManager with a sequence of states.

        Parameters
        ----------
        original_mission : list of str
            A list of state constants from RobotState (e.g., [ST, L1, RB_ENTRY, ST]).
        """
        self.original_mission = list(original_mission)
        self.mission_queue = list(original_mission)
        self.current_state = RobotState.IDLE
        self.crossings_seen = 0
        self.mission_step_requested = threading.Event()
        
        # Preload first stage if mission not empty
        self.advance_mission()

    def advance_mission(self):
        """
        Pop the next state from the mission queue and update the current state.
        Resets 'crossings_seen' for the new stage.
        """
        if len(self.mission_queue) > 0:
            self.current_state = self.mission_queue.pop(0)
            print(f"MISSION UPDATE: Switched to {self.current_state}")
        else:
            print("MISSION COMPLETE")
            self.current_state = RobotState.IDLE
        
        self.crossings_seen = 0

    def reset_mission(self):
        """
        Restore the original mission queue and restart from the first stage.
        """
        self.mission_queue = list(self.original_mission)
        self.current_state = RobotState.IDLE
        self.crossings_seen = 0
        self.advance_mission()
        print(f"Mission reset. Remaining queued stages: {self.mission_queue}")

    def request_step(self):
        """
        Signal that the current mission stage is complete and the robot should advance.
        Used by the key listener or other external triggers.
        """
        self.mission_step_requested.set()

    def check_step_requested(self):
        """
        Non-blocking check to see if a mission advance was requested.
        Clears the event if it was set.

        Returns
        -------
        bool
            True if advancement was requested and handled.
        """
        if self.mission_step_requested.is_set():
            self.mission_step_requested.clear()
            self.advance_mission()
            return True
        return False
