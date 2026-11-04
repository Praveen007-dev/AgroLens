// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Tamil (`ta`).
class AppLocalizationsTa extends AppLocalizations {
  AppLocalizationsTa([String locale = 'ta']) : super(locale);

  @override
  String get appTitle => 'AgroLens';

  @override
  String get languageLabel => 'மொழி';

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
  String get checkYourCrop => 'நல்ல அறுவடைக்கான முதல் படி';

  @override
  String get scanIntroduction =>
      'பயிரில் தெரியும் சிக்கல்களைச் சரிபார்க்க இலையைப் படம் எடுக்கவும்.';

  @override
  String get plantNameLabel => 'தாவரம் அல்லது பயிர்';

  @override
  String get plantNameHint => 'எந்தத் தாவரத்தின் பெயரையும் உள்ளிடவும்';

  @override
  String get plantNameRequired =>
      'முதலில் தாவரம் அல்லது பயிரின் பெயரை உள்ளிடவும்.';

  @override
  String get supportedCropsTitle => 'விரைவுத் தேர்வு';

  @override
  String get modelCoverageNotice =>
      'எந்தத் தாவரத்தின் பெயரையும் உள்ளிடலாம். இந்தச் செயல்விளக்கம் படத்தை அடையாளம் காணாது; உருவகப்படுத்தப்பட்ட முடிவுகளை மட்டுமே காட்டும். இதன் மாதிரி லேபிள்கள் தக்காளி, உருளைக்கிழங்கு, மக்காச்சோளம், குடைமிளகாய் மற்றும் நெல்லுக்கு மட்டுமே உள்ளன.';

  @override
  String cropNotSupported(String crop) {
    return 'இந்தச் செயல்விளக்கத்தால் $cropஐப் பகுப்பாய்வு செய்ய முடியாது. நோயறிதல் செய்யப்படவில்லை. இதன் மாதிரி லேபிள்கள் தக்காளி, உருளைக்கிழங்கு, மக்காச்சோளம், குடைமிளகாய் மற்றும் நெல்லுக்கு மட்டுமே உள்ளன.';
  }

  @override
  String get demoModeNotice =>
      'செயல்விளக்க முறை: கணிப்புகள் உருவகப்படுத்தப்பட்டவை; இவை நோயறிதல் அல்ல.';

  @override
  String get cropLabel => 'பயிர்';

  @override
  String get cropTomato => 'தக்காளி';

  @override
  String get cropPotato => 'உருளைக்கிழங்கு';

  @override
  String get cropCorn => 'மக்காச்சோளம்';

  @override
  String get cropPepper => 'குடைமிளகாய்';

  @override
  String get cropRice => 'நெல்';

  @override
  String get choosePhoto => 'படத்தைத் தேர்ந்தெடுக்கவும்';

  @override
  String get takePhoto => 'படம் எடுக்கவும்';

  @override
  String get photoActionsHint =>
      'பாதிக்கப்பட்ட ஒரு இலையைத் தெளிவான வெளிச்சத்தில் படம் எடுக்கவும்.';

  @override
  String get photoSelected => 'படம் தேர்ந்தெடுக்கப்பட்டது';

  @override
  String get analyzePhoto => 'படத்தைப் பகுப்பாய்வு செய்யவும்';

  @override
  String get analyzing => 'பகுப்பாய்வு செய்கிறது...';

  @override
  String errorCouldNotOpenPhoto(String error) {
    return 'படத்தைத் திறக்க முடியவில்லை: $error';
  }

  @override
  String errorCouldNotAnalyzePhoto(String error) {
    return 'இந்தப் படத்தைப் பகுப்பாய்வு செய்ய முடியவில்லை: $error';
  }

  @override
  String errorCouldNotSaveScan(String error) {
    return 'கணிப்பு தயார், ஆனால் இந்தச் சாதனத்தில் பதிவைச் சேமிக்க முடியவில்லை: $error';
  }

  @override
  String get predictionTitle => 'கணிப்பு';

  @override
  String resultSummary(String crop, String confidence) {
    return '$crop · நம்பிக்கை $confidence';
  }

  @override
  String get lowConfidenceWarning =>
      'நம்பிக்கை குறைவாக உள்ளது. தெளிவான படத்தை எடுத்து வேளாண் நிபுணரிடம் முடிவை உறுதிப்படுத்தவும்.';

  @override
  String modelVersion(String version) {
    return 'மாதிரி: $version';
  }

  @override
  String get locationTitle => 'விருப்ப இடம்';

  @override
  String get locationPrivacyNotice =>
      'இடத்தைச் சேர் என்பதைத் தேர்ந்தெடுத்தால் மட்டுமே உங்கள் இருப்பிடம் கேட்கப்படும். சேர்க்கப்படும் ஆயத்தொலைவுகள் இந்தச் சாதனத்தில் இந்தப் பதிவுடன் சேமிக்கப்படும்.';

  @override
  String get addLocation => 'இடத்தைச் சேர்க்கவும்';

  @override
  String get removeLocation => 'இடத்தை நீக்கவும்';

  @override
  String get gettingLocation => 'இருப்பிடத்தைப் பெறுகிறது...';

  @override
  String locationCoordinates(String latitude, String longitude) {
    return 'ஆயத்தொலைவுகள்: $latitude, $longitude';
  }

  @override
  String get locationServiceDisabled =>
      'இருப்பிடச் சேவைகள் முடக்கப்பட்டுள்ளன. அவற்றை இயக்கி மீண்டும் முயற்சிக்கவும்.';

  @override
  String get locationPermissionDenied =>
      'இருப்பிட அனுமதி மறுக்கப்பட்டது. இந்தப் பதிவில் இடத்தைச் சேர்க்க அனுமதி வழங்கவும்.';

  @override
  String get locationPermissionDeniedForever =>
      'இருப்பிட அனுமதி தடுக்கப்பட்டுள்ளது. இடத்தைச் சேர்க்க உலாவி அல்லது சாதன அமைப்புகளில் அனுமதிக்கவும்.';

  @override
  String locationRequestFailed(String error) {
    return 'உங்கள் இருப்பிடத்தைப் பெற முடியவில்லை: $error';
  }

  @override
  String get scanSavedLocally => 'பதிவு இந்தச் சாதனத்தில் சேமிக்கப்பட்டது.';

  @override
  String get diseaseHealthy => 'ஆரோக்கியமான செடி';

  @override
  String get diseaseBacterialSpot => 'பாக்டீரியா புள்ளி நோய்';

  @override
  String get diseaseEarlyBlight => 'முன்பருவ கருகல் நோய்';

  @override
  String get diseaseLateBlight => 'பின்பருவ கருகல் நோய்';

  @override
  String get diseaseLeafMold => 'இலைப் பூஞ்சை';

  @override
  String get diseaseSeptoriaLeafSpot => 'செப்டோரியா இலைப் புள்ளி';

  @override
  String get diseaseSpiderMites => 'இரு புள்ளி சிலந்திப் பூச்சி';

  @override
  String get diseaseTargetSpot => 'இலக்கு வடிவப் புள்ளி';

  @override
  String get diseaseYellowLeafCurlVirus => 'மஞ்சள் இலை சுருள் வைரஸ்';

  @override
  String get diseaseMosaicVirus => 'மொசைக் வைரஸ்';

  @override
  String get diseaseCommonRust => 'பொதுத் துரு நோய்';

  @override
  String get diseaseNorthernLeafBlight => 'வடக்கு இலைக் கருகல்';

  @override
  String get diseaseBrownSpot => 'பழுப்புப் புள்ளி நோய்';

  @override
  String get diseaseLeafBlast => 'இலைக் கருகல் நோய்';
}
