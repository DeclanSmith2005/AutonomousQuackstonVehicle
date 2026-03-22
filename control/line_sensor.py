"""
Line Sensor Module
Handles grayscale sensor signal processing and pattern detection.
"""

class LineSensor:
    """
    Handles grayscale sensor signal processing and pattern detection.
    """
    # Detection threshold (fraction of calibrated range)
    LOGIC_DETECT = 0.55
    WHITE_DETECT = 0.90

    def __init__(self, offsets):
        """
        Initialize the LineSensor with hardware offsets.

        Parameters
        ----------
        offsets : list of float
            [left_offset, center_offset, right_offset] to correct sensor bias.
        """
        self.offsets = offsets
        self.cal_min = [0, 0, 0]
        self.cal_max = [4095, 4095, 4095]
        self.last_line_seen = True
        self.last_error = 0.0

    def apply_calibration(self, cal_min, cal_max):
        """
        Apply calibration values from the wiggle routine.

        Parameters
        ----------
        cal_min : list of int
            Minimum ADC values seen for each sensor.
        cal_max : list of int
            Maximum ADC values seen for each sensor.
        """
        self.cal_min = cal_min
        self.cal_max = cal_max
        print(f"Calibration applied: min={cal_min}, max={cal_max}")

    def color_signal(self, raw_value, sensor_idx):
        """
        Convert raw ADC value to normalized signal [0.0, 1.0].
        0 = off line (low reflectance), 1 = on line (high reflectance)
        """
        corrected = raw_value - self.offsets[sensor_idx]  # apply bias correction
        cmin = self.cal_min[sensor_idx]
        cmax = self.cal_max[sensor_idx]

        if cmax <= cmin:
            return 0.0
        
        normalized = (corrected - cmin) / (cmax - cmin)
        return max(0.0, min(1.0, normalized))

    def get_signals(self, raw):
        """Return normalized [left, center, right] signals in range [0, 1]."""
        return [self.color_signal(raw[i], i) for i in range(3)]

    def active_sensor_mask(self, raw, threshold=None):
        """Return boolean mask [left, center, right] indicating sensors above threshold."""
        detect_threshold = self.LOGIC_DETECT if threshold is None else threshold
        return [self.color_signal(raw[i], i) > detect_threshold for i in range(3)]

    def active_sensor_count(self, raw, threshold=None):
        """Return count of sensors currently above the threshold."""
        return sum(self.active_sensor_mask(raw, threshold))

    def analyze_pattern(self, raw, update_history=True):
        """
        Analyze the 3-sensor array to detect specific track patterns.

        Returns
        -------
        str
            'CROSS' if all sensors see the line,
            'BOUNDARY' if white boundary is detected,
            'LINE' if at least one sensor sees the line,
            'NONE' otherwise.
        """
        signals = self.get_signals(raw)
        current_mask = [s > self.LOGIC_DETECT for s in signals]

        left_active = current_mask[0]
        center_active = current_mask[1]
        right_active = current_mask[2]

        # All three sensors detect line recently = intersection or stop.
        if left_active and center_active and right_active:
            return "CROSS"

        # At least one sensor detects white boundary (high reflectance)
        if any(s > self.WHITE_DETECT for s in signals):
            return "BOUNDARY"

        # At least one sensor detects regular line
        if any(current_mask):
            return "LINE"
        
        return "NONE"

    def is_full_cross(self, raw):
        """Check if all three sensors are above the detection threshold."""
        return self.analyze_pattern(raw, update_history=False) == "CROSS"

    def compute_error(self, raw):
        """
        Compute lateral error from sensor readings using a weighted average.
        
        Returns
        -------
        tuple (float, bool)
            (error, stop_detected)
            error: positive = line is to the left (steer left), 
                   negative = line is to the right (steer right)
            stop_detected: True if a 'CROSS' pattern is detected.
        """
        signals = self.get_signals(raw)
        left, center, right = signals
        
        pattern = self.analyze_pattern(raw, update_history=False)
        stop_detected = (pattern == "CROSS")
        
        # Check if any sensor sees the line
        total_signal = left + center + right
        
        if total_signal < 0.2:
            # No line detected - use last known error direction
            self.last_line_seen = False
            # Return last error amplified to encourage correction
            return self.last_error * 1.3, stop_detected
        
        self.last_line_seen = True
        
        # Weighted average position calculation
        # Left sensor = +1, Center = 0, Right = -1
        # Positive error = line to left = steer left (positive servo angle)
        # Negative error = line to right = steer right (negative servo angle)
        weighted_pos = (left - right) / total_signal
        
        # Scale to -100 to +100 range
        error = weighted_pos * 100.0
        self.last_error = error
        
        return error, stop_detected