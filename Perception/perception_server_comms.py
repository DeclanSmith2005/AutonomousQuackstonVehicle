import zmq
import time

_global_context = zmq.Context()

# Initialize persistent socket once at module load
class _VehicleStateManager:
    """Manages persistent ZMQ connection for low-latency vehicle state updates."""
    
    def __init__(self):
        self.sub_socket = _global_context.socket(zmq.SUB)
        # If running on the same Pi, use 127.0.0.1. 
        # If running on a laptop, use the Pi's IP.
        self.sub_socket.connect("tcp://127.0.0.1:5555")
        self.sub_socket.subscribe("")  # Subscribe to all topics
        self.current_state = None
        self.no_line = None
        self.stopped = None
    
    def update(self):
        """Process all pending messages and update state (non-blocking)."""
        try:
            while True:
                try:
                    msg = self.sub_socket.recv_json(flags=zmq.NOBLOCK)
                    if msg.get("topic") == "MISSION_STATE":
                        self.current_state = msg.get("state")
                        self.no_line = msg.get("no_line")
                        self.stopped = msg.get("stopped")
                except zmq.Again:
                    # No more messages available
                    break
        except Exception as e:
            print(f"Error receiving state: {e}")
    
    def get_state_data(self):
        """Return the current vehicle state data."""
        return self.current_state, self.no_line, self.stopped

class _CTESender:
    """Manages persistent ZMQ connection for sending CTE (Cross-Track Error) and distance data."""
    
    def __init__(self):
        self.pub_socket = _global_context.socket(zmq.PUB)
        # If running on the same Pi, use 127.0.0.1.
        # If running on a laptop, use the Pi's IP.
        self.pub_socket.connect("tcp://127.0.0.1:5556")
        # Small delay to ensure connection is established before sending
        time.sleep(0.1)
    
    def send_cte(self, cte_meters, distance_meters):
        """Send CTE and lookahead distance data to the server (non-blocking).
        
        Parameters
        ----------
        cte_meters : list of float
            Cross-Track Error values in meters at each lookahead point.
        distance_meters : list of float
            Lookahead distances in meters (how far ahead each CTE is measured).
        """
        try:
            # Convert to CSV string to ensure JSON serializability
            cte_str = ','.join(str(x) for x in cte_meters)
            distance_str = ','.join(str(x) for x in distance_meters)
            msg = {
                "topic": "TRAJECTORY",
                "cte": cte_str,
                "distance": distance_str,  # Distance from car in meters (was "y_ref")
                "timestamp_cte": time.time()
            }
            print(f"Sending: cte=[{cte_str[:30]}...], dist=[{distance_str[:30]}...]")
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"Error sending CTE AND distance: {e}")

class _DistanceToLineSender:
    """Manages persistent ZMQ connection for sending distance to horizontal line data."""

    def __init__(self):
        self.pub_socket = _global_context.socket(zmq.PUB)
        # If running on the same Pi, use 127.0.0.1. 
        # If running on a laptop, use the Pi's IP.
        self.pub_socket.connect("tcp://127.0.0.1:5556")
        # Small delay to ensure connection is established before sending
        time.sleep(0.1)
    
    def send_distance_to_line(self, distance_to_line):
        """Send distance to horizontal line to the server (non-blocking).
        
        Parameters
        ----------
        distance_to_line : float
            Distance in meters from the car to the detected horizontal line.
        """
        try:
            msg = {
                "topic": "TRAJECTORY",
                "distance_to_line": distance_to_line,
                "timestamp_distance_to_line": time.time()
            }
            print(f"Sending distance to line: {distance_to_line:.3f} m")
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"Error sending distance to line: {e}")

class _DuckSender:
    """Manages persistent ZMQ connection for sending duck object detections."""
    def __init__(self):
        self.pub_socket = _global_context.socket(zmq.PUB)
        # If running on the same Pi, use 127.0.0.1. 
        # If running on a laptop, use the Pi's IP.
        self.pub_socket.connect("tcp://127.0.0.1:5556")
        # Small delay to ensure connection is established before sending
        time.sleep(0.1)
    
    def send_duck_detection(self, distance, horizontal_distance):
        """Send duck detection data to the server (non-blocking).
        
        Parameters
        ----------
        distance : float
            Distance in meters from the car to the detected duck.
        horizontal_distance : float
            Horizontal distance in meters from the center of the vehicle to the detected duck.
        """
        try:
            msg = {
                "topic": "DUCK",
                "distance": distance,
                "horizontal_distance": horizontal_distance,
                "timestamp_DUCK": time.time()
            }
            # print(f"Sending duck detection: distance={distance:.3f} m, horizontal_distance={horizontal_distance:.3f} m")
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"Error sending duck detection: {e}")

class _ObjectSender: 
    def __init__(self):
        self.pub_socket = _global_context.socket(zmq.PUB)
        # If running on the same Pi, use 127.0.0.1. 
        # If running on a laptop, use the Pi's IP.
        self.pub_socket.connect("tcp://127.0.0.1:5556")
        # Small delay to ensure connection is established before sending
        time.sleep(0.1)
    
    # send detection to corresponding server topic based on label
    def send_object_detection(self, label, distance):
        """Send generic object detection data to the server based on label (non-blocking).
        
        Parameters
        ----------
        label : str
            The label of the detected object
        distance : float
            Distance in meters from the car to the detected object.
        """
        try:
            topic = label.upper() # Ex: "STOP", "DNE", "ONEWAY", "YIELD"
            msg = {
                "topic": topic, 
                "distance": distance,
                f"timestamp_{topic}": time.time() # Ex: "timestamp_STOP", "timestamp_DNE", etc.
            }
            print(f"Sending object detection: {label} at distance={distance:.3f} m")
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"Error sending object detection: {e}")

_state_manager = _VehicleStateManager()
_cte_sender = _CTESender()
_distance_to_line_sender = _DistanceToLineSender()
_duck_sender = _DuckSender()
_object_sender = _ObjectSender()

def get_vehicle_state():
    """Return the current vehicle state from the MISSION_STATE topic.
    
    This function uses a persistent socket initialized once at module load,
    so it can be called frame-by-frame with zero latency and no TCP overhead.
    """
    _state_manager.update()
    current_state, no_line, stopped = _state_manager.get_state_data()
    return current_state, no_line, stopped

def send_cte_yref_to_server(cte_meters, y_ref):
    """Send the CTE in meters and y_ref to the server.
    
    Uses a persistent socket initialized once at module load for zero latency
    and efficient frame-by-frame sending.
    
    Parameters
    ----------
    cte_meters : float
        Cross-Track Error in meters
    y_ref : float
        Reference y-coordinate
    """
    _cte_sender.send_cte(cte_meters, y_ref)

def send_distance_to_line_to_server(distance_to_line):
    """Send the distance to the horizontal line to the server.
    
    Uses a persistent socket initialized once at module load for zero latency
    and efficient frame-by-frame sending.
    
    Parameters
    ----------
    distance_to_line : float
        Distance in meters from the car to the detected horizontal line.
    """
    _distance_to_line_sender.send_distance_to_line(distance_to_line)

def send_duck_detection_to_server(distance, horizontal_distance):
    """Send duck detection data to the server.
    
    Uses a persistent socket initialized once at module load for zero latency
    and efficient frame-by-frame sending.
    
    Parameters
    ----------
    distance : float
        Distance in meters from the car to the detected duck.
    horizontal_distance : float
        Horizontal distance in meters from the center of the vehicle to the detected duck.
    """
    _duck_sender.send_duck_detection(distance, horizontal_distance)

def send_object_detection_to_server(label, distance):
    """Send generic object detection data to the server based on label.
    
    Uses a persistent socket initialized once at module load for zero latency
    and efficient frame-by-frame sending.
    
    Parameters
    ----------
    label : str
        The label of the detected object
    distance : float
        Distance in meters from the car to the detected object.
    """
    _object_sender.send_object_detection(label, distance)