// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Kannada (`kn`).
class AppLocalizationsKn extends AppLocalizations {
  AppLocalizationsKn([String locale = 'kn']) : super(locale);

  @override
  String get appTitle => 'AgroLens';

  @override
  String get languageLabel => 'ಭಾಷೆ';

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
  String get checkYourCrop => 'ಉತ್ತಮ ಬೆಳೆಗೆ ಇಲ್ಲಿಂದ ಆರಂಭ';

  @override
  String get scanIntroduction =>
      'ಬೆಳೆಯಲ್ಲಿ ಕಾಣುವ ಸಮಸ್ಯೆಗಳನ್ನು ಪರಿಶೀಲಿಸಲು ಎಲೆಯ ಚಿತ್ರ ತೆಗೆಯಿರಿ.';

  @override
  String get plantNameLabel => 'ಸಸ್ಯ ಅಥವಾ ಬೆಳೆ';

  @override
  String get plantNameHint => 'ಯಾವುದೇ ಸಸ್ಯದ ಹೆಸರನ್ನು ನಮೂದಿಸಿ';

  @override
  String get plantNameRequired => 'ಮೊದಲು ಸಸ್ಯ ಅಥವಾ ಬೆಳೆಯ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.';

  @override
  String get supportedCropsTitle => 'ತ್ವರಿತ ಆಯ್ಕೆ';

  @override
  String get modelCoverageNotice =>
      'ಯಾವುದೇ ಸಸ್ಯದ ಹೆಸರನ್ನು ನಮೂದಿಸಬಹುದು. ಈ ಡೆಮೊ ಚಿತ್ರವನ್ನು ಗುರುತಿಸುವುದಿಲ್ಲ; ಅನುಕರಣೆಯ ಫಲಿತಾಂಶಗಳನ್ನು ಮಾತ್ರ ತೋರಿಸುತ್ತದೆ. ಇದರ ಮಾದರಿ ಲೇಬಲ್‌ಗಳು ಟೊಮೇಟೊ, ಆಲೂಗಡ್ಡೆ, ಮೆಕ್ಕೆಜೋಳ, ದೊಣ್ಣೆ ಮೆಣಸಿನಕಾಯಿ ಮತ್ತು ಭತ್ತಕ್ಕೆ ಮಾತ್ರ ಇವೆ.';

  @override
  String cropNotSupported(String crop) {
    return 'ಈ ಡೆಮೊ $crop ಅನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ಯಾವುದೇ ರೋಗನಿರ್ಣಯ ಮಾಡಿಲ್ಲ. ಇದರ ಮಾದರಿ ಲೇಬಲ್‌ಗಳು ಟೊಮೇಟೊ, ಆಲೂಗಡ್ಡೆ, ಮೆಕ್ಕೆಜೋಳ, ದೊಣ್ಣೆ ಮೆಣಸಿನಕಾಯಿ ಮತ್ತು ಭತ್ತಕ್ಕೆ ಮಾತ್ರ ಇವೆ.';
  }

  @override
  String get demoModeNotice =>
      'ಡೆಮೊ ಮೋಡ್: ಮುನ್ಸೂಚನೆಗಳು ಅನುಕರಣೆಯಾಗಿವೆ; ಇವು ರೋಗನಿರ್ಣಯವಲ್ಲ.';

  @override
  String get cropLabel => 'ಬೆಳೆ';

  @override
  String get cropTomato => 'ಟೊಮೇಟೊ';

  @override
  String get cropPotato => 'ಆಲೂಗಡ್ಡೆ';

  @override
  String get cropCorn => 'ಮೆಕ್ಕೆಜೋಳ';

  @override
  String get cropPepper => 'ದೊಣ್ಣೆ ಮೆಣಸಿನಕಾಯಿ';

  @override
  String get cropRice => 'ಭತ್ತ';

  @override
  String get choosePhoto => 'ಚಿತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ';

  @override
  String get takePhoto => 'ಚಿತ್ರ ತೆಗೆಯಿರಿ';

  @override
  String get photoActionsHint =>
      'ಬಾಧಿತವಾದ ಒಂದು ಎಲೆಯ ಸ್ಪಷ್ಟ ಮತ್ತು ಚೆನ್ನಾಗಿ ಬೆಳಗಿದ ಚಿತ್ರ ತೆಗೆಯಿರಿ.';

  @override
  String get photoSelected => 'ಚಿತ್ರ ಆಯ್ಕೆಯಾಗಿದೆ';

  @override
  String get analyzePhoto => 'ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಿ';

  @override
  String get analyzing => 'ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...';

  @override
  String errorCouldNotOpenPhoto(String error) {
    return 'ಚಿತ್ರವನ್ನು ತೆರೆಯಲಾಗಲಿಲ್ಲ: $error';
  }

  @override
  String errorCouldNotAnalyzePhoto(String error) {
    return 'ಈ ಚಿತ್ರವನ್ನು ವಿಶ್ಲೇಷಿಸಲಾಗಲಿಲ್ಲ: $error';
  }

  @override
  String errorCouldNotSaveScan(String error) {
    return 'ಮುನ್ಸೂಚನೆ ಸಿದ್ಧವಾಗಿದೆ, ಆದರೆ ಸ್ಕ್ಯಾನ್ ಅನ್ನು ಈ ಸಾಧನದಲ್ಲಿ ಉಳಿಸಲಾಗಲಿಲ್ಲ: $error';
  }

  @override
  String get predictionTitle => 'ಮುನ್ಸೂಚನೆ';

  @override
  String resultSummary(String crop, String confidence) {
    return '$crop · ವಿಶ್ವಾಸ ಮಟ್ಟ $confidence';
  }

  @override
  String get lowConfidenceWarning =>
      'ವಿಶ್ವಾಸ ಮಟ್ಟ ಕಡಿಮೆಯಿದೆ. ಸ್ಪಷ್ಟ ಚಿತ್ರ ತೆಗೆದು ಕೃಷಿ ತಜ್ಞರೊಂದಿಗೆ ಫಲಿತಾಂಶವನ್ನು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.';

  @override
  String modelVersion(String version) {
    return 'ಮಾದರಿ: $version';
  }

  @override
  String get locationTitle => 'ಕೃಷಿ ಭೂಮಿಯ ಸ್ಥಳ';

  @override
  String get locationPrivacyNotice =>
      'ಪ್ರತಿ ಸ್ಕ್ಯಾನ್‌ಗೆ ಸ್ಥಳ ಅಗತ್ಯ. ಗುಂಡಿಯನ್ನು ಒತ್ತಿದಾಗ ಮಾತ್ರ ಸ್ಥಳವನ್ನು ಕೇಳಲಾಗುತ್ತದೆ ಮತ್ತು ಈ ಸಾಧನದಲ್ಲಿ ಸ್ಕ್ಯಾನ್‌ನೊಂದಿಗೆ ಉಳಿಸಲಾಗುತ್ತದೆ.';

  @override
  String get requiredLabel => 'ಅಗತ್ಯ';

  @override
  String get readyLabel => 'ಸಿದ್ಧ';

  @override
  String get addLocation => 'ನನ್ನ ಸ್ಥಳ ಬಳಸಿ';

  @override
  String get updateLocation => 'ಸ್ಥಳ ನವೀಕರಿಸಿ';

  @override
  String get removeLocation => 'ಸ್ಥಳ ತೆಗೆದುಹಾಕಿ';

  @override
  String get gettingLocation => 'ಸ್ಥಳ ಪಡೆಯಲಾಗುತ್ತಿದೆ...';

  @override
  String get locationRequired =>
      'ಬೆಳೆಯನ್ನು ವಿಶ್ಲೇಷಿಸುವ ಮೊದಲು ಕೃಷಿ ಭೂಮಿಯ ಸ್ಥಳವನ್ನು ಹೊಂದಿಸಿ.';

  @override
  String locationCoordinates(String latitude, String longitude) {
    return 'ನಿರ್ದೇಶಾಂಕಗಳು: $latitude, $longitude';
  }

  @override
  String get locationServiceDisabled =>
      'ಸ್ಥಳ ಸೇವೆಗಳು ಆಫ್ ಆಗಿವೆ. ಅವುಗಳನ್ನು ಆನ್ ಮಾಡಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.';

  @override
  String get locationPermissionDenied =>
      'ಸ್ಥಳ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ. ಸ್ಕ್ಯಾನ್ ಮುಂದುವರಿಸಲು ಸ್ಥಳ ಅನುಮತಿ ನೀಡಿ.';

  @override
  String get locationPermissionDeniedForever =>
      'ಸ್ಥಳ ಅನುಮತಿಯನ್ನು ನಿರ್ಬಂಧಿಸಲಾಗಿದೆ. ಸ್ಕ್ಯಾನ್ ಮಾಡಲು ಬ್ರೌಸರ್ ಅಥವಾ ಸಾಧನದ ಸೆಟ್ಟಿಂಗ್‌ಗಳಲ್ಲಿ ಅನುಮತಿಸಿ.';

  @override
  String get locationPositionUnavailable =>
      '60 ಸೆಕೆಂಡುಗಳಲ್ಲಿ GPS ಸ್ಥಳ ಸಿಗಲಿಲ್ಲ. ಸಿಗ್ನಲ್ ಪರಿಶೀಲಿಸಿ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.';

  @override
  String get locationSettingsUnavailable =>
      'ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ತೆರೆಯಲಾಗಲಿಲ್ಲ. ಸಾಧನದ ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ತೆರೆಯಿರಿ ಮತ್ತು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.';

  @override
  String get openSettings => 'ಸೆಟ್ಟಿಂಗ್‌ಗಳನ್ನು ತೆರೆಯಿರಿ';

  @override
  String locationRequestFailed(String error) {
    return 'ನಿಮ್ಮ ಸ್ಥಳವನ್ನು ಪಡೆಯಲಾಗಲಿಲ್ಲ: $error';
  }

  @override
  String get scanSavedLocally => 'ಸ್ಕ್ಯಾನ್ ಈ ಸಾಧನದಲ್ಲಿ ಉಳಿಸಲಾಗಿದೆ.';

  @override
  String get diseaseHealthy => 'ಆರೋಗ್ಯಕರ ಸಸ್ಯ';

  @override
  String get diseaseBacterialSpot => 'ಬ್ಯಾಕ್ಟೀರಿಯಾ ಚುಕ್ಕೆ ರೋಗ';

  @override
  String get diseaseEarlyBlight => 'ಮುಂಚಿನ ಅಂಗಮಾರಿ';

  @override
  String get diseaseLateBlight => 'ತಡ ಅಂಗಮಾರಿ';

  @override
  String get diseaseLeafMold => 'ಎಲೆ ಬೂಷ್ಟು';

  @override
  String get diseaseSeptoriaLeafSpot => 'ಸೆಪ್ಟೋರಿಯಾ ಎಲೆ ಚುಕ್ಕೆ';

  @override
  String get diseaseSpiderMites => 'ಎರಡು ಚುಕ್ಕೆ ಜೇಡ ಹುಳ';

  @override
  String get diseaseTargetSpot => 'ಗುರಿ ಚುಕ್ಕೆ';

  @override
  String get diseaseYellowLeafCurlVirus => 'ಹಳದಿ ಎಲೆ ಮುದುಡು ವೈರಸ್';

  @override
  String get diseaseMosaicVirus => 'ಮೊಸಾಯಿಕ್ ವೈರಸ್';

  @override
  String get diseaseCommonRust => 'ಸಾಮಾನ್ಯ ತುಕ್ಕು ರೋಗ';

  @override
  String get diseaseNorthernLeafBlight => 'ಉತ್ತರ ಎಲೆ ಅಂಗಮಾರಿ';

  @override
  String get diseaseBrownSpot => 'ಕಂದು ಚುಕ್ಕೆ';

  @override
  String get diseaseLeafBlast => 'ಎಲೆ ಸಿಡಿತ ರೋಗ';

  @override
  String get authWelcomeTitle => 'AgroLens‌ಗೆ ಸ್ವಾಗತ';

  @override
  String get authWelcomeSubtitle =>
      'ನಿಮ್ಮ ಬೆಳೆಗಳ ಆರೈಕೆಯನ್ನು ಮುಂದುವರಿಸಲು ಸೈನ್ ಇನ್ ಮಾಡಿ.';

  @override
  String get authIdentifier => 'ಇಮೇಲ್ ಅಥವಾ ಬಳಕೆದಾರ ಹೆಸರು';

  @override
  String get authPassword => 'ಪಾಸ್‌ವರ್ಡ್';

  @override
  String get authConfirmPassword => 'ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ';

  @override
  String get authEmail => 'ಇಮೇಲ್';

  @override
  String get authUsername => 'ಬಳಕೆದಾರ ಹೆಸರು';

  @override
  String get authForgotPassword => 'ಪಾಸ್‌ವರ್ಡ್ ಮರೆತಿರಾ?';

  @override
  String get authLogin => 'ಲಾಗಿನ್';

  @override
  String get authSignUp => 'ಸೈನ್ ಅಪ್';

  @override
  String get authCreateAccount => 'ನಿಮ್ಮ ಖಾತೆ ರಚಿಸಿ';

  @override
  String get authNoAccount => 'AgroLens‌ಗೆ ಹೊಸಬರೇ?';

  @override
  String get authHaveAccount => 'ಈಗಾಗಲೇ ಖಾತೆ ಇದೆಯೇ?';

  @override
  String get authSendResetLink => 'ಮರುಹೊಂದಿಕೆ ಲಿಂಕ್ ಕಳುಹಿಸಿ';

  @override
  String get authResetPasswordTitle => 'ಪಾಸ್‌ವರ್ಡ್ ಮರುಹೊಂದಿಸಿ';

  @override
  String get authResetPasswordSubtitle =>
      'ಇಮೇಲ್ ನಮೂದಿಸಿ; ಖಾತೆ ಇದ್ದರೆ ಮರುಹೊಂದಿಕೆ ಲಿಂಕ್ ಕಳುಹಿಸುತ್ತೇವೆ.';

  @override
  String get authBackToLogin => 'ಲಾಗಿನ್‌ಗೆ ಹಿಂತಿರುಗಿ';

  @override
  String get authPasswordTooShort => 'ಕನಿಷ್ಠ 8 ಅಕ್ಷರಗಳನ್ನು ಬಳಸಿ.';

  @override
  String get authPasswordMismatch => 'ಪಾಸ್‌ವರ್ಡ್‌ಗಳು ಹೊಂದಿಕೆಯಾಗುತ್ತಿಲ್ಲ.';

  @override
  String get authEmailInvalid => 'ಮಾನ್ಯ ಇಮೇಲ್ ವಿಳಾಸ ನಮೂದಿಸಿ.';

  @override
  String get authUsernameRequired => 'ಬಳಕೆದಾರ ಹೆಸರನ್ನು ನಮೂದಿಸಿ.';

  @override
  String get authRequired => 'ಈ ಕ್ಷೇತ್ರ ಅಗತ್ಯವಿದೆ.';

  @override
  String get authUnexpectedError => 'ಏನೋ ತಪ್ಪಾಗಿದೆ. ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.';

  @override
  String get authResetSent =>
      'ಈ ಇಮೇಲ್‌ಗೆ ಖಾತೆ ಇದ್ದರೆ, ಮರುಹೊಂದಿಕೆ ಲಿಂಕ್ ಕಳುಹಿಸಲಾಗುತ್ತದೆ.';

  @override
  String get authLoggingIn => 'ಸೈನ್ ಇನ್ ಆಗುತ್ತಿದೆ…';

  @override
  String get authCreatingAccount => 'ಖಾತೆ ರಚಿಸಲಾಗುತ್ತಿದೆ…';

  @override
  String get authSendingReset => 'ಕಳುಹಿಸಲಾಗುತ್ತಿದೆ…';

  @override
  String get authShowPassword => 'ಪಾಸ್‌ವರ್ಡ್ ತೋರಿಸಿ';

  @override
  String get authHidePassword => 'ಪಾಸ್‌ವರ್ಡ್ ಮರೆಮಾಡಿ';

  @override
  String authLoggedInAs(String name) {
    return '$name ಆಗಿ ಸೈನ್ ಇನ್ ಆಗಿದ್ದೀರಿ';
  }

  @override
  String get authLogOut => 'ಲಾಗ್ ಔಟ್';
}
