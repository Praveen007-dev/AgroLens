import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_hi.dart';
import 'app_localizations_kn.dart';
import 'app_localizations_ta.dart';
import 'app_localizations_te.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('hi'),
    Locale('kn'),
    Locale('ta'),
    Locale('te')
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'AgroLens'**
  String get appTitle;

  /// No description provided for @languageLabel.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get languageLabel;

  /// No description provided for @languageEnglish.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get languageEnglish;

  /// No description provided for @languageHindi.
  ///
  /// In en, this message translates to:
  /// **'हिन्दी'**
  String get languageHindi;

  /// No description provided for @languageTelugu.
  ///
  /// In en, this message translates to:
  /// **'తెలుగు'**
  String get languageTelugu;

  /// No description provided for @languageTamil.
  ///
  /// In en, this message translates to:
  /// **'தமிழ்'**
  String get languageTamil;

  /// No description provided for @languageKannada.
  ///
  /// In en, this message translates to:
  /// **'ಕನ್ನಡ'**
  String get languageKannada;

  /// No description provided for @checkYourCrop.
  ///
  /// In en, this message translates to:
  /// **'A healthier harvest starts here'**
  String get checkYourCrop;

  /// No description provided for @scanIntroduction.
  ///
  /// In en, this message translates to:
  /// **'Photograph a leaf to check for visible crop health issues.'**
  String get scanIntroduction;

  /// No description provided for @plantNameLabel.
  ///
  /// In en, this message translates to:
  /// **'Plant or crop'**
  String get plantNameLabel;

  /// No description provided for @plantNameHint.
  ///
  /// In en, this message translates to:
  /// **'Type any plant name'**
  String get plantNameHint;

  /// No description provided for @plantNameRequired.
  ///
  /// In en, this message translates to:
  /// **'Enter the plant or crop name first.'**
  String get plantNameRequired;

  /// No description provided for @supportedCropsTitle.
  ///
  /// In en, this message translates to:
  /// **'Quick select'**
  String get supportedCropsTitle;

  /// No description provided for @modelCoverageNotice.
  ///
  /// In en, this message translates to:
  /// **'Any plant name can be entered. This demo uses simulated results, not image recognition. Its placeholder labels cover tomato, potato, corn, bell pepper, and rice only.'**
  String get modelCoverageNotice;

  /// No description provided for @cropNotSupported.
  ///
  /// In en, this message translates to:
  /// **'The demo cannot analyze {crop} yet. No diagnosis was made. Its placeholder labels cover tomato, potato, corn, bell pepper, and rice only.'**
  String cropNotSupported(String crop);

  /// No description provided for @demoModeNotice.
  ///
  /// In en, this message translates to:
  /// **'Demo mode: predictions are simulated and are not a diagnosis.'**
  String get demoModeNotice;

  /// No description provided for @cropLabel.
  ///
  /// In en, this message translates to:
  /// **'Crop'**
  String get cropLabel;

  /// No description provided for @cropTomato.
  ///
  /// In en, this message translates to:
  /// **'Tomato'**
  String get cropTomato;

  /// No description provided for @cropPotato.
  ///
  /// In en, this message translates to:
  /// **'Potato'**
  String get cropPotato;

  /// No description provided for @cropCorn.
  ///
  /// In en, this message translates to:
  /// **'Corn'**
  String get cropCorn;

  /// No description provided for @cropPepper.
  ///
  /// In en, this message translates to:
  /// **'Bell pepper'**
  String get cropPepper;

  /// No description provided for @cropRice.
  ///
  /// In en, this message translates to:
  /// **'Rice'**
  String get cropRice;

  /// No description provided for @choosePhoto.
  ///
  /// In en, this message translates to:
  /// **'Choose a photo'**
  String get choosePhoto;

  /// No description provided for @takePhoto.
  ///
  /// In en, this message translates to:
  /// **'Take a photo'**
  String get takePhoto;

  /// No description provided for @photoActionsHint.
  ///
  /// In en, this message translates to:
  /// **'Use a clear, well-lit photo of one affected leaf.'**
  String get photoActionsHint;

  /// No description provided for @photoSelected.
  ///
  /// In en, this message translates to:
  /// **'Photo selected'**
  String get photoSelected;

  /// No description provided for @analyzePhoto.
  ///
  /// In en, this message translates to:
  /// **'Analyze photo'**
  String get analyzePhoto;

  /// No description provided for @analyzing.
  ///
  /// In en, this message translates to:
  /// **'Analyzing...'**
  String get analyzing;

  /// No description provided for @errorCouldNotOpenPhoto.
  ///
  /// In en, this message translates to:
  /// **'Could not open the image: {error}'**
  String errorCouldNotOpenPhoto(String error);

  /// No description provided for @errorCouldNotAnalyzePhoto.
  ///
  /// In en, this message translates to:
  /// **'Could not analyze this image: {error}'**
  String errorCouldNotAnalyzePhoto(String error);

  /// No description provided for @errorCouldNotSaveScan.
  ///
  /// In en, this message translates to:
  /// **'The prediction is ready, but the scan could not be saved on this device: {error}'**
  String errorCouldNotSaveScan(String error);

  /// No description provided for @predictionTitle.
  ///
  /// In en, this message translates to:
  /// **'Prediction'**
  String get predictionTitle;

  /// No description provided for @resultSummary.
  ///
  /// In en, this message translates to:
  /// **'{crop} · {confidence} confidence'**
  String resultSummary(String crop, String confidence);

  /// No description provided for @lowConfidenceWarning.
  ///
  /// In en, this message translates to:
  /// **'Low confidence. Try a clearer photo and confirm the result with an agricultural expert.'**
  String get lowConfidenceWarning;

  /// No description provided for @modelVersion.
  ///
  /// In en, this message translates to:
  /// **'Model: {version}'**
  String modelVersion(String version);

  /// No description provided for @locationTitle.
  ///
  /// In en, this message translates to:
  /// **'Optional location'**
  String get locationTitle;

  /// No description provided for @locationPrivacyNotice.
  ///
  /// In en, this message translates to:
  /// **'Your location is only requested if you choose Add location. If added, coordinates are saved with this scan on this device.'**
  String get locationPrivacyNotice;

  /// No description provided for @addLocation.
  ///
  /// In en, this message translates to:
  /// **'Add location'**
  String get addLocation;

  /// No description provided for @removeLocation.
  ///
  /// In en, this message translates to:
  /// **'Remove location'**
  String get removeLocation;

  /// No description provided for @gettingLocation.
  ///
  /// In en, this message translates to:
  /// **'Getting location...'**
  String get gettingLocation;

  /// No description provided for @locationCoordinates.
  ///
  /// In en, this message translates to:
  /// **'Coordinates: {latitude}, {longitude}'**
  String locationCoordinates(String latitude, String longitude);

  /// No description provided for @locationServiceDisabled.
  ///
  /// In en, this message translates to:
  /// **'Location services are turned off. Turn them on and try again.'**
  String get locationServiceDisabled;

  /// No description provided for @locationPermissionDenied.
  ///
  /// In en, this message translates to:
  /// **'Location permission was denied. Allow location access to add a location to this scan.'**
  String get locationPermissionDenied;

  /// No description provided for @locationPermissionDeniedForever.
  ///
  /// In en, this message translates to:
  /// **'Location permission is blocked. Enable it in your browser or device settings to add a location.'**
  String get locationPermissionDeniedForever;

  /// No description provided for @locationRequestFailed.
  ///
  /// In en, this message translates to:
  /// **'Could not get your location: {error}'**
  String locationRequestFailed(String error);

  /// No description provided for @scanSavedLocally.
  ///
  /// In en, this message translates to:
  /// **'Scan saved on this device.'**
  String get scanSavedLocally;

  /// No description provided for @diseaseHealthy.
  ///
  /// In en, this message translates to:
  /// **'Healthy plant'**
  String get diseaseHealthy;

  /// No description provided for @diseaseBacterialSpot.
  ///
  /// In en, this message translates to:
  /// **'Bacterial spot'**
  String get diseaseBacterialSpot;

  /// No description provided for @diseaseEarlyBlight.
  ///
  /// In en, this message translates to:
  /// **'Early blight'**
  String get diseaseEarlyBlight;

  /// No description provided for @diseaseLateBlight.
  ///
  /// In en, this message translates to:
  /// **'Late blight'**
  String get diseaseLateBlight;

  /// No description provided for @diseaseLeafMold.
  ///
  /// In en, this message translates to:
  /// **'Leaf mold'**
  String get diseaseLeafMold;

  /// No description provided for @diseaseSeptoriaLeafSpot.
  ///
  /// In en, this message translates to:
  /// **'Septoria leaf spot'**
  String get diseaseSeptoriaLeafSpot;

  /// No description provided for @diseaseSpiderMites.
  ///
  /// In en, this message translates to:
  /// **'Two-spotted spider mite'**
  String get diseaseSpiderMites;

  /// No description provided for @diseaseTargetSpot.
  ///
  /// In en, this message translates to:
  /// **'Target spot'**
  String get diseaseTargetSpot;

  /// No description provided for @diseaseYellowLeafCurlVirus.
  ///
  /// In en, this message translates to:
  /// **'Yellow leaf curl virus'**
  String get diseaseYellowLeafCurlVirus;

  /// No description provided for @diseaseMosaicVirus.
  ///
  /// In en, this message translates to:
  /// **'Mosaic virus'**
  String get diseaseMosaicVirus;

  /// No description provided for @diseaseCommonRust.
  ///
  /// In en, this message translates to:
  /// **'Common rust'**
  String get diseaseCommonRust;

  /// No description provided for @diseaseNorthernLeafBlight.
  ///
  /// In en, this message translates to:
  /// **'Northern leaf blight'**
  String get diseaseNorthernLeafBlight;

  /// No description provided for @diseaseBrownSpot.
  ///
  /// In en, this message translates to:
  /// **'Brown spot'**
  String get diseaseBrownSpot;

  /// No description provided for @diseaseLeafBlast.
  ///
  /// In en, this message translates to:
  /// **'Leaf blast'**
  String get diseaseLeafBlast;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'hi', 'kn', 'ta', 'te'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'hi':
      return AppLocalizationsHi();
    case 'kn':
      return AppLocalizationsKn();
    case 'ta':
      return AppLocalizationsTa();
    case 'te':
      return AppLocalizationsTe();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
