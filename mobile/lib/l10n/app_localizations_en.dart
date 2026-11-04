// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'AgroLens';

  @override
  String get languageLabel => 'Language';

  @override
  String get languageEnglish => 'English';

  @override
  String get languageHindi => 'हिन्दी';

  @override
  String get languageTelugu => 'తెలుగు';

  @override
  String get languageTamil => 'தமிழ்';

  @override
  String get languageKannada => 'ಕನ್ನಡ';

  @override
  String get checkYourCrop => 'A healthier harvest starts here';

  @override
  String get scanIntroduction =>
      'Photograph a leaf to check for visible crop health issues.';

  @override
  String get plantNameLabel => 'Plant or crop';

  @override
  String get plantNameHint => 'Type any plant name';

  @override
  String get plantNameRequired => 'Enter the plant or crop name first.';

  @override
  String get supportedCropsTitle => 'Quick select';

  @override
  String get modelCoverageNotice =>
      'Any plant name can be entered. This demo uses simulated results, not image recognition. Its placeholder labels cover tomato, potato, corn, bell pepper, and rice only.';

  @override
  String cropNotSupported(String crop) {
    return 'The demo cannot analyze $crop yet. No diagnosis was made. Its placeholder labels cover tomato, potato, corn, bell pepper, and rice only.';
  }

  @override
  String get demoModeNotice =>
      'Demo mode: predictions are simulated and are not a diagnosis.';

  @override
  String get cropLabel => 'Crop';

  @override
  String get cropTomato => 'Tomato';

  @override
  String get cropPotato => 'Potato';

  @override
  String get cropCorn => 'Corn';

  @override
  String get cropPepper => 'Bell pepper';

  @override
  String get cropRice => 'Rice';

  @override
  String get choosePhoto => 'Choose a photo';

  @override
  String get takePhoto => 'Take a photo';

  @override
  String get photoActionsHint =>
      'Use a clear, well-lit photo of one affected leaf.';

  @override
  String get photoSelected => 'Photo selected';

  @override
  String get analyzePhoto => 'Analyze photo';

  @override
  String get analyzing => 'Analyzing...';

  @override
  String errorCouldNotOpenPhoto(String error) {
    return 'Could not open the image: $error';
  }

  @override
  String errorCouldNotAnalyzePhoto(String error) {
    return 'Could not analyze this image: $error';
  }

  @override
  String errorCouldNotSaveScan(String error) {
    return 'The prediction is ready, but the scan could not be saved on this device: $error';
  }

  @override
  String get predictionTitle => 'Prediction';

  @override
  String resultSummary(String crop, String confidence) {
    return '$crop · $confidence confidence';
  }

  @override
  String get lowConfidenceWarning =>
      'Low confidence. Try a clearer photo and confirm the result with an agricultural expert.';

  @override
  String modelVersion(String version) {
    return 'Model: $version';
  }

  @override
  String get locationTitle => 'Optional location';

  @override
  String get locationPrivacyNotice =>
      'Your location is only requested if you choose Add location. If added, coordinates are saved with this scan on this device.';

  @override
  String get addLocation => 'Add location';

  @override
  String get removeLocation => 'Remove location';

  @override
  String get gettingLocation => 'Getting location...';

  @override
  String locationCoordinates(String latitude, String longitude) {
    return 'Coordinates: $latitude, $longitude';
  }

  @override
  String get locationServiceDisabled =>
      'Location services are turned off. Turn them on and try again.';

  @override
  String get locationPermissionDenied =>
      'Location permission was denied. Allow location access to add a location to this scan.';

  @override
  String get locationPermissionDeniedForever =>
      'Location permission is blocked. Enable it in your browser or device settings to add a location.';

  @override
  String locationRequestFailed(String error) {
    return 'Could not get your location: $error';
  }

  @override
  String get scanSavedLocally => 'Scan saved on this device.';

  @override
  String get diseaseHealthy => 'Healthy plant';

  @override
  String get diseaseBacterialSpot => 'Bacterial spot';

  @override
  String get diseaseEarlyBlight => 'Early blight';

  @override
  String get diseaseLateBlight => 'Late blight';

  @override
  String get diseaseLeafMold => 'Leaf mold';

  @override
  String get diseaseSeptoriaLeafSpot => 'Septoria leaf spot';

  @override
  String get diseaseSpiderMites => 'Two-spotted spider mite';

  @override
  String get diseaseTargetSpot => 'Target spot';

  @override
  String get diseaseYellowLeafCurlVirus => 'Yellow leaf curl virus';

  @override
  String get diseaseMosaicVirus => 'Mosaic virus';

  @override
  String get diseaseCommonRust => 'Common rust';

  @override
  String get diseaseNorthernLeafBlight => 'Northern leaf blight';

  @override
  String get diseaseBrownSpot => 'Brown spot';

  @override
  String get diseaseLeafBlast => 'Leaf blast';
}
