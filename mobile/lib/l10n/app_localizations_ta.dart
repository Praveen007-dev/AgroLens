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
  String get locationTitle => 'பண்ணை இருப்பிடம்';

  @override
  String get locationPrivacyNotice =>
      'ஒவ்வொரு பதிவுக்கும் இருப்பிடம் அவசியம். பொத்தானைத் தட்டினால் மட்டுமே இருப்பிடம் கேட்கப்படும்; அது இந்தச் சாதனத்தில் பதிவுடன் சேமிக்கப்படும்.';

  @override
  String get requiredLabel => 'அவசியம்';

  @override
  String get readyLabel => 'தயார்';

  @override
  String get addLocation => 'எனது இருப்பிடத்தைப் பயன்படுத்து';

  @override
  String get updateLocation => 'இருப்பிடத்தைப் புதுப்பி';

  @override
  String get removeLocation => 'இடத்தை நீக்கவும்';

  @override
  String get gettingLocation => 'இருப்பிடத்தைப் பெறுகிறது...';

  @override
  String get locationRequired =>
      'பயிரைப் பகுப்பாய்வு செய்வதற்கு முன் பண்ணை இருப்பிடத்தை அமைக்கவும்.';

  @override
  String locationCoordinates(String latitude, String longitude) {
    return 'ஆயத்தொலைவுகள்: $latitude, $longitude';
  }

  @override
  String get locationServiceDisabled =>
      'இருப்பிடச் சேவைகள் முடக்கப்பட்டுள்ளன. அவற்றை இயக்கி மீண்டும் முயற்சிக்கவும்.';

  @override
  String get locationPermissionDenied =>
      'இருப்பிட அனுமதி மறுக்கப்பட்டது. பதிவைத் தொடர இருப்பிட அனுமதி வழங்கவும்.';

  @override
  String get locationPermissionDeniedForever =>
      'இருப்பிட அனுமதி தடுக்கப்பட்டுள்ளது. படம் எடுக்க உலாவி அல்லது சாதன அமைப்புகளில் அனுமதிக்கவும்.';

  @override
  String get locationPositionUnavailable =>
      '60 விநாடிகளில் GPS இருப்பிடத்தைப் பெற முடியவில்லை. சிக்னலைச் சரிபார்த்து மீண்டும் முயற்சிக்கவும்.';

  @override
  String get locationSettingsUnavailable =>
      'அமைப்புகளைத் திறக்க முடியவில்லை. சாதன அமைப்புகளைத் திறந்து மீண்டும் முயற்சிக்கவும்.';

  @override
  String get openSettings => 'அமைப்புகளைத் திற';

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

  @override
  String get authWelcomeTitle => 'AgroLens-க்கு வரவேற்கிறோம்';

  @override
  String get authWelcomeSubtitle => 'பயிர்களைப் பராமரிக்கத் தொடர உள்நுழையவும்.';

  @override
  String get authIdentifier => 'மின்னஞ்சல் அல்லது பயனர் பெயர்';

  @override
  String get authPassword => 'கடவுச்சொல்';

  @override
  String get authConfirmPassword => 'கடவுச்சொல்லை உறுதிப்படுத்தவும்';

  @override
  String get authEmail => 'மின்னஞ்சல்';

  @override
  String get authUsername => 'பயனர் பெயர்';

  @override
  String get authForgotPassword => 'கடவுச்சொல் மறந்துவிட்டதா?';

  @override
  String get authLogin => 'உள்நுழை';

  @override
  String get authSignUp => 'பதிவு செய்';

  @override
  String get authCreateAccount => 'கணக்கை உருவாக்கவும்';

  @override
  String get authNoAccount => 'AgroLens-க்கு புதியவரா?';

  @override
  String get authHaveAccount => 'ஏற்கனவே கணக்கு உள்ளதா?';

  @override
  String get authSendResetLink => 'மீட்டமைப்பு இணைப்பை அனுப்பு';

  @override
  String get authResetPasswordTitle => 'கடவுச்சொல்லை மீட்டமை';

  @override
  String get authResetPasswordSubtitle =>
      'மின்னஞ்சலை உள்ளிடவும்; கணக்கு இருந்தால் மீட்டமைப்பு இணைப்பு அனுப்பப்படும்.';

  @override
  String get authBackToLogin => 'உள்நுழைவுக்குத் திரும்பு';

  @override
  String get authPasswordTooShort => 'குறைந்தது 8 எழுத்துகள் பயன்படுத்தவும்.';

  @override
  String get authPasswordMismatch => 'கடவுச்சொற்கள் பொருந்தவில்லை.';

  @override
  String get authEmailInvalid => 'சரியான மின்னஞ்சல் முகவரியை உள்ளிடவும்.';

  @override
  String get authUsernameRequired => 'பயனர் பெயரை உள்ளிடவும்.';

  @override
  String get authRequired => 'இந்தப் புலம் அவசியம்.';

  @override
  String get authUnexpectedError =>
      'ஏதோ தவறு ஏற்பட்டது. மீண்டும் முயற்சிக்கவும்.';

  @override
  String get authResetSent =>
      'இந்த மின்னஞ்சலுக்கு கணக்கு இருந்தால், மீட்டமைப்பு இணைப்பு அனுப்பப்படும்.';

  @override
  String get authLoggingIn => 'உள்நுழைகிறது…';

  @override
  String get authCreatingAccount => 'கணக்கு உருவாக்கப்படுகிறது…';

  @override
  String get authSendingReset => 'அனுப்புகிறது…';

  @override
  String get authShowPassword => 'கடவுச்சொல்லைக் காட்டு';

  @override
  String get authHidePassword => 'கடவுச்சொல்லை மறை';

  @override
  String authLoggedInAs(String name) {
    return '$name ஆக உள்நுழைந்துள்ளீர்கள்';
  }

  @override
  String get authLogOut => 'வெளியேறு';
}
