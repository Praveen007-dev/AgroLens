// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Hindi (`hi`).
class AppLocalizationsHi extends AppLocalizations {
  AppLocalizationsHi([String locale = 'hi']) : super(locale);

  @override
  String get appTitle => 'AgroLens';

  @override
  String get languageLabel => 'भाषा';

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
  String get checkYourCrop => 'बेहतर फसल की शुरुआत यहाँ से';

  @override
  String get scanIntroduction =>
      'फसल की दिखाई देने वाली समस्याएँ जाँचने के लिए पत्ती की तस्वीर लें।';

  @override
  String get plantNameLabel => 'पौधा या फसल';

  @override
  String get plantNameHint => 'किसी भी पौधे का नाम लिखें';

  @override
  String get plantNameRequired => 'पहले पौधे या फसल का नाम लिखें।';

  @override
  String get supportedCropsTitle => 'जल्दी चुनें';

  @override
  String get modelCoverageNotice =>
      'किसी भी पौधे का नाम लिख सकते हैं। यह डेमो तस्वीर पहचानता नहीं, केवल सिम्युलेटेड परिणाम दिखाता है। इसके नमूना लेबल केवल टमाटर, आलू, मक्का, शिमला मिर्च और धान के लिए हैं।';

  @override
  String cropNotSupported(String crop) {
    return 'डेमो अभी $crop का विश्लेषण नहीं कर सकता। कोई निदान नहीं किया गया। इसके नमूना लेबल केवल टमाटर, आलू, मक्का, शिमला मिर्च और धान के लिए हैं।';
  }

  @override
  String get demoModeNotice =>
      'डेमो मोड: अनुमान सिम्युलेटेड हैं, यह निदान नहीं है।';

  @override
  String get cropLabel => 'फसल';

  @override
  String get cropTomato => 'टमाटर';

  @override
  String get cropPotato => 'आलू';

  @override
  String get cropCorn => 'मक्का';

  @override
  String get cropPepper => 'शिमला मिर्च';

  @override
  String get cropRice => 'धान';

  @override
  String get choosePhoto => 'तस्वीर चुनें';

  @override
  String get takePhoto => 'तस्वीर लें';

  @override
  String get photoActionsHint =>
      'प्रभावित पत्ती की साफ़ और अच्छी रोशनी वाली तस्वीर लें।';

  @override
  String get photoSelected => 'तस्वीर चुनी गई';

  @override
  String get analyzePhoto => 'तस्वीर का विश्लेषण करें';

  @override
  String get analyzing => 'विश्लेषण हो रहा है...';

  @override
  String errorCouldNotOpenPhoto(String error) {
    return 'तस्वीर नहीं खुल सकी: $error';
  }

  @override
  String errorCouldNotAnalyzePhoto(String error) {
    return 'तस्वीर का विश्लेषण नहीं हो सका: $error';
  }

  @override
  String errorCouldNotSaveScan(String error) {
    return 'अनुमान तैयार है, लेकिन स्कैन इस डिवाइस पर सहेजा नहीं जा सका: $error';
  }

  @override
  String get predictionTitle => 'अनुमान';

  @override
  String resultSummary(String crop, String confidence) {
    return '$crop · विश्वास स्तर $confidence';
  }

  @override
  String get lowConfidenceWarning =>
      'विश्वास स्तर कम है। साफ़ तस्वीर लें और कृषि विशेषज्ञ से परिणाम की पुष्टि करें।';

  @override
  String modelVersion(String version) {
    return 'मॉडल: $version';
  }

  @override
  String get locationTitle => 'वैकल्पिक स्थान';

  @override
  String get locationPrivacyNotice =>
      'आपका स्थान केवल तभी माँगा जाएगा जब आप स्थान जोड़ें चुनेंगे। जोड़े गए निर्देशांक इस डिवाइस पर इस स्कैन के साथ सहेजे जाएँगे।';

  @override
  String get addLocation => 'स्थान जोड़ें';

  @override
  String get removeLocation => 'स्थान हटाएँ';

  @override
  String get gettingLocation => 'स्थान प्राप्त हो रहा है...';

  @override
  String locationCoordinates(String latitude, String longitude) {
    return 'निर्देशांक: $latitude, $longitude';
  }

  @override
  String get locationServiceDisabled =>
      'स्थान सेवाएँ बंद हैं। उन्हें चालू करके फिर कोशिश करें।';

  @override
  String get locationPermissionDenied =>
      'स्थान की अनुमति नहीं मिली। इस स्कैन में स्थान जोड़ने के लिए अनुमति दें।';

  @override
  String get locationPermissionDeniedForever =>
      'स्थान की अनुमति ब्लॉक है। स्थान जोड़ने के लिए ब्राउज़र या डिवाइस सेटिंग में अनुमति दें।';

  @override
  String locationRequestFailed(String error) {
    return 'स्थान प्राप्त नहीं हो सका: $error';
  }

  @override
  String get scanSavedLocally => 'स्कैन इस डिवाइस पर सहेजा गया।';

  @override
  String get diseaseHealthy => 'स्वस्थ पौधा';

  @override
  String get diseaseBacterialSpot => 'जीवाणु धब्बा रोग';

  @override
  String get diseaseEarlyBlight => 'अगेती झुलसा';

  @override
  String get diseaseLateBlight => 'पछेती झुलसा';

  @override
  String get diseaseLeafMold => 'पत्ती फफूंद';

  @override
  String get diseaseSeptoriaLeafSpot => 'सेप्टोरिया पत्ती धब्बा';

  @override
  String get diseaseSpiderMites => 'दो-धब्बों वाला मकड़ी घुन';

  @override
  String get diseaseTargetSpot => 'लक्ष्याकार धब्बा';

  @override
  String get diseaseYellowLeafCurlVirus => 'पीली पत्ती मोड़क विषाणु';

  @override
  String get diseaseMosaicVirus => 'मोज़ेक विषाणु';

  @override
  String get diseaseCommonRust => 'सामान्य रतुआ';

  @override
  String get diseaseNorthernLeafBlight => 'उत्तरी पत्ती झुलसा';

  @override
  String get diseaseBrownSpot => 'भूरा धब्बा';

  @override
  String get diseaseLeafBlast => 'पत्ती झुलसा';
}
