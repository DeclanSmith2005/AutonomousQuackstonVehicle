import time
import sys
import threading
import matplotlib.pyplot as plt
from picarx import Picarx

# Global flag for stopping the loop
stop_flag = False

def key_listener():
    """Listen for 's' key press to stop the loop."""
    global stop_flag
    while not stop_flag:
        user_input = input()
        if user_input.lower() == 's':
            stop_flag = True
            print("\nStopping...")
            break

def line_position_error(values):
    # values: [left, center, right]
    total = sum(values) + 1e-6
    weights = [-1.0, 0.0, 1.0]
    position = sum(w * v for w, v in zip(weights, values)) / total
    return position

def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def pid_controller(setpoint, pv, kp, ki, kd, previous_error, integral, dt):
    error = setpoint - pv
    integral += error * dt
    derivative = (error - previous_error) / dt
    control = kp * error + ki * integral + kd * derivative
    return control, error, integral

def main():
    setpoint = 0.0  # Desired distance to center line
    pv = 0  # Initial process variable

    px = Picarx()

    kp = 40.0  # Proportional gain
    ki = 0.0  # Integral gain
    kd = 10.0  # Derivative gain
    
    previous_error = 0.0
    integral = 0.0
    dt = 0.05  # Time step

    time_steps = []
    pv_values = []
    control_values = []
    speed_values = []
    steering_values = []

    start = time.time()

    base_speed = 50
    min_speed = 10

    # Start keyboard listener thread
    global stop_flag
    stop_flag = False
    listener_thread = threading.Thread(target=key_listener, daemon=True)
    listener_thread.start()
    print("PID controller running. Press 's' + Enter to stop.")

    while not stop_flag:
        greyscale_values = px.get_grayscale_data()
        pv = line_position_error(greyscale_values)

        control, error, integral = pid_controller(setpoint, pv, kp, ki, kd, 
                                                  previous_error, integral, dt)

        previous_error = error

        steering = clamp(control, -30, 30)
        speed = clamp(base_speed - abs(error) * 50, min_speed, base_speed)

        px.set_dir_servo_angle(steering)
        px.forward(speed)

        # log
        time_steps.append(time.time() - start)
        pv_values.append(pv)
        control_values.append(control)
        speed_values.append(speed)
        steering_values.append(steering)

        time.sleep(dt)
    
    px.stop()

    plt.figure(figsize=(12, 8))

    plt.subplot(3, 1, 1)
    plt.plot(time_steps, pv_values, label='PV (position)')
    plt.axhline(setpoint, color='k', linestyle='--', label='Setpoint')
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(time_steps, control_values, label='Control')
    plt.plot(time_steps, steering_values, label='Steering')
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(time_steps, speed_values, label='Speed')
    plt.legend()

    plt.tight_layout()
    plt.savefig(f'pid_plot_{int(time.time())}.png', dpi=150)
    print(f"Plot saved to pid_plot_{int(time.time())}.png")

if __name__ == "__main__":
    main()