%% 1. Import Data
data_table = readtable('step_response.csv');

raw_time = data_table.Time;
raw_u = data_table.Input_u;
raw_y = data_table.Output_y;

%% 2. Find the Step
% We look for the exact moment the servo moved.
% Your servo jumped from -13.9 to 20.
step_index = find(diff(raw_u) > 10, 1) + 1; % Find large jump

% Safety check
if isempty(step_index)
    error('Could not find the step input in the CSV data.');
end

%% 3. Slice and Shift Data
% We want some pre-step samples plus data FROM the step UNTIL the line is lost (Output = 0)
% Find where it hits 0 *after* the step
zero_indices = find(raw_y(step_index:end) == 0);

if ~isempty(zero_indices)
    % Stop 1 sample before it hits 0 to avoid garbage data
    end_index = step_index + zero_indices(1) - 2; 
else
    end_index = length(raw_y);
end

% Include a short pre-step window to satisfy transient-data requirements
pre_step_count = min(step_index - 1, 10);
start_index = step_index - pre_step_count;

% Create Clean Vectors
t_clean = raw_time(start_index:end_index);
u_clean = raw_u(start_index:end_index);
y_clean = raw_y(start_index:end_index);

% Shift Time to start at 0
t_clean = t_clean - t_clean(1);

% Shift Input/Output to start at 0 (Linearization around operating point)
% The tuner assumes Step(0 -> A) results in Response(0 -> B)
baseline_index = max(1, step_index - 1);
u0 = raw_u(baseline_index);
y0 = raw_y(baseline_index);
u_shifted = u_clean - u0; % Should go from 0 to 33.9
y_shifted = y_clean - y0; % Should start at 0 and go up

%% 4. Create System ID Object
% Calculate sample time (dt) from your time vector
dt = mean(diff(t_clean));

% Create the data object for the Tuner
tuning_data = iddata(y_shifted, u_shifted, dt);

% Plot to confirm it looks like a clean step response
figure(1);
plot(tuning_data);
title('Cleaned Step Response for PID Tuner');
grid on;

% Identify a process model with an integrator and delay
sys = procest(tuning_data, 'P0DI');

% Optional: check fit
figure; compare(tuning_data, sys);

% Open PID Tuner
pidtool(sys, 'PID');