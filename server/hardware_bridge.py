import time
import zmq
import json
from picarx import Picarx

CAL_SAMPLE_INTERVAL = 0.01
CAL_TURN_ANGLE = 30
CAL_TURN_SPEED = 10
CAL_TURN_DURATION = 0.5
CAL_STOP_DURATION = 0.1


def collect_calibration_samples(px, cal_min, cal_max, duration_s):
    start = time.time()
    while (time.time() - start) < duration_s:
        sample = px.get_grayscale_data()
        for index in range(3):
            cal_min[index] = min(cal_min[index], sample[index])
            cal_max[index] = max(cal_max[index], sample[index])
        time.sleep(CAL_SAMPLE_INTERVAL)


def run_wiggle_calibration(px):
    cal_min = [4095, 4095, 4095]
    cal_max = [0, 0, 0]

    px.set_dir_servo_angle(CAL_TURN_ANGLE)
    px.forward(CAL_TURN_SPEED)
    collect_calibration_samples(px, cal_min, cal_max, CAL_TURN_DURATION)

    px.set_dir_servo_angle(-CAL_TURN_ANGLE)
    px.forward(CAL_TURN_SPEED)
    collect_calibration_samples(px, cal_min, cal_max, CAL_TURN_DURATION)

    px.stop()
    px.set_dir_servo_angle(0)
    time.sleep(CAL_STOP_DURATION)

    return cal_min, cal_max

def main():
    px = Picarx()
    context = zmq.Context()

    # PUB Socket: Sends Sensor Data (Port 5555)
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5555")
    pub_socket.setsockopt(zmq.CONFLATE, 1)  # Let late subscribers get latest sensor data

    # PULL Socket: Receives Motor Commands (Port 5556)
    pull_socket = context.socket(zmq.PULL)
    pull_socket.bind("tcp://*:5556")

    print("Hardware Bridge Running...")

    try:
        while True:
            # --- 1. PUBLISH SENSORS ---
            grayscale = px.get_grayscale_data()
            sensor_msg = {
                "topic": "SENSORS",
                "grayscale": grayscale,
                "timestamp": time.time()
            }
            pub_socket.send_json(sensor_msg)

            # --- 2. PROCESS COMMANDS ---
            try:
                # Non-blocking receive
                cmd_msg = pull_socket.recv_json(flags=zmq.NOBLOCK)

                cmd_type = cmd_msg.get("type")

                if cmd_type == "motor":
                    # {type: "motor", speed: 20, steer: -15}
                    if cmd_msg.get("speed") is not None:
                        px.forward(cmd_msg["speed"])
                    if cmd_msg.get("steer") is not None:
                        px.set_dir_servo_angle(cmd_msg["steer"])

                elif cmd_type == "stop":
                    px.stop()

                elif cmd_type == "calibrate":
                    print("Starting wiggle calibration...")
                    cal_min, cal_max = run_wiggle_calibration(px)
                    pub_socket.send_json(
                        {
                            "topic": "CALIBRATION",
                            "status": "ok",
                            "cal_min": cal_min,
                            "cal_max": cal_max,
                            "timestamp": time.time(),
                        }
                    )
                    print(f"Calibration complete. min={cal_min}, max={cal_max}")

            except zmq.Again:
                pass  # No new command, keep doing what we're doing

            time.sleep(0.01)  # 100Hz Loop

    finally:
        px.stop()


if __name__ == "__main__":
    main()