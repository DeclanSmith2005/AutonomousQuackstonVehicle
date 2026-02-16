import time


class LineSensor:
    def __init__(self, px, offsets):
        self.cal_max = 0
        self.cal_min = 0
        self.px = px
        self.offsets = offsets  # [L, M, R]

        # Signal gates and tuning
        self.WHITE_CUTOFF = 1000
        self.LINE_THRESHOLD = 700
        self.LOGIC_DETECT = 50
        self.NOISE_GATE = 50
        self.RECOVERY_STEER = 70
        self.BRANCH_BIAS = 20
        self.BASE_SPEED = 30

        # Steering weights for weighted average
        self.weights = [1, 0, -1]

        # Memory for recovery steering
        self.last_line_seen = False
        # -1 = line was left, 0 = center, 1 = right
        self.last_line_direction = 0

    def get_raw(self):
        return self.px.get_grayscale_data()

    def color_signal(self, raw, offset):
        if raw > self.WHITE_CUTOFF:
            return 0.0
        if raw < self.LINE_THRESHOLD:
            return 0.0
        return max(0.0, raw - offset)

    def _signals(self, raw_values):
        l_raw, m_raw, r_raw = raw_values
        return (
            self.color_signal(l_raw, self.offsets[0]),
            self.color_signal(m_raw, self.offsets[1]),
            self.color_signal(r_raw, self.offsets[2]),
        )

    def analyze_pattern(self, raw_values):
        s_l, s_m, s_r = self._signals(raw_values)
        
        if all(r > self.WHITE_CUTOFF for r in raw_values):
            return "STOP_WHITE"

        is_l = s_l > self.LOGIC_DETECT
        is_m = s_m > self.LOGIC_DETECT
        is_r = s_r > self.LOGIC_DETECT

        count = sum([is_l, is_m, is_r])
        if count == 3 or (count == 2 and is_m):
            return "CROSS_GREEN"
        if count > 0:
            return "LINE"
        return "NONE"

    def compute_error(self, raw_values, bias_mode="c"):
        """
        Converts grayscale readings into a steering error.

        Returns (error, stop_detected, base_speed).
        """
        s_l, s_m, s_r = self._signals(raw_values)

        stop_detected = s_l > self.LOGIC_DETECT and s_m > self.LOGIC_DETECT and s_r > self.LOGIC_DETECT
        base_speed = self.BASE_SPEED

        has_line = s_l > self.NOISE_GATE or s_m > self.NOISE_GATE or s_r > self.NOISE_GATE
        if not has_line:
            self.last_line_seen = False
            if self.last_line_direction < 0:
                return self.RECOVERY_STEER, stop_detected, base_speed
            if self.last_line_direction > 0:
                return -self.RECOVERY_STEER, stop_detected, base_speed
            return 0.0, stop_detected, base_speed

        total_signal = s_l + s_m + s_r
        if total_signal == 0:
            return 0.0, stop_detected, base_speed

        numerator = (s_l * self.weights[0]) + (s_r * self.weights[2])
        error = (numerator / total_signal) * 100.0

        self.last_line_seen = True
        if error > 20:
            self.last_line_direction = -1
        elif error < -20:
            self.last_line_direction = 1
        else:
            self.last_line_direction = 0

        has_left = s_l > self.LOGIC_DETECT
        has_mid = s_m > self.LOGIC_DETECT
        has_right = s_r > self.LOGIC_DETECT

        if bias_mode == "r" and has_mid and has_right:
            error -= self.BRANCH_BIAS
            base_speed = 10
        elif bias_mode == "l" and has_mid and has_left:
            error += self.BRANCH_BIAS
            base_speed = 10

        return error, stop_detected, base_speed

    def calibrate(self, straight_angle=0):
        print("--- WIGGLE CALIBRATION START ---")
        print("Robot will move! Clear the area.")
        time.sleep(1)

        # Initialize: Min = High Number, Max = Low Number
        # We want to find the LOWEST value (Black) and HIGHEST value (Green/White)
        self.cal_min = [4095, 4095, 4095]
        self.cal_max = [0, 0, 0]

        # Define the Wiggle Maneuver
        # (Steering Angle, Speed, Duration)
        maneuvers = [
            (straight_angle - 30, 10, 0.5),   # Turn Left Forward
            (straight_angle - 30, -10, 0.5),  # Turn Left Backward
            (straight_angle + 30, 10, 0.5),   # Turn Right Forward
            (straight_angle + 30, -10, 0.5),  # Turn Right Backward
            (straight_angle, 0, 0.1)           # Stop
        ]

        for angle, speed, duration in maneuvers:
            self.px.set_dir_servo_angle(angle)
            self.px.forward(speed)

            # Record data heavily during the maneuver
            maneuver_start = time.time()
            while (time.time() - maneuver_start) < duration:
                raw = self.get_raw()
                for i in range(3):
                    # Capture the "Blackest" black (Minimum value)
                    if raw[i] < self.cal_min[i]:
                        self.cal_min[i] = raw[i]

                    # Capture the "Whitest" white/green (Maximum value)
                    if raw[i] > self.cal_max[i]:
                        self.cal_max[i] = raw[i]
                time.sleep(0.01)  # High frequency sampling

        self.px.stop()

        # Apply the Calibration
        # Offset is the "Black" floor (Minimum read)
        self.offsets = self.cal_min

        # Calculate signal range (Max - Min)
        ranges = [self.cal_max[i] - self.cal_min[i] for i in range(3)]
        avg_range = sum(ranges) / 3

        # Auto-Tune Thresholds based on the range we found
        # If the range is huge (0 to 1200), a 50 threshold is too small.
        # If the range is tiny (0 to 100), a 50 threshold is risky.
        self.NOISE_GATE = avg_range * 0.1  # 10% of the signal is noise
        self.LOGIC_DETECT = avg_range * 0.5  # 50% is a confirmed line

        print(f"CALIBRATION COMPLETE")
        print(f"Black Offsets: {self.offsets}")
        print(f"Max Signals:   {self.cal_max}")
        print(f"Detected Range: {ranges}")