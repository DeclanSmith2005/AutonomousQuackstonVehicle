import time
import zmq
import config

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
        self.trajectory = None
        self.trajectory_timestamp = 0
        self.trajectory_timeout = 0.3  # Trajectory valid for 300ms
        
        # Give sockets time to bind
        time.sleep(0.1)
        print(f"[ZMQ] Publishing on port {pub_port}, Subscribing on port {sub_port}")
    
    def publish_mission_state(self, state, mission_queue):
        """Publish current mission state to subscribers."""
        try:
            msg = {
                "topic": "MISSION_STATE",
                "state": state.name if hasattr(state, 'name') else str(state),
                "queue": [s.name if hasattr(s, 'name') else str(s) for s in mission_queue]
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
                        self.trajectory = msg.get("points")
                        self.trajectory_timestamp = time.time()
                        
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
    
    def receive_trajectory(self):
        """Non-blocking receive of trajectory points. Returns list of (dist_cm, cte_cm) or None."""
        self._process_incoming_messages()
        
        # Return trajectory only if it's fresh
        if self.trajectory is not None:
            if (time.time() - self.trajectory_timestamp) < self.trajectory_timeout:
                return self.trajectory
        return None
    
    def close(self):
        """Clean up ZMQ resources."""
        self.pub_socket.close()
        self.sub_socket.close()
        self.context.term()
        print("[ZMQ] Sockets closed")
