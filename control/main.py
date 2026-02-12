import csv
import os
import time
import threading
from picarx import Picarx
from pid_controller import PIDController
from line_sensor import LineSensor

# --- CONFIG (mirrors pid.py) ---
OFFSETS = [111, 95, 100]
KP, KI, KD = 0.40, 0.0, 0.05
MAX_STEER = 35
POLARITY = -1
LOOP_INTERVAL = 0.01
ERROR_BUFFER_LEN = 5

stop_flag = False
bias_mode = "c"


def key_listener():
    global stop_flag, bias_mode
    while not stop_flag:
        cmd = input().strip().lower()
        if cmd == "s":
            stop_flag = True
        elif cmd in ("l", "r", "c"):
            bias_mode = cmd
            print(f"Mode set to: {bias_mode}")


def main():
    global stop_flag, bias_mode

    px = Picarx()
    pid = PIDController(KP, KI, KD, min_out=-MAX_STEER, max_out=MAX_STEER)
    eyes = LineSensor(px, OFFSETS)

    error_buffer = [0.0] * ERROR_BUFFER_LEN
    history = []
    start_time = time.time()

    threading.Thread(target=key_listener, daemon=True).start()

    try:
        while not stop_flag:
            loop_start = time.time()

            raw = eyes.get_raw()
            error, stop_detected, base_speed = eyes.compute_error(raw, bias_mode)

            if stop_detected:
                print("STOP LINE DETECTED")
                px.stop()
                time.sleep(2.0)

                print("Clearing line...")
                px.forward(base_speed)
                time.sleep(0.5)
                continue

            error_buffer.pop(0)
            error_buffer.append(error)
            smooth_error = sum(error_buffer) / len(error_buffer)

            now = time.time()
            steering = pid.update(smooth_error * POLARITY, dt=1.0)
            if steering > 30:
                steering = 30
            if steering < -30:
                steering = -30

            speed_drop = abs(steering) * 0.4
            current_speed = max(base_speed - speed_drop, 5)

            px.set_dir_servo_angle(steering)
            px.forward(current_speed)

            history.append((now - start_time, smooth_error, steering, current_speed))

            elapsed = time.time() - loop_start
            wait_time = LOOP_INTERVAL - elapsed
            if wait_time > 0:
                time.sleep(wait_time)

    finally:
        px.stop()

        if history:
            os.makedirs("logs", exist_ok=True)
            log_name = f"logs/pid_log_{time.strftime('%Y%m%d_%H%M%S')}.csv"
            try:
                with open(log_name, "w", newline="") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["time_s", "error", "steering_angle", "speed"])
                    writer.writerows(history)
                print(f"Wrote log to {log_name}")
            except OSError as exc:
                print(f"Failed to write log: {exc}")


if __name__ == "__main__":
    main()