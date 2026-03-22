import time
import zmq
import config


def _parse_bool(value):
    """Best-effort conversion of common boolean encodings."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "y", "on", "visible"}:
            return True
        if lowered in {"0", "false", "no", "n", "off", "hidden", "not_visible"}:
            return False
    return None


def _is_duck_label(value):
    """Return True when a label/class/name value refers to a duck."""
    if value is None:
        return False
    return str(value).strip().lower() == "duck"


def _extract_duck_visible(msg):
    """Extract duck visibility from a perception message.

    Returns True/False when duck visibility can be determined, else None.
    """
    if not isinstance(msg, dict):
        return None

    topic = str(msg.get("topic", "")).strip().upper()

    if topic == "DUCK":
        # Perception currently publishes DUCK packets only on active detections,
        # typically with distance fields but no explicit visibility boolean.
        if any(key in msg for key in ("distance", "horizontal_distance", "timestamp_duck")):
            return True

    return None

def _parse_csv_floats(value):
    """Parse a comma-separated string into a list of floats.
    
    Parameters
    ----------
    value : str
        Comma-separated float values, e.g. "0.1,0.2,0.3"
    
    Returns
    -------
    list of float or None
        Parsed list, or None if parsing fails.
    """
    if value is None:
        return None
    try:
        if isinstance(value, str):
            return [float(x.strip()) for x in value.split(',') if x.strip()]
        elif isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        else:
            return [float(value)]
    except (TypeError, ValueError) as e:
        print(f"[ZMQ] Error parsing CSV floats: {e}")
        return None


class ServerManager:
    """Manages ZMQ sockets for mission state publishing and CTE/trajectory reception."""
    
    def __init__(self, pub_port=config.SENSOR_PORT, sub_port=config.MOTOR_PORT):
        self.context = zmq.Context()
        
        # PUB Socket: Sends mission state and telemetry to hardware_bridge (Port 5555)
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(f"tcp://*:{pub_port}")
        
        # SUB Socket: Receives CTE/trajectory from camera system (Port 5556)
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.bind(f"tcp://*:{sub_port}")
        self.sub_socket.subscribe("")  # Subscribe to all topics
        
        # SUB Socket: Receives mission queue from pathing (Port 5557)
        self.pathing_socket = self.context.socket(zmq.SUB)
        self.pathing_socket.connect("tcp://127.0.0.1:5557")
        self.pathing_socket.subscribe("")

        # PUB Socket: Sends DUCK_READY state to pathing (Port 5558)
        self.duck_ready_socket = self.context.socket(zmq.PUB)
        self.duck_ready_socket.connect("tcp://127.0.0.1:5558")

        self.last_pathing_timestamp = 0.0
        self.latest_mission_queue = None
        self.latest_dist_to_next_node = 0.0
        self.new_mission_available = False
        self.pathing_stop = False
        
        # Trajectory state for turns
        self.trajectory_cte = None  # CTE in meters from perception
        self.trajectory_distance = None  # Lookahead distance in meters from perception
        self.trajectory_timestamp = 0
        self.trajectory_timeout = config.TRAJECTORY_TIMEOUT

        # Distance-to-intersection state (can arrive with TRAJECTORY or DISTANCE topics)
        self.intersection_distance_cm = None
        self.intersection_distance_timestamp = 0
        self.intersection_distance_timeout = config.INTERSECTION_DISTANCE_TIMEOUT

        # Duck visibility state from perception
        self.duck_visible = False
        self.duck_visible_timestamp = 0
        self.duck_visible_timeout = 0.75

        # Localization state (x, y in meters; heading in degrees)
        self.localization_data = None
        self.localization_timestamp = 0
        self.localization_timeout = config.LOCALIZATION_TIMEOUT
        
        # Give sockets time to bind
        time.sleep(0.1)
        print(f"[ZMQ] Publishing on port {pub_port}, Subscribing on port {sub_port}")
    
    def publish_mission_state(self, state, mission_queue, no_line, stopped):
        """Publish current mission state to subscribers."""
        try:
            msg = {
                "topic": "MISSION_STATE",
                "state": state.name if hasattr(state, 'name') else str(state),
                "queue": [s.name if hasattr(s, 'name') else str(s) for s in mission_queue],
                "no_line": bool(no_line),
                "no_line_turn": bool(no_line),
                "stopped": stopped
            }
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"[ZMQ] Error publishing state: {e}")
    
    def publish_telemetry(self, speed, error, steering):
        """Publish telemetry data to subscribers."""
        try:
            msg = {
                "topic": "TELEMETRY",
                "speed": speed,
                "error": error,
                "steering": steering,
                "timestamp": time.time()
            }
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"[ZMQ] Error publishing telemetry: {e}")
    
    def process_incoming_messages(self):
        """Process all pending messages from camera system.
        
        This method parses incoming ZMQ messages and updates the internal state for:
        - TRAJECTORY: lists of CTE and lookahead distances.
        - DISTANCE_TO_LINE: distance to the next intersection (cm).
        - LOCALIZATION: (x, y) coordinates and heading.
        - DUCK: visibility of obstacles.
        """
        try:
            while True:
                try:
                    msg = self.sub_socket.recv_json(flags=zmq.NOBLOCK)
                    topic = msg.get("topic")
                    
                    if topic == "TRAJECTORY":
                        # Parse comma-separated strings into lists of floats
                        cte_list = _parse_csv_floats(msg.get("cte"))
                        distance_list = _parse_csv_floats(msg.get("distance"))
                        if cte_list is not None and distance_list is not None:
                            self.trajectory_cte = cte_list  # list of CTE values in meters
                            self.trajectory_distance = distance_list  # list of lookahead distances in meters
                            self.trajectory_timestamp = time.time()  # Use local receive time for freshness check

                        # Perception may stream "NONE" until a stop line is visible, then send meters.
                        if "distance_to_line" in msg:
                            self._handle_intersection_distance(msg.get("distance_to_line"))

                    elif topic in ("DISTANCE_TO_LINE", "DISTANCE"):
                        val = msg.get("distance_to_line", msg.get("distance"))
                        self._handle_intersection_distance(val)

                    duck_visible = _extract_duck_visible(msg)
                    if duck_visible is not None:
                        self.duck_visible = duck_visible
                        self.duck_visible_timestamp = time.time()
                        
                except zmq.Again:
                    # No more messages
                    break
        except Exception as e:
            print(f"[ZMQ] Error receiving: {e}")

        # Process messages from Pathing
        try:
            while True:
                try:
                    msg = self.pathing_socket.recv_json(flags=zmq.NOBLOCK)
                    topic = msg.get("topic")
                    if topic == "DIRECTIONS":
                        msg_time = msg.get("time", 0.0)
                        if msg_time > self.last_pathing_timestamp:
                            self.last_pathing_timestamp = msg_time
                            self.latest_mission_queue = msg.get("dirs", [])
                            self.latest_dist_to_next_node = msg.get("distToNextNode", 0.0)
                            self.new_mission_available = True
                    elif topic == "STOP":
                        self.pathing_stop = msg.get("stopTheCar", False)
                except zmq.Again:
                    break
        except Exception as e:
            print(f"[ZMQ] Error receiving from pathing: {e}")

    def _handle_intersection_distance(self, value):
        """Internal helper to update intersection distance from various message formats."""
        if isinstance(value, str) and value.strip().upper() == "NONE":
            self.intersection_distance_cm = None
            self.intersection_distance_timestamp = time.time()
        else:
            try:
                # Convert meters from perception to centimeters for control logic
                self.intersection_distance_cm = float(value) * 100.0
                self.intersection_distance_timestamp = time.time()
            except (TypeError, ValueError):
                pass
    
    def receive_intersection_distance(self):
        """Non-blocking receive of distance to intersection from camera system.
        
        Returns
        -------
        float or None
            Distance to intersection in cm.
        """
        if self.intersection_distance_cm is not None:
            if (time.time() - self.intersection_distance_timestamp) < self.intersection_distance_timeout:
                return self.intersection_distance_cm
        return None
    
    def receive_trajectory(self, max_age_s=None):
        """Non-blocking receive of trajectory data.

        Returns
        -------
        dict or None
            {'cte': list[float], 'distance': list[float]} in meters when fresh, None otherwise.
            Each list contains values parsed from comma-separated strings.
            - cte: Cross-Track Error at each lookahead point (meters)
            - distance: Lookahead distance from car (meters)
        """
        freshness_window = self.trajectory_timeout if max_age_s is None else float(max_age_s)
        freshness_window = max(0.0, freshness_window)

        # Return trajectory only if it's fresh
        if self.trajectory_cte is not None:
            if (time.time() - self.trajectory_timestamp) < freshness_window:
                return {'cte': self.trajectory_cte, 'distance': self.trajectory_distance}
        return None

    def receive_duck_visible(self):
        """Return whether a duck is currently visible from perception."""
        # If perception stops publishing duck state entirely, expire to False.
        if (time.time() - self.duck_visible_timestamp) > self.duck_visible_timeout:
            return False
        return bool(self.duck_visible)

    def receive_localization(self):
        """Return fresh localization data dict or None when stale/unavailable."""
        if self.localization_data is None:
            return None
        if (time.time() - self.localization_timestamp) > self.localization_timeout:
            return None
        return self.localization_data
    
    def receive_mission_queue(self):
        """Return the latest mission queue if a new one is available, else None."""
        if self.new_mission_available:
            self.new_mission_available = False
            return self.latest_mission_queue
        return None

    def receive_dist_to_next_node(self):
        """Return the latest distance to the next node sent by the pathing system."""
        return self.latest_dist_to_next_node

    def receive_stop_the_car(self):
        """Return the latest stopTheCar command from pathing."""
        return getattr(self, "pathing_stop", False)

    def publish_duck_ready(self, ready):
        """Publish DUCK_READY state to pathing."""
        try:
            msg = {
                "topic": "DUCK_READY",
                "ready": bool(ready),
                "time": time.time()
            }
            self.duck_ready_socket.send_json(msg)
        except Exception as e:
            print(f"[ZMQ] Error publishing DUCK_READY: {e}")

    def close(self):
        """Clean up ZMQ resources."""
        self.pub_socket.close()
        self.sub_socket.close()
        self.pathing_socket.close()
        self.duck_ready_socket.close()
        self.context.term()
        print("[ZMQ] Sockets closed")