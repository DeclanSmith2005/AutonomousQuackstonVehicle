from robot_hat import PWM
from gpiozero import LED, Button
import time
import threading

class IOComponents:
    def __init__(self):
        # Setup Blinkers
        self.p9 = PWM('P9')  # RIGHT BLINKER
        self.p8 = PWM('P8')  # LEFT BLINKER
        self.p8.freq(2)
        self.p9.freq(2)
        
        # Setup Brake Light
        self.brake_light = LED(17) # D0 -> GPIO17
        
        # Brake blink state (for signal_all)
        self._brake_blink_active = False
        self._brake_blink_thread = None
        
        # Setup Limit Switch
        self.limit_switch = Button(4, pull_up=True, bounce_time=0.05)
        self.limit_switch.when_pressed = self._on_limit_switch_pressed
        
        # State tracker for limit switch
        self.limit_switch_pressed_flag = False

    def _on_limit_switch_pressed(self):
        self.limit_switch_pressed_flag = True

    def clear_limit_switch_flag(self):
        self.limit_switch_pressed_flag = False

    def is_limit_switch_pressed(self):
        return self.limit_switch_pressed_flag

    # Turn Signal Controls
    def signal_left(self):
        self.p9.pulse_width_percent(0)
        self.p8.pulse_width_percent(50)

    def signal_right(self):
        self.p8.pulse_width_percent(0)
        self.p9.pulse_width_percent(50)

    def signal_hazard(self):
        self.p8.pulse_width_percent(50)
        self.p9.pulse_width_percent(50)

    def signal_off(self):
        self.p8.pulse_width_percent(0)
        self.p9.pulse_width_percent(0)

    # Brake Light Controls
    def brake_on(self):
        self.brake_light.on()

    def brake_off(self):
        self.brake_light.off()

    def update_brakes(self, speed):
        """Turn on brake lights if speed is close to 0."""
        if abs(speed) < 1.0: # Close to 0
            self.brake_on()
        else:
            self.brake_off()

    # All-lights blinking (for pickup/dropoff stops)
    def signal_all(self):
        """Blink both blinkers AND brake light together."""
        self.p8.pulse_width_percent(50)
        self.p9.pulse_width_percent(50)
        if not self._brake_blink_active:
            self._brake_blink_active = True
            self._brake_blink_thread = threading.Thread(
                target=self._brake_blink_loop, daemon=True
            )
            self._brake_blink_thread.start()

    def _brake_blink_loop(self):
        """Background thread: toggle brake LED at ~2 Hz to match blinkers."""
        while self._brake_blink_active:
            self.brake_light.on()
            time.sleep(0.25)
            if not self._brake_blink_active:
                break
            self.brake_light.off()
            time.sleep(0.25)

    def signal_all_off(self):
        """Stop all-lights blinking mode."""
        self._brake_blink_active = False
        self.signal_off()
        self.brake_off()
