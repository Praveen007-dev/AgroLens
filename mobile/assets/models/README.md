# AgroLens Machine Learning Assets

`labels.txt` currently contains disease classes for tomato, potato, corn, bell
pepper, and rice. There is no trained `.tflite` model in this repository yet;
the app currently generates simulated examples for those crops and does not
perform image recognition. Entering another plant name is allowed, but the
demo reports that it cannot classify that plant instead of returning a
prediction for a different crop.

## Adding a trained model

1. Place your quantized `.tflite` model file here:
   - File path: `assets/models/crop_disease_model.tflite`
2. Update `labels.txt` to exactly match the model's output classes and order.
3. Include representative training and validation data for every supported
   crop, healthy condition, and disease. Adding a crop name alone does not add
   model support for that crop.
4. Document the required input dimensions and normalization in
   `mobile/lib/config/app_config.dart`.
