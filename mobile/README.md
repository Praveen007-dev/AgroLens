# AgroLens mobile app

AgroLens is a phone-first Flutter app for photographing crop leaves, optionally
adding a consented location, and reviewing a crop-health result. The interface
is available in English, Hindi, Telugu, Tamil, and Kannada.

## Crop coverage

The plant field accepts any crop or plant name. The current demo does **not**
perform image recognition: it generates simulated examples for tomato, potato,
corn, bell pepper, and rice only, and reports unsupported crops instead of
silently substituting tomato. There is no trained TensorFlow Lite model in
this repository yet. Detecting additional plants requires training and
validating a model with representative images and labels for those species and
conditions.

## Run on a phone

Open this directory in Android Studio or Xcode and run the Flutter project on a
connected Android or iOS device. The native `android/` and `ios/` projects are
included. Android builds require the Android SDK; iOS builds require macOS and
Xcode.

To build an Android APK:

```shell
flutter pub get
flutter build apk --release
```

For browser preview only:

```shell
flutter run -d chrome
```

## Test

```shell
flutter analyze
flutter test
```
