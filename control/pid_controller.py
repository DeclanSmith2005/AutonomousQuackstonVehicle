class PIDController:
    """
    Standard PID controller for steering control.
    """
    def __init__(self, kp, ki, kd, min_out, max_out):
        """
        Initialize the PID controller.

        Parameters
        ----------
        kp, ki, kd : float
            Proportional, Integral, and Derivative gains.
        min_out, max_out : float
            Lower and upper bounds for the controller output (e.g., servo limits).
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_out = min_out
        self.max_out = max_out
        
        # Memory variables
        self.last_error = 0.0
        self.integral = 0.0
        self.last_output = 0.0
        self.filtered_derivative = 0.0
        
    def update(self, error, dt):
        """
        Calculate the PID output based on current error and elapsed time.

        Parameters
        ----------
        error : float
            The current error (Target - Measured).
        dt : float
            Time elapsed since the last update (seconds).
        
        Returns
        -------
        float
            Clamped controller output.
        """
        if dt <= 0:
            return self.last_output

        # Proportional term
        P = self.kp * error
        
        # Integral term
        self.integral += error * dt
        I = self.ki * self.integral
        
        # Derivative term with low-pass filter to suppress noise spikes
        raw_derivative = (error - self.last_error) / dt
        alpha = 0.3  # Lower = smoother but laggier
        self.filtered_derivative = alpha * raw_derivative + (1 - alpha) * self.filtered_derivative
        
        # Cap the filtered derivative to prevent saturation spikes from dominating
        max_deriv = 200.0
        self.filtered_derivative = max(-max_deriv, min(max_deriv, self.filtered_derivative))
        
        D = self.kd * self.filtered_derivative
        
        # Calculate combined output
        output = P + I + D
        
        # Save state for the next update
        self.last_error = error
        
        # Clamp output to specified limits
        self.last_output = max(self.min_out, min(self.max_out, output))
        return self.last_output

    def reset(self):
        """
        Reset controller memory to prevent windup or derivative spikes 
        after a mode switch or long pause.
        """
        self.last_error = 0.0
        self.integral = 0.0
        self.last_output = 0.0
        self.filtered_derivative = 0.0