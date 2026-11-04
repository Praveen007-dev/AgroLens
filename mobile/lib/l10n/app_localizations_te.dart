// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Telugu (`te`).
class AppLocalizationsTe extends AppLocalizations {
  AppLocalizationsTe([String locale = 'te']) : super(locale);

  @override
  String get appTitle => 'AgroLens';

  @override
  String get languageLabel => 'భాష';

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
  String get checkYourCrop => 'మంచి పంటకు ఇక్కడే ఆరంభం';

  @override
  String get scanIntroduction =>
      'పంటలో కనిపించే సమస్యలను పరిశీలించడానికి ఆకు ఫోటో తీయండి.';

  @override
  String get plantNameLabel => 'మొక్క లేదా పంట';

  @override
  String get plantNameHint => 'ఏ మొక్క పేరు అయినా టైప్ చేయండి';

  @override
  String get plantNameRequired => 'ముందుగా మొక్క లేదా పంట పేరును నమోదు చేయండి.';

  @override
  String get supportedCropsTitle => 'త్వరగా ఎంచుకోండి';

  @override
  String get modelCoverageNotice =>
      'ఏ మొక్క పేరు అయినా నమోదు చేయవచ్చు. ఈ డెమో ఫోటోను గుర్తించదు; అనుకరణ ఫలితాలను మాత్రమే చూపిస్తుంది. దీని నమూనా లేబుళ్లు టమాటా, బంగాళాదుంప, మొక్కజొన్న, క్యాప్సికం, వరికి మాత్రమే ఉన్నాయి.';

  @override
  String cropNotSupported(String crop) {
    return 'ఈ డెమో $cropను విశ్లేషించలేకపోతుంది. ఎలాంటి నిర్ధారణ చేయలేదు. దీని నమూనా లేబుళ్లు టమాటా, బంగాళాదుంప, మొక్కజొన్న, క్యాప్సికం, వరికి మాత్రమే ఉన్నాయి.';
  }

  @override
  String get demoModeNotice =>
      'డెమో మోడ్: అంచనాలు అనుకరణ మాత్రమే, ఇవి నిర్ధారణ కాదు.';

  @override
  String get cropLabel => 'పంట';

  @override
  String get cropTomato => 'టమాటా';

  @override
  String get cropPotato => 'బంగాళాదుంప';

  @override
  String get cropCorn => 'మొక్కజొన్న';

  @override
  String get cropPepper => 'క్యాప్సికం';

  @override
  String get cropRice => 'వరి';

  @override
  String get choosePhoto => 'ఫోటోను ఎంచుకోండి';

  @override
  String get takePhoto => 'ఫోటో తీయండి';

  @override
  String get photoActionsHint =>
      'దెబ్బతిన్న ఒక ఆకును స్పష్టమైన వెలుతురులో ఫోటో తీయండి.';

  @override
  String get photoSelected => 'ఫోటో ఎంచుకోబడింది';

  @override
  String get analyzePhoto => 'ఫోటోను విశ్లేషించండి';

  @override
  String get analyzing => 'విశ్లేషిస్తోంది...';

  @override
  String errorCouldNotOpenPhoto(String error) {
    return 'ఫోటోను తెరవలేకపోయాము: $error';
  }

  @override
  String errorCouldNotAnalyzePhoto(String error) {
    return 'ఈ ఫోటోను విశ్లేషించలేకపోయాము: $error';
  }

  @override
  String errorCouldNotSaveScan(String error) {
    return 'అంచనా సిద్ధంగా ఉంది, కానీ స్కాన్‌ను ఈ పరికరంలో సేవ్ చేయలేకపోయాము: $error';
  }

  @override
  String get predictionTitle => 'అంచనా';

  @override
  String resultSummary(String crop, String confidence) {
    return '$crop · నమ్మక స్థాయి $confidence';
  }

  @override
  String get lowConfidenceWarning =>
      'నమ్మక స్థాయి తక్కువగా ఉంది. స్పష్టమైన ఫోటో తీసి వ్యవసాయ నిపుణుడితో ఫలితాన్ని నిర్ధారించండి.';

  @override
  String modelVersion(String version) {
    return 'మోడల్: $version';
  }

  @override
  String get locationTitle => 'ఐచ్ఛిక స్థానం';

  @override
  String get locationPrivacyNotice =>
      'మీరు స్థానం జోడించండి ఎంచుకున్నప్పుడే మీ స్థానాన్ని అడుగుతాము. జోడించిన కోఆర్డినేట్లు ఈ పరికరంలో ఈ స్కాన్‌తో సేవ్ అవుతాయి.';

  @override
  String get addLocation => 'స్థానాన్ని జోడించండి';

  @override
  String get removeLocation => 'స్థానాన్ని తొలగించండి';

  @override
  String get gettingLocation => 'స్థానాన్ని పొందుతోంది...';

  @override
  String locationCoordinates(String latitude, String longitude) {
    return 'కోఆర్డినేట్లు: $latitude, $longitude';
  }

  @override
  String get locationServiceDisabled =>
      'స్థాన సేవలు ఆఫ్‌లో ఉన్నాయి. వాటిని ఆన్ చేసి మళ్లీ ప్రయత్నించండి.';

  @override
  String get locationPermissionDenied =>
      'స్థాన అనుమతి నిరాకరించబడింది. ఈ స్కాన్‌కు స్థానం జోడించడానికి అనుమతించండి.';

  @override
  String get locationPermissionDeniedForever =>
      'స్థాన అనుమతి బ్లాక్ చేయబడింది. స్థానం జోడించడానికి బ్రౌజర్ లేదా పరికర సెట్టింగ్‌లలో అనుమతించండి.';

  @override
  String locationRequestFailed(String error) {
    return 'మీ స్థానాన్ని పొందలేకపోయాము: $error';
  }

  @override
  String get scanSavedLocally => 'స్కాన్ ఈ పరికరంలో సేవ్ చేయబడింది.';

  @override
  String get diseaseHealthy => 'ఆరోగ్యకరమైన మొక్క';

  @override
  String get diseaseBacterialSpot => 'బాక్టీరియా మచ్చ';

  @override
  String get diseaseEarlyBlight => 'ముందస్తు ఎండు తెగులు';

  @override
  String get diseaseLateBlight => 'ఆలస్యపు ఎండు తెగులు';

  @override
  String get diseaseLeafMold => 'ఆకు బూజు';

  @override
  String get diseaseSeptoriaLeafSpot => 'సెప్టోరియా ఆకు మచ్చ';

  @override
  String get diseaseSpiderMites => 'రెండు మచ్చల సాలీడు పురుగు';

  @override
  String get diseaseTargetSpot => 'లక్ష్యాకారపు మచ్చ';

  @override
  String get diseaseYellowLeafCurlVirus => 'పసుపు ఆకు ముడత వైరస్';

  @override
  String get diseaseMosaicVirus => 'మొజాయిక్ వైరస్';

  @override
  String get diseaseCommonRust => 'సాధారణ తుప్పు తెగులు';

  @override
  String get diseaseNorthernLeafBlight => 'ఉత్తర ఆకు ఎండు తెగులు';

  @override
  String get diseaseBrownSpot => 'గోధుమ మచ్చ';

  @override
  String get diseaseLeafBlast => 'ఆకు అగ్గి తెగులు';
}
