import time
import math
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
        for key in ("visible", "detected", "is_visible", "present"):
            if key in msg:
                parsed = _parse_bool(msg.get(key))
                if parsed is not None:
                    return parsed
        label = msg.get("label") or msg.get("class") or msg.get("name")
        if _is_duck_label(label):
            return True

    if topic in {"OBJECT", "OBJECTS", "DETECTION", "DETECTIONS", "OBJECT_DETECTION"}:
        objects = msg.get("objects") or msg.get("detections")
        if isinstance(objects, list):
            duck_seen = False
            for obj in objects:
                if not isinstance(obj, dict):
                    continue
                label = obj.get("label") or obj.get("class") or obj.get("name")
                if _is_duck_label(label):
                    duck_seen = True
                    for key in ("visible", "detected", "is_visible", "present"):
                        if key in obj:
                            parsed = _parse_bool(obj.get(key))
                            if parsed is not None:
                                if parsed:
                                    return True
                                break
                    else:
                        return True
            return duck_seen

        label = msg.get("label") or msg.get("class") or msg.get("name")
        if _is_duck_label(label):
            for key in ("visible", "detected", "is_visible", "present"):
                if key in msg:
                    parsed = _parse_bool(msg.get(key))
                    if parsed is not None:
                        return parsed
            return True

    return None


def _validate_distance_cm(value):
    """Return a sane distance in cm or None for invalid/outlier data."""
    try:
        distance_cm = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(distance_cm):
        return None
    if not (config.DISTANCE_MIN_CM <= distance_cm <= config.DISTANCE_MAX_CM):
        return None
    return distance_cm


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
        
        # Camera CTE state
        self.camera_cte = None
        self.camera_cte_timestamp = 0
        self.camera_cte_timeout = 0.5  # CTE valid for 500ms
        
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
                "no_line": no_line,
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
    
    def _process_incoming_messages(self):
        """Process all pending messages from camera system."""
        try:
            while True:
                try:
                    msg = self.sub_socket.recv_json(flags=zmq.NOBLOCK)
                    topic = msg.get("topic")
                    
                    if topic == "CTE":
                        self.camera_cte = msg.get("cte")
                        self.camera_cte_timestamp = time.time()
                    
                    elif topic == "TRAJECTORY":
                        # Parse comma-separated strings into lists of floats
                        cte_list = _parse_csv_floats(msg.get("cte"))
                        distance_list = _parse_csv_floats(msg.get("distance"))
                        distance_line = _validate_distance_cm(msg.get("distance_to_line"))
                        if distance_line is not None:
                            self.intersection_distance_cm = distance_line
                            self.intersection_distance_timestamp = time.time()
                        if cte_list is not None and distance_list is not None:
                            self.trajectory_cte = cte_list  # list of CTE values in meters
                            self.trajectory_distance = distance_list  # list of lookahead distances in meters
                            self.trajectory_timestamp = time.time()  # Use local receive time for freshness check

                    duck_visible = _extract_duck_visible(msg)
                    if duck_visible is not None:
                        self.duck_visible = duck_visible
                        self.duck_visible_timestamp = time.time()
                        
                except zmq.Again:
                    # No more messages
                    break
        except Exception as e:
            print(f"[ZMQ] Error receiving: {e}")
    
    def receive_camera_cte(self):
        """Non-blocking receive of CTE from camera system. Returns CTE or None."""
        self._process_incoming_messages()
        
        # Return CTE only if it's fresh
        if self.camera_cte is not None:
            if (time.time() - self.camera_cte_timestamp) < self.camera_cte_timeout:
                return self.camera_cte
        return None

    def receive_intersection_distance(self):
        """Non-blocking receive of distance to intersection from camera system.
        
        Returns
        -------
        float or None
            Distance to intersection in cm.
        """
        self._process_incoming_messages()
        
        if self.intersection_distance_cm is not None:
            if (time.time() - self.intersection_distance_timestamp) < self.intersection_distance_timeout:
                return self.intersection_distance_cm
        return None
    
    def receive_trajectory(self):
        """Non-blocking receive of trajectory data.

        Returns
        -------
        dict or None
            {'cte': list[float], 'distance': list[float]} in meters when fresh, None otherwise.
            Each list contains values parsed from comma-separated strings.
            - cte: Cross-Track Error at each lookahead point (meters)
            - distance: Lookahead distance from car (meters)
        """
        self._process_incoming_messages()
        
        # Return trajectory only if it's fresh
        if self.trajectory_cte is not None:
            if (time.time() - self.trajectory_timestamp) < self.trajectory_timeout:
                return {'cte': self.trajectory_cte, 'distance': self.trajectory_distance}
        return None

    def receive_duck_visible(self):
        """Return whether a duck is currently visible from perception."""
        self._process_incoming_messages()

        # If perception stops publishing duck state entirely, expire to False.
        if (time.time() - self.duck_visible_timestamp) > self.duck_visible_timeout:
            return False
        return bool(self.duck_visible)
    
    def close(self):
        """Clean up ZMQ resources."""
        self.pub_socket.close()
        self.sub_socket.close()
        self.context.term()
        print("[ZMQ] Sockets closed")