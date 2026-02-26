class LineSensor:
    def __init__(self, offsets):
        self.cal_min = list(offsets)
        self.cal_max = [offset + 1000 for offset in offsets]
        self.offsets = offsets  # [L, M, R]

        # Signal gates and tuning
        self.WHITE_CUTOFF = 1000
        self.MIN_LINE_PERCENT = 5.0
        self.NOISE_GATE = 10.0
        self.LOGIC_DETECT = 30.0
        self.LINE_PRESENT_ON = 12.0
        self.LINE_PRESENT_OFF = 6.0
        self.RECOVERY_STEER = 40
        self.BRANCH_BIAS = 20
        self.BASE_SPEED = 30
        self.BRANCH_SPEED = 10

        # Calibration/tuning constants
        self.ADC_MAX = 4095
        self.CAL_SAMPLE_INTERVAL = 0.01
        self.CAL_TURN_ANGLE = 30
        self.CAL_TURN_SPEED = 10
        self.CAL_TURN_DURATION = 0.5
        self.CAL_STOP_DURATION = 0.1

        # Steering weights for weighted average
        self.weights = [1, 0, -1]

        # Memory for recovery steering
        self.last_line_seen = False
        self.line_present_latched = False
        # -1 = line was left, 0 = center, 1 = right
        self.last_line_direction = 0

    def color_signal(self, raw, sensor_index):
        if raw > self.WHITE_CUTOFF:
            return 0.0

        sensor_min = self.cal_min[sensor_index]
        sensor_max = self.cal_max[sensor_index]
        span = max(1.0, float(sensor_max - sensor_min))
        normalized_percent = ((raw - sensor_min) / span) * 100.0

        if normalized_percent < self.MIN_LINE_PERCENT:
            return 0.0
        
        return max(0.0, normalized_percent)

    def _signals(self, raw_values):
        l_raw, m_raw, r_raw = raw_values
        return (
            self.color_signal(l_raw, 0),
            self.color_signal(m_raw, 1),
            self.color_signal(r_raw, 2),
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

        strongest_signal = max(s_l, s_m, s_r)
        if self.line_present_latched:
            has_line = strongest_signal > self.LINE_PRESENT_OFF
        else:
            has_line = strongest_signal > self.LINE_PRESENT_ON
        self.line_present_latched = has_line

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
            base_speed = self.BRANCH_SPEED
        elif bias_mode == "l" and has_mid and has_left:
            error += self.BRANCH_BIAS
            base_speed = self.BRANCH_SPEED

        return error, stop_detected, base_speed

    def apply_calibration(self, cal_min, cal_max):
        # Record signal range (Max - Min)
        self.cal_min = cal_min
        self.cal_max = cal_max
        self.offsets = cal_min

        ranges = [self.cal_max[i] - self.cal_min[i] for i in range(3)]
        avg_range = sum(ranges) / 3

        # Thresholds are now interpreted in normalized percent space (0-100).
        self.NOISE_GATE = 10.0
        self.LOGIC_DETECT = 50.0

        print(f"CALIBRATION APPLIED")
        print(f"Black Offsets: {self.offsets}")
        print(f"Max Signals:   {self.cal_max}")
        print(f"Detected Range: {ranges}")
        print(f"Average Range: {avg_range}")