---
title: "[CTE Filtering & PolyFit Cuts]"
date: 2026-03-04
week: 8
hours: 4.0
tags: [Perception, Coding]
contributors: [Nolan Su-Hackett]
---

# Daily Logbook Entry Template

## Objectives

What did you plan to accomplish in this session?

- Clean up filtering of CTE for Turns
- Create cuts on turn masks to allow better curve fitting 
- Design y_reference points at which CTE offset values in meters will be returned for PID Loop

## Detailed Work Log

### Session 1: [CTE Cleanup, PolyFit Cuts] (12:00 - 15:00)

**Members Present**: [Nolan Su-Hackett]

**Description**: 
Reviewed previously written turn masking code, and added some changes that should clean it up and allow tighter and more accurate fitting. Changes will be described in relation to code changes below

```python
#Old Masking Code: V1

            # right side of the lane (mirror = take x >= lane_center_x)
            # mask_turn[
            #     max(intersection_y - roi_half_width, 0): min(intersection_y + roi_half_width, height),
            #     lane_center_x:
            # ] = 255

            #Newer Code Tighter Filtering V2
            y0 = intersection_y
            y1 = min(intersection_y + int(2.5 * roi_half_width), height)
            mask_turn[y0: y1, l:] = 255

```
Changes:
1. Intersection_y is the highest row at which an intersection is detected, this would be the highest row of the green cross that would appear in the BEV transform. Previously the code took tolerance above this point however this is not necessary as it should already be the upper bound, intersection_y will now be the new upper bound on y.
2. Previously the lower bound takes a distance which is half a tape width below the highest detected intersection point, this means that the bottom half rows of the turn pixels can be cut out, this is changed in V2, by allowed 1.25* a full tape width below the highest detected intersection point.
3. Previously the x bound filtered everything on the other side of the lane center (dependent on case (left or right)), however this can cut off half of the straight section of the tape. Instead of the center V2 uses the left or right, which are defined as the left or right bounds of the centered green tape.

PolyFit Cuts:

```python
mask_turn[:int(0.8*height), :int(0.7*width) ] = 0
mask_turn[:int(0.8*height), int(0.2*width):] = 0
```

Line 1: cuts a rectangle out off the Turn_BEV, this is so that the polynomial does not need to fit to a large proportion of pixels that create the shape of a 90-degree turn. This was done so that the polunomial curve will fit a more natural turn path, the images can be seen in the documentation section

**Materials/Tools Used**:
- Python
**Process/Steps**:
1. Read previously written code
2. Identify possible optimizations
3. devise a way for the polynomial to fit a more natural turning path.

**Documentation**:
![Reference Image](elec-392-project-duclair_2/images/week-08/NewLanes_1_.jpg)
Figure 1: Reference Image
![Pre-Cleanup](elec-392-project-duclair_2/images/week-08/PreFilterAdjustments.png)
Figure 2: Original BEV and Transformed BEV before the work on the cleanup
![Post-Cleanup](images/week-08/PostFilterAdjustments.png)
Figure 3: Original BEV and Transformed BEV after the cleanup was done
![PolyFit Cuts](images/week-08/PolyFitCuts.png)
Figure 4: After creating the rectangular cut to the TURN BEV for the polyfit


### Session 2: [Activity Name] (HH:MM - HH:MM)

**Members Present**: [Name1, Name2, Name3]

**Description**:

## Results & Data

### Measurements/Observations

| Parameter | Expected | Measured | Pass/Fail | Notes |
|-----------|----------|----------|-----------|-------|
| | | | | |

### Code Snippets

```python
# Add relevant code here
```

### Calculations

Show your mathematical work:

$$
x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
$$

## Challenges & Solutions

### Challenge 1: [Issue Description]

**Problem**: 

**Debugging Steps**:
1.
2.
3.

**Solution**: 

**Lessons Learned**: 

## Next Steps

- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## References

- [Reference 1](URL)
- [Reference 2](URL)

## Personal Notes

Any additional thoughts, observations, or things to remember...

---

**Entry completed**: YYYY-MM-DD HH:MM
