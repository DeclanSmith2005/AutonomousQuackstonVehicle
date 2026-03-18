from picarx import Picarx
import time

px = Picarx()

print("--- CONTRAST CHECK ---")
print("1. Place sensors over the BLACK background.")
input("Press Enter to read Background...")
bg_vals = px.get_grayscale_data()
print(f"Background (Black): {bg_vals}")

print("\n2. Place sensors over the BLUE tape.")
input("Press Enter to read Line...")
line_vals = px.get_grayscale_data()
print(f"Line (Blue): {line_vals}")

# Calculate the Delta (Signal Strength)
avg_bg = sum(bg_vals) / 3
avg_line = sum(line_vals) / 3
delta = abs(avg_line - avg_bg)

print(f"\n--- RESULTS ---")
print(f"Signal Strength (Delta): {delta:.1f}")

if delta < 150:
    print("CRITICAL WARNING: Contrast is too low! The robot cannot see this line reliably.")
    print("Try distinct electrical tape (e.g., White or Reflective Silver).")
elif avg_line > avg_bg:
    print("CONFIGURATION: Line is LIGHTER than background. (Inverted Logic)")
else:
    print("CONFIGURATION: Line is DARKER than background. (Standard Logic)")