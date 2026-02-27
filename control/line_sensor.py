"""
Line Sensor Module
Handles grayscale sensor signal processing and pattern detection.
"""

class LineSensor:
    # Detection threshold (fraction of calibrated range)
    LOGIC_DETECT = 0.35  # sensor shows line at ~35%+ of range

    WHITE_DETECT = 0.90

    # Speed settings
    BASE_SPEED = 20
    MIN_SPEED = 5

    def __init__(self, offsets):
        """
        offsets: [left_offset, center_offset, right_offset] in mm or arbitrary units
        """
        self.offsets = offsets
        self.cal_min = [0, 0, 0]
        self.cal_max = [4095, 4095, 4095]
        self.last_line_seen = True
        self.last_error = 0.0

    def apply_calibration(self, cal_min, cal_max):
        """Apply calibration values from wiggle routine."""
        self.cal_min = cal_min
        self.cal_max = cal_max
        print(f"Calibration applied: min={cal_min}, max={cal_max}")

    def color_signal(self, raw_value, sensor_idx):
        """
        Convert raw ADC value to normalized signal [0.0, 1.0].
        0 = off line (low reflectance), 1 = on line (high reflectance)
        """
        cmin = self.cal_min[sensor_idx]
        cmax = self.cal_max[sensor_idx]

        if cmax <= cmin:
            return 0.0
        normalized = (raw_value - cmin) / (cmax - cmin)

        return max(0.0, min(1.0, normalized))

    def analyze_pattern(self, raw):
        """
        Analyze 3-sensor array to detect patterns.
        Returns: 'LINE', 'CROSS_GREEN', 'STOP_WHITE', or 'NONE'
        """
        signals = [self.color_signal(raw[i], i) for i in range(3)]
        # left, center, right = signals
        
        # All three sensors detect line = intersection or stop
        if (all(s > self.LOGIC_DETECT for s in signals) or
                all(s > self.LOGIC_DETECT for s in signals[:2]) or  # left and center
                all(s > self.LOGIC_DETECT for s in signals[1:])):  # center and right
            return "CROSS"

        # At least one sensor detects white line
        if any(s > self.WHITE_DETECT for s in signals):
            return "BOUNDARY"

        # At least one sensor detects line
        if any(s > self.LOGIC_DETECT for s in signals): # update main.py
            return "LINE"
        
        return "NONE"

    def compute_error(self, raw):
        """
        Compute lateral error from sensor readings using weighted average.
        Returns: (error, stop_detected, base_speed)
        
        Error: positive = line is to the left (steer left), negative = line is to the right (steer right)
        """
        signals = [self.color_signal(raw[i], i) for i in range(3)]
        left, center, right = signals
        
        pattern = self.analyze_pattern(raw)
        stop_detected = (pattern == "CROSS")
        
        # Check if any sensor sees the line
        total_signal = left + center + right
        
        if total_signal < 0.2:
            # No line detected - use last known error direction
            self.last_line_seen = False
            # Return last error amplified to encourage correction
            return self.last_error * 1.3, stop_detected, self.BASE_SPEED
        
        self.last_line_seen = True
        
        # Weighted average position calculation
        # Left sensor = +1, Center = 0, Right = -1
        # Positive error = line to left = steer left (positive servo angle)
        # Negative error = line to right = steer right (negative servo angle)
        
        #if total_signal > 0.01:
        weighted_pos = (left - right) / total_signal
        # Scale to -100 to +100 range
        error = weighted_pos * 100.0
        #else:
        #    error = 0.0
        
        self.last_error = error
        
        # Reduce speed when error is large
        speed = self.BASE_SPEED
        if abs(error) > 50:
            speed = self.MIN_SPEED
        
        return error, stop_detected, speed