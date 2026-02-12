class PIDController:
    def __init__(self, kp, ki, kd, min_out, max_out):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.min_out = min_out
        self.max_out = max_out
        
        # Memory variables
        self.last_error = 0.0
        self.integral = 0.0
        
    def update(self, error, dt):
        """
        Calculates the PID output.
        :param error: The current error (Target - Current)
        :param dt: Time elapsed since last update (seconds)
        """
        # P Term
        P = self.kp * error
        
        # I Term (with anti-windup clamping)
        self.integral += error * dt
        # Clamp integral to avoid "windup" (e.g. +/- 50)
        self.integral = max(-50, min(50, self.integral)) 
        I = self.ki * self.integral
        
        # D Term
        if dt > 0:
            derivative = (error - self.last_error) / dt
        else:
            derivative = 0
        D = self.kd * derivative
        
        # Calculate Output
        output = P + I + D
        
        # Save error for next loop
        self.last_error = error
        
        # Clamp output to servo limits
        return max(self.min_out, min(self.max_out, output))

    def reset(self):
        """Clears the memory (good for after a hard turn)"""
        self.last_error = 0.0
        self.integral = 0.0