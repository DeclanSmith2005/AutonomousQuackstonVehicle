---
title: "5V Voltage Regulator Circuit Design"
date: 2025-01-08
week: 1
author: Jane Smith
team: Super Awesome Team
hours: 3.5
tags: [circuit-design, voltage-regulator, power-supply]
status: completed
---

# 5V Voltage Regulator Circuit Design

> **Session Date**: January 8, 2025  
> **Duration**: 10:00 AM - 1:30 PM (3.5 hours)  
> **Location**: Electronics Lab, Room 204

## 🎯 Objectives

Design and test a 5V voltage regulator circuit for powering microcontroller projects.

- Design circuit schematic using LM7805 regulator
- Calculate component values for stable operation
- Build and test prototype on breadboard
- Measure output voltage stability under load

## 📋 Detailed Work Log

### Session 1: Circuit Design (10:00 AM - 11:30 AM)

**Description**:  
Designed a linear voltage regulator circuit using the LM7805 IC to convert 9V battery input to stable 5V output.

**Materials/Tools Used**:
- LM7805 voltage regulator IC
- 10µF and 1µF capacitors
- 9V battery and connector
- Breadboard and jumper wires
- Multimeter

**Process/Steps**:
1. Reviewed LM7805 datasheet for pin configuration and recommended circuit
2. Calculated minimum input voltage: $V_{in(min)} = V_{out} + V_{dropout} = 5V + 2V = 7V$
3. Selected capacitors: 10µF on input, 1µF on output (per datasheet)
4. Drew circuit schematic

**Calculations**:

Maximum current capacity:
$$I_{max} = 1A$$

Power dissipation at full load:
$$P_{dissipated} = (V_{in} - V_{out}) \times I_{load}$$
$$P_{dissipated} = (9V - 5V) \times 0.5A = 2W$$

Therefore, heatsink required for loads > 500mA.

### Session 2: Breadboard Implementation (11:30 AM - 1:00 PM)

**Description**:  
Built the circuit on breadboard and performed initial testing.

**Process**:
1. Placed LM7805 on breadboard
2. Connected 10µF capacitor on input (pin 1 to GND)
3. Connected 1µF capacitor on output (pin 3 to GND)
4. Connected 9V battery to input
5. Measured output voltage with no load

**Initial Results**:
- Input voltage: 9.1V
- Output voltage (no load): 4.98V ✅
- Ripple voltage: < 20mV ✅

### Session 3: Load Testing (1:00 PM - 1:30 PM)

**Description**:  
Tested circuit performance under different load conditions.

**Test Setup**:
- Used variable resistor as load
- Measured output voltage at different currents
- Monitored regulator temperature

## 📊 Results & Data

### Measurements/Observations

| Load Current | Output Voltage | Regulation | IC Temperature | Pass/Fail |
|--------------|----------------|------------|----------------|-----------|  
| 0mA          | 4.98V          | -          | Ambient        | ✅ Pass   |
| 100mA        | 4.97V          | 0.2%       | Warm           | ✅ Pass   |
| 250mA        | 4.96V          | 0.4%       | Hot            | ✅ Pass   |
| 500mA        | 4.94V          | 0.8%       | Very Hot       | ⚠️ Needs heatsink|

### Key Findings

1. Circuit functions correctly within specified range
2. Voltage regulation excellent (<1%) up to 500mA
3. Heatsink required for loads > 250mA for extended operation
4. Ripple voltage well within acceptable limits

## 🐛 Challenges & Solutions

### Challenge 1: Initial Output Voltage Too Low (4.2V)

**Problem**: First measurement showed output of only 4.2V instead of expected 5V.

**Debugging Steps**:
1. Checked input voltage → OK (9.1V)
2. Verified IC orientation → **Found issue**: IC was backwards!
3. Rechecked datasheet pin diagram
4. Flipped IC 180 degrees

**Solution**: Corrected IC orientation. Output now 4.98V.

**Lesson Learned**: Always double-check IC pinout before powering circuit. Pin 1 is input, not output.

### Challenge 2: Circuit Getting Very Hot

**Problem**: LM7805 became uncomfortably hot to touch at 500mA load.

**Analysis**:  
Power dissipation calculation:
$$P = (9V - 5V) \times 0.5A = 2W$$

LM7805 thermal resistance: 65°C/W  
Expected temperature rise: $2W \times 65°C/W = 130°C$ ⚠️

**Solution**: Need to add TO-220 heatsink for loads > 250mA or reduce input voltage to 7V.

## 🔄 Next Steps

- [x] Complete initial circuit design
- [x] Test basic functionality
- [ ] Order appropriate heatsink (TO-220 package)
- [ ] Design PCB layout in KiCad
- [ ] Add LED power indicator
- [ ] Add protection diode for input polarity
- [ ] Test with actual microcontroller load

## 📚 References

- [LM7805 Datasheet](https://www.ti.com/lit/ds/symlink/lm7805.pdf) - Texas Instruments
- [Voltage Regulator Design Guide](https://www.electronics-tutorials.ws/power/linear-voltage-regulator.html)
- Course textbook: Chapter 12 - Power Supply Design

## 💭 Personal Notes

This was a good learning experience with linear regulators. Key takeaway: linear regulators are simple but inefficient for large voltage differences. For battery-powered projects, should consider switching regulators instead.

The thermal management issue was eye-opening - never realized how much heat would be generated. This makes sense given the power dissipation formula, but experiencing it firsthand reinforces the importance of proper thermal design.

Next time: Start with thermal calculations BEFORE building the circuit!

---

**Entry completed**: 2025-01-08 13:45