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
  /// **'Farm location'**
  String get locationTitle;

  /// No description provided for @locationPrivacyNotice.
  ///
  /// In en, this message translates to:
  /// **'Required for every scan. Your location is only requested when you tap the button and is saved with the scan on this device.'**
  String get locationPrivacyNotice;

  /// No description provided for @requiredLabel.
  ///
  /// In en, this message translates to:
  /// **'Required'**
  String get requiredLabel;

  /// No description provided for @readyLabel.
  ///
  /// In en, this message translates to:
  /// **'Ready'**
  String get readyLabel;

  /// No description provided for @addLocation.
  ///
  /// In en, this message translates to:
  /// **'Use my location'**
  String get addLocation;

  /// No description provided for @updateLocation.
  ///
  /// In en, this message translates to:
  /// **'Update location'**
  String get updateLocation;

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

  /// No description provided for @locationRequired.
  ///
  /// In en, this message translates to:
  /// **'Set your farm location before analyzing a crop.'**
  String get locationRequired;

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
  /// **'Location permission was denied. Allow location access to continue with a scan.'**
  String get locationPermissionDenied;

  /// No description provided for @locationPermissionDeniedForever.
  ///
  /// In en, this message translates to:
  /// **'Location permission is blocked. Enable it in your browser or device settings to scan.'**
  String get locationPermissionDeniedForever;

  /// No description provided for @locationPositionUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Could not get a GPS fix within 60 seconds. Check your signal and try again.'**
  String get locationPositionUnavailable;

  /// No description provided for @locationSettingsUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Could not open settings. Open your device settings manually and try again.'**
  String get locationSettingsUnavailable;

  /// No description provided for @openSettings.
  ///
  /// In en, this message translates to:
  /// **'Open settings'**
  String get openSettings;

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

  /// No description provided for @authWelcomeTitle.
  ///
  /// In en, this message translates to:
  /// **'Welcome to AgroLens'**
  String get authWelcomeTitle;

  /// No description provided for @authWelcomeSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Sign in to continue caring for your crops.'**
  String get authWelcomeSubtitle;

  /// No description provided for @authIdentifier.
  ///
  /// In en, this message translates to:
  /// **'Email or username'**
  String get authIdentifier;

  /// No description provided for @authPassword.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get authPassword;

  /// No description provided for @authConfirmPassword.
  ///
  /// In en, this message translates to:
  /// **'Confirm password'**
  String get authConfirmPassword;

  /// No description provided for @authEmail.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get authEmail;

  /// No description provided for @authUsername.
  ///
  /// In en, this message translates to:
  /// **'Username'**
  String get authUsername;

  /// No description provided for @authForgotPassword.
  ///
  /// In en, this message translates to:
  /// **'Forgot password?'**
  String get authForgotPassword;

  /// No description provided for @authLogin.
  ///
  /// In en, this message translates to:
  /// **'Log in'**
  String get authLogin;

  /// No description provided for @authSignUp.
  ///
  /// In en, this message translates to:
  /// **'Sign up'**
  String get authSignUp;

  /// No description provided for @authCreateAccount.
  ///
  /// In en, this message translates to:
  /// **'Create your account'**
  String get authCreateAccount;

  /// No description provided for @authNoAccount.
  ///
  /// In en, this message translates to:
  /// **'New to AgroLens?'**
  String get authNoAccount;

  /// No description provided for @authHaveAccount.
  ///
  /// In en, this message translates to:
  /// **'Already have an account?'**
  String get authHaveAccount;

  /// No description provided for @authSendResetLink.
  ///
  /// In en, this message translates to:
  /// **'Send reset link'**
  String get authSendResetLink;

  /// No description provided for @authResetPasswordTitle.
  ///
  /// In en, this message translates to:
  /// **'Reset your password'**
  String get authResetPasswordTitle;

  /// No description provided for @authResetPasswordSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Enter your email and we’ll send a reset link if an account matches.'**
  String get authResetPasswordSubtitle;

  /// No description provided for @authBackToLogin.
  ///
  /// In en, this message translates to:
  /// **'Back to log in'**
  String get authBackToLogin;

  /// No description provided for @authPasswordTooShort.
  ///
  /// In en, this message translates to:
  /// **'Use at least 8 characters.'**
  String get authPasswordTooShort;

  /// No description provided for @authPasswordMismatch.
  ///
  /// In en, this message translates to:
  /// **'Passwords do not match.'**
  String get authPasswordMismatch;

  /// No description provided for @authEmailInvalid.
  ///
  /// In en, this message translates to:
  /// **'Enter a valid email address.'**
  String get authEmailInvalid;

  /// No description provided for @authUsernameRequired.
  ///
  /// In en, this message translates to:
  /// **'Enter a username.'**
  String get authUsernameRequired;

  /// No description provided for @authRequired.
  ///
  /// In en, this message translates to:
  /// **'This field is required.'**
  String get authRequired;

  /// No description provided for @authUnexpectedError.
  ///
  /// In en, this message translates to:
  /// **'Something went wrong. Please try again.'**
  String get authUnexpectedError;

  /// No description provided for @authResetSent.
  ///
  /// In en, this message translates to:
  /// **'If an account matches that email, a password reset link is on its way.'**
  String get authResetSent;

  /// No description provided for @authLoggingIn.
  ///
  /// In en, this message translates to:
  /// **'Signing in…'**
  String get authLoggingIn;

  /// No description provided for @authCreatingAccount.
  ///
  /// In en, this message translates to:
  /// **'Creating account…'**
  String get authCreatingAccount;

  /// No description provided for @authSendingReset.
  ///
  /// In en, this message translates to:
  /// **'Sending…'**
  String get authSendingReset;

  /// No description provided for @authShowPassword.
  ///
  /// In en, this message translates to:
  /// **'Show password'**
  String get authShowPassword;

  /// No description provided for @authHidePassword.
  ///
  /// In en, this message translates to:
  /// **'Hide password'**
  String get authHidePassword;

  /// No description provided for @authLoggedInAs.
  ///
  /// In en, this message translates to:
  /// **'Signed in as {name}'**
  String authLoggedInAs(String name);

  /// No description provided for @authLogOut.
  ///
  /// In en, this message translates to:
  /// **'Log out'**
  String get authLogOut;
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
