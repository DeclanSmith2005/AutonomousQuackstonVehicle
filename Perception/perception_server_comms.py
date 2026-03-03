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
    
    def update(self):
        """Process all pending messages and update state (non-blocking)."""
        try:
            while True:
                try:
                    msg = self.sub_socket.recv_json(flags=zmq.NOBLOCK)
                    if msg.get("topic") == "MISSION_STATE":
                        self.current_state = msg.get("state")
                except zmq.Again:
                    # No more messages available
                    break
        except Exception as e:
            print(f"Error receiving state: {e}")
    
    def get_state(self):
        """Return the current vehicle state."""
        return self.current_state

class _CTESender:
    """Manages persistent ZMQ connection for sending CTE (Cross-Track Error) data."""
    
    def __init__(self):
        self.pub_socket = _global_context.socket(zmq.PUB)
        # If running on the same Pi, use 127.0.0.1. 
        # If running on a laptop, use the Pi's IP.
        self.pub_socket.connect("tcp://127.0.0.1:5556")
        # Small delay to ensure connection is established before sending
        time.sleep(0.1)
    
    def send_cte(self, cte_meters):
        """Send CTE data to the server (non-blocking)."""
        try:
            msg = {
                "topic": "CTE",
                "cte": cte_meters
            }
            self.pub_socket.send_json(msg)
        except Exception as e:
            print(f"Error sending CTE: {e}")

_state_manager = _VehicleStateManager()
_cte_sender = _CTESender()

def get_vehicle_state():
    """Return the current vehicle state from the MISSION_STATE topic.
    
    This function uses a persistent socket initialized once at module load,
    so it can be called frame-by-frame with zero latency and no TCP overhead.
    """
    _state_manager.update()
    return _state_manager.get_state()

def send_cte_to_server(cte_meters):
    """Send the CTE in meters to the server.
    
    Uses a persistent socket initialized once at module load for zero latency
    and efficient frame-by-frame sending.
    
    Parameters
    ----------
    cte_meters : float
        Cross-Track Error in meters
    """
    _cte_sender.send_cte(cte_meters)
