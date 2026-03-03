---
title: "[Training Data Annotations, Model Training and Validation]"
date: 2026-02-28
week: 6.5
hours: 5.0
tags: [Data Annotation, Model Training, Model Testing]
contributors: [Nolan Su-Hackett]
---

# Daily Logbook Entry Template

## Objectives

What did you plan to accomplish in this session?

- Complete Annotating my delegated set of images Cars(50), Oneways(100), and Yield(50). 
- Ensure that the Validation Scores like mAP (mean Average Precision) values fall within our defined target which was 0.8
- Following Validation, Port the model to the car, and evaluate its live performance

## Detailed Work Log

### Session 1: [Data Annotation, Model Training, Validation] (12:00 - 17:00)

**Members Present**: [Nolan Su-Hackett]

**Description**: 
Used an online software recommended by the gitbook to create PASCAL VOC XML annotations. The activity consisted of drawing tight bounding boxes around each of the objects, and labelling them. The labels used were car, Leftway, Rightway, and Yield. The oneway class was split into directions so that when the object detection was run, the model would know which way the oneway is facing. This was not necessary as the team will have access to the map and street directions however, it could provide a fallback method if one was needed. Changed code to match our application and labels, then follow the google colab to create model and port to car for validation.

Altered the train_road_signs_model.py file so that the labels in that file matches the labels in the xml files.

Follow the Google Colab file: ELEC 392 - EfficientDet-Lite Detector for the Coral TPU - European Road Signs with the modified dataset which would be the annotations + images, and the altered train_road_signs_model.py file.

Record mAP files and port the model to the Raspberry Pi.


**Materials/Tools Used**:
- Python (Code modification of train_road_signs_model)
- Makesense (labelling)
- Google Colab
- Filezilla (Porting the model)

**Process/Steps**:
1. Annotate Images
2. Modify train_road_signs_model.py file so that the labels in that file matches the labels in the xml files.
3. Follow the Google Colab file: ELEC 392 - EfficientDet-Lite Detector for the Coral TPU - European Road Signs with the modified dataset which would be the annotations + images, and the altered train_road_signs_model.py file.
4. Record mAP files and port the model to the Raspberry Pi.
5. Test model live on the car.

**Documentation**:

These are the final evaluation results for each of the classes.
tflite model evaluation results: 
{'AP': 0.67734873, 'AP50': 0.80261075, 'AP75': 0.7602328, 'APs': -1.0, 'APm': 0.681984, 'APl': 0.6967611, 'ARmax1': 0.74449927, 'ARmax10': 0.7502135, 'ARmax100': 0.7516421, 'ARs': -1.0, 'ARm': 0.76838094, 'ARl': 0.71459186, 'AP_/car': 0.713041, 'AP_/DNE': 0.89257425, 'AP_/Duck': 0.9110089, 'AP_/crosswalk': -1.0, 'AP_/Leftway': 0.42610046, 'AP_/Rightway': 0.010212609, 'AP_/Stop': 0.947005, 'AP_/Yield': 0.8414989}

### Code Snippets
Changes made to train_road_sign_model file
```python

 Your labels map as a dictionary (zero is reserved):
label_map = {1: 'DNE', 2: 'Duck', 3: 'Leftway', 4: 'Stop', 5: 'Yield', 6: 'Rightway, 7: 'Car'}

```

## Challenges & Solutions

### Challenge 1: [Oneway Detection Failure]

**Problem**: 
Generally the evaluation results were in target range of 0.8, however for the classes Leftway and Rightway the model seems to struggle.

**Debugging Steps**:
1.Ported model to car to test it live to see what problems it was having when distinguishing the oneway sign. The model seemed quite good at identifying the oneway sign itself as either leftway or rightway, which means that the problem was not with identifying the sign but identifying the direction as both directions look generally similar.

**Solution**: 
The solution to that problem would be relabelling the oneway sign as just oneway rather than separating it into the direction based classification.
**Lessons Learned**: 
- it is difficult to classify a variation of a class, like the direction of a oneway sign, the lesson learned is to keep this in mind when deciding what classes to use and to think about alternatives for the classes that do need a more specified variation.

### Challenge 2: [Car Class is Over Detected]

**Problem**: 
Although the evaluation results for the car were not bad on the testing image set, when the model was tested live, it was overclassifying the car class.

**Debugging Steps**:
1.Ported model to car to test it live to see what problems arise, and it was revealed that the model was identifying cars in a lot of empty spaces.

**Solution**: 
Attempt to redraw bounding boxes on just the wheels separately rather than bounding wheels together iwth empty space, this will make it so that the model will identify the empty spaces as cars less often.
**Lessons Learned**: 
- avoid empty spaces in bounding boxes if possible,
## Next Steps
- [ ] Retrain with the One way Label
- [ ] Redraw the bounding boxes on the Car to only identify individual wheels rather than capturign the wheels and all the space between them


## References

## Personal Notes

- be mindful of what a model can misinterpret, and plan around it, a model will not be perfect so have backups and fail safes.
---

**Entry completed**: 2026-02-28 17:00
