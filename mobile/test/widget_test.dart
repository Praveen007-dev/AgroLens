import 'dart:async';

import 'package:agrolens/main.dart';
import 'package:agrolens/models/inference_result.dart';
import 'package:agrolens/models/scan_record.dart';
import 'package:agrolens/services/location_service.dart';
import 'package:agrolens/services/auth_service.dart';
import 'package:agrolens/services/local_auth_service.dart';
import 'package:agrolens/services/mock_inference_service.dart';
import 'package:agrolens/services/storage_service.dart';
import 'package:flutter/material.dart'
    show
        ChoiceChip,
        CircularProgressIndicator,
        EditableText,
        FilledButton,
        Key,
        ListView,
        Scrollable,
        SliverChildListDelegate;
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _FakeLocationService extends LocationService {
  int requestCount = 0;

  @override
  Future<ScanLocation> getCurrentLocation() async {
    requestCount++;
    return const ScanLocation(
      latitude: 12.9716,
      longitude: 77.5946,
      hasConsent: true,
    );
  }
}

class _DeniedLocationService extends LocationService {
  @override
  Future<ScanLocation> getCurrentLocation() async {
    throw const LocationServiceException(LocationFailure.permissionDenied);
  }
}

class _LocationFailureService extends LocationService {
  _LocationFailureService(this.failure);

  final LocationFailure failure;
  int appSettingsRequests = 0;
  int locationSettingsRequests = 0;

  @override
  Future<ScanLocation> getCurrentLocation() async {
    throw LocationServiceException(failure);
  }

  @override
  Future<bool> openAppSettings() async {
    appSettingsRequests++;
    return true;
  }

  @override
  Future<bool> openLocationSettings() async {
    locationSettingsRequests++;
    return true;
  }
}

class _AuthenticatedAuthService implements AuthService {
  @override
  Future<AuthSession?> restoreSession() async =>
      const AuthSession(email: 'farmer@example.test', username: 'Test Farmer');

  @override
  Future<AuthSession> login({
    required String identifier,
    required String password,
  }) async =>
      const AuthSession(email: 'farmer@example.test', username: 'Test Farmer');

  @override
  Future<AuthSession> signUp({
    required String username,
    required String email,
    required String password,
  }) async =>
      AuthSession(email: email, username: username);

  @override
  Future<void> signOut() async {}
}

class _SignedOutAuthService implements AuthService {
  bool failLogin = false;
  Completer<AuthSession>? pendingLogin;
  int loginRequests = 0;
  int signUpRequests = 0;
  int signOutRequests = 0;

  @override
  Future<AuthSession?> restoreSession() async => null;

  @override
  Future<AuthSession> login({
    required String identifier,
    required String password,
  }) async {
    loginRequests++;
    if (failLogin) throw const AuthException('Invalid credentials.');
    if (pendingLogin case final pending?) return pending.future;
    return AuthSession(email: identifier, username: identifier);
  }

  @override
  Future<AuthSession> signUp({
    required String username,
    required String email,
    required String password,
  }) async {
    signUpRequests++;
    return AuthSession(
      email: email,
      username: username,
    );
  }

  @override
  Future<void> signOut() async {
    signOutRequests++;
  }
}

Future<void> _pumpSignedInApp(
  WidgetTester tester, {
  LocationService? locationService,
}) async {
  await tester.pumpWidget(
    AgroLensApp(
      authService: _AuthenticatedAuthService(),
      locationService: locationService,
    ),
  );
  await tester.pumpAndSettle();
}

Future<void> _scrollTo(WidgetTester tester, Finder finder) async {
  for (var attempt = 0; attempt < 8; attempt++) {
    if (finder.evaluate().isNotEmpty) {
      await tester.ensureVisible(finder);
      await tester.pumpAndSettle();
      return;
    }
    await tester.drag(find.byType(Scrollable).first, const Offset(0, -450));
    await tester.pumpAndSettle();
  }
  expect(finder, findsOneWidget);
}

void main() {
  testWidgets('login validates inputs, toggles password, and opens dashboard',
      (tester) async {
    final authService = _SignedOutAuthService();
    await tester.pumpWidget(AgroLensApp(authService: authService));
    await tester.pumpAndSettle();

    expect(find.text('Welcome to AgroLens').first, findsOneWidget);
    final identifier = find.byKey(const Key('auth-identifier'));
    final password = find.byKey(const Key('auth-password'));
    expect(identifier, findsOneWidget);
    expect(password, findsOneWidget);
    final editablePassword = find.descendant(
      of: password,
      matching: find.byType(EditableText),
    );
    expect(tester.widget<EditableText>(editablePassword).obscureText, isTrue);

    await tester.tap(find.byTooltip('Show password'));
    await tester.pumpAndSettle();
    expect(tester.widget<EditableText>(editablePassword).obscureText, isFalse);

    final submit = find.byKey(const Key('auth-submit'));
    await _scrollTo(tester, submit);
    await tester.tap(submit);
    await tester.pumpAndSettle();
    expect(find.text('This field is required.'), findsNWidgets(2));
    expect(authService.loginRequests, 0);

    await _scrollTo(tester, identifier);
    await tester.enterText(identifier, 'farmer@example.test');
    await _scrollTo(tester, password);
    await tester.enterText(password, 'correct-horse-battery');
    await _scrollTo(tester, find.byKey(const Key('auth-submit')));
    await tester.tap(find.byKey(const Key('auth-submit')));
    await tester.pumpAndSettle();
    expect(authService.loginRequests, 1);
    expect(authService.signUpRequests, 0);
    expect(find.byKey(const Key('agrolens-auth-page')), findsNothing);
    await _scrollTo(tester, find.byKey(const Key('analyze-photo')));
    await tester.tap(find.byKey(const Key('auth-sign-out')));
    await tester.pumpAndSettle();
    expect(authService.signOutRequests, 1);
    expect(find.byKey(const Key('agrolens-auth-page')), findsOneWidget);
  });

  testWidgets('login shows auth errors and does not navigate',
      (tester) async {
    final authService = _SignedOutAuthService()..failLogin = true;
    await tester.pumpWidget(AgroLensApp(authService: authService));
    await tester.pumpAndSettle();

    final identifier = find.byKey(const Key('auth-identifier'));
    await _scrollTo(tester, identifier);
    await tester.enterText(
      identifier,
      'farmer@example.test',
    );
    final password = find.byKey(const Key('auth-password'));
    await _scrollTo(tester, password);
    await tester.enterText(
      password,
      'wrong-password',
    );
    await _scrollTo(tester, find.byKey(const Key('auth-submit')));
    await tester.tap(find.byKey(const Key('auth-submit')));
    await tester.pumpAndSettle();

    expect(find.text('Invalid credentials.'), findsOneWidget);
    expect(find.byKey(const Key('agrolens-auth-page')), findsOneWidget);
    expect(find.byKey(const Key('analyze-photo')), findsNothing);
  });

  testWidgets('login shows a disabled loading state while the request runs',
      (tester) async {
    final authService = _SignedOutAuthService()
      ..pendingLogin = Completer<AuthSession>();
    await tester.pumpWidget(AgroLensApp(authService: authService));
    await tester.pumpAndSettle();

    final identifier = find.byKey(const Key('auth-identifier'));
    await _scrollTo(tester, identifier);
    await tester.enterText(identifier, 'farmer@example.test');
    final password = find.byKey(const Key('auth-password'));
    await _scrollTo(tester, password);
    await tester.enterText(password, 'secure-password');
    final submit = find.byKey(const Key('auth-submit'));
    await _scrollTo(tester, submit);
    await tester.tap(submit);
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(tester.widget<FilledButton>(submit).onPressed, isNull);

    authService.pendingLogin!.complete(
      const AuthSession(email: 'farmer@example.test', username: 'Farmer'),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('agrolens-auth-page')), findsNothing);
  });

  testWidgets('sign-up validates and submits account fields', (tester) async {
    final authService = _SignedOutAuthService();
    await tester.pumpWidget(AgroLensApp(authService: authService));
    await tester.pumpAndSettle();

    final signUpLink = find.textContaining('New to AgroLens?');
    await _scrollTo(tester, signUpLink);
    await tester.tap(signUpLink);
    await tester.pumpAndSettle();
    final username = find.byKey(const Key('auth-username'));
    await _scrollTo(tester, username);
    await tester.enterText(username, 'Farm User');
    final email = find.byKey(const Key('auth-email'));
    await _scrollTo(tester, email);
    await tester.enterText(email, 'farmer@example.test');
    final password = find.byKey(const Key('auth-password'));
    await _scrollTo(tester, password);
    await tester.enterText(password, 'secure-password');
    final confirmPassword = find.byKey(const Key('auth-confirm-password'));
    await _scrollTo(tester, confirmPassword);
    await tester.enterText(confirmPassword, 'secure-password');
    await _scrollTo(tester, find.byKey(const Key('auth-submit')));
    await tester.tap(find.byKey(const Key('auth-submit')));
    await tester.pumpAndSettle();

    expect(authService.signUpRequests, 1);
    expect(find.byKey(const Key('agrolens-auth-page')), findsNothing);
    await _scrollTo(tester, find.byKey(const Key('analyze-photo')));
  });

  testWidgets('local sign-up, login, and logout work through the app',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    await tester.pumpWidget(
      AgroLensApp(authService: LocalAuthService()),
    );
    await tester.pumpAndSettle();

    final signUpLink = find.textContaining('New to AgroLens?');
    await _scrollTo(tester, signUpLink);
    await tester.tap(signUpLink);
    await tester.pumpAndSettle();
    for (final entry in <(Key, String)>[
      (const Key('auth-username'), 'Farm User'),
      (const Key('auth-email'), 'farmer@example.test'),
      (const Key('auth-password'), 'secure-password'),
      (const Key('auth-confirm-password'), 'secure-password'),
    ]) {
      final field = find.byKey(entry.$1);
      await _scrollTo(tester, field);
      await tester.enterText(field, entry.$2);
    }
    final submit = find.byKey(const Key('auth-submit'));
    await _scrollTo(tester, submit);
    await tester.tap(submit);
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('agrolens-auth-page')), findsNothing);

    await tester.tap(find.byKey(const Key('auth-sign-out')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('agrolens-auth-page')), findsOneWidget);

    final identifier = find.byKey(const Key('auth-identifier'));
    await _scrollTo(tester, identifier);
    await tester.enterText(identifier, 'FARM USER');
    final password = find.byKey(const Key('auth-password'));
    await _scrollTo(tester, password);
    await tester.enterText(password, 'secure-password');
    await _scrollTo(tester, submit);
    await tester.tap(submit);
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('agrolens-auth-page')), findsNothing);

    await tester.tap(find.byKey(const Key('auth-sign-out')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('agrolens-auth-page')), findsOneWidget);
  });

  testWidgets('forgot password explains local recovery is unavailable',
      (tester) async {
    final authService = _SignedOutAuthService();
    await tester.pumpWidget(AgroLensApp(authService: authService));
    await tester.pumpAndSettle();

    final forgotPassword = find.byKey(const Key('auth-forgot-password'));
    await _scrollTo(tester, forgotPassword);
    await tester.tap(forgotPassword);
    await tester.pumpAndSettle();
    final email = find.byKey(const Key('auth-email'));
    await _scrollTo(tester, email);
    await tester.enterText(email, 'farmer@example.test');
    final submit = find.byKey(const Key('auth-submit'));
    await _scrollTo(tester, submit);
    await tester.tap(submit);
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('auth-notice')), findsOneWidget);
    expect(
      find.text('Password reset is unavailable for locally stored accounts.'),
      findsOneWidget,
    );
    expect(find.byKey(const Key('agrolens-auth-page')), findsOneWidget);
  });

  testWidgets('shows the AgroLens scan screen and demo notice', (tester) async {
    await _pumpSignedInApp(tester);

    expect(find.text('AgroLens'), findsOneWidget);
    expect(find.text('A healthier harvest starts here'), findsOneWidget);
    final coverageNotice = find.textContaining('Any plant name can be entered');
    await _scrollTo(tester, coverageNotice);
    expect(
      find.text(
        'Any plant name can be entered. This demo uses simulated results, not image recognition. Its placeholder labels cover tomato, potato, corn, bell pepper, and rice only.',
      ),
      findsOneWidget,
    );
    final childrenDelegate =
        tester.widget<ListView>(find.byType(ListView)).childrenDelegate;
    expect(childrenDelegate, isA<SliverChildListDelegate>());
    final sections = (childrenDelegate as SliverChildListDelegate).children;
    final photoSection = sections.indexWhere(
      (widget) => widget.key == const Key('photo-section-heading'),
    );
    final cropSection = sections.indexWhere(
      (widget) => widget.key == const Key('crop-section-heading'),
    );
    final locationSection = sections.indexWhere(
      (widget) => widget.key == const Key('location-section-heading'),
    );
    expect(photoSection, greaterThanOrEqualTo(0));
    expect(photoSection, lessThan(cropSection));
    expect(cropSection, lessThan(locationSection));

    final analyzeButton = find.byKey(const Key('analyze-photo'));
    await _scrollTo(tester, analyzeButton);
    expect(analyzeButton, findsOneWidget);
  });

  testWidgets('lets the user select a crop', (tester) async {
    await _pumpSignedInApp(tester);

    final potatoChip = find.byKey(const Key('crop-chip-Potato'));
    await _scrollTo(tester, potatoChip);
    await tester.tap(potatoChip);
    await tester.pumpAndSettle();

    expect(tester.widget<ChoiceChip>(potatoChip).selected, isTrue);
  });

  testWidgets('accepts a plant name not in the quick-select list', (
    tester,
  ) async {
    await _pumpSignedInApp(tester);

    final plantName = find.byKey(const Key('plant-name-field'));
    await _scrollTo(tester, plantName);
    await tester.enterText(
      plantName,
      'Mango',
    );

    expect(find.text('Mango'), findsOneWidget);
    await _scrollTo(
      tester,
      find.textContaining('Any plant name can be entered'),
    );
    expect(
      find.textContaining('Any plant name can be entered'),
      findsOneWidget,
    );
  });

  testWidgets('supports Hindi, Telugu, Tamil, and Kannada', (tester) async {
    await _pumpSignedInApp(tester);

    const languages = <(String, String)>[
      ('हिन्दी', 'बेहतर फसल की शुरुआत यहाँ से'),
      ('తెలుగు', 'మంచి పంటకు ఇక్కడే ఆరంభం'),
      ('தமிழ்', 'நல்ல அறுவடைக்கான முதல் படி'),
      ('ಕನ್ನಡ', 'ಉತ್ತಮ ಬೆಳೆಗೆ ಇಲ್ಲಿಂದ ಆರಂಭ'),
    ];

    for (final (language, heading) in languages) {
      await tester.tap(find.byKey(const Key('language-selector')));
      await tester.pumpAndSettle();
      await tester.tap(find.text(language).last);
      await tester.pumpAndSettle();
      expect(find.text(heading), findsOneWidget);
    }
  });

  testWidgets('requires location and requests it only after the user taps',
      (tester) async {
    final locationService = _FakeLocationService();
    await _pumpSignedInApp(tester, locationService: locationService);

    expect(locationService.requestCount, 0);
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsNothing);
    final useLocation = find.byKey(const Key('set-required-location'));
    await _scrollTo(tester, useLocation);
    expect(find.text('Required'), findsOneWidget);
    expect(find.text('Use my location'), findsOneWidget);

    final analyzeFinder = find.byKey(const Key('analyze-photo'));
    await _scrollTo(tester, analyzeFinder);
    final analyzeButton =
        tester.widget<FilledButton>(find.byKey(const Key('analyze-photo')));
    expect(analyzeButton.onPressed, isNull);

    await _scrollTo(tester, useLocation);
    await tester.tap(useLocation);
    await tester.pumpAndSettle();

    expect(locationService.requestCount, 1);
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsOneWidget);
    expect(find.text('Ready'), findsOneWidget);
    expect(find.text('Update location'), findsOneWidget);
    expect(find.text('Remove location'), findsNothing);
  });

  testWidgets('explains when location permission is denied', (tester) async {
    await _pumpSignedInApp(tester, locationService: _DeniedLocationService());

    final useLocation = find.byKey(const Key('set-required-location'));
    await _scrollTo(tester, useLocation);
    await tester.tap(useLocation);
    await tester.pumpAndSettle();

    expect(
      find.text(
        'Location permission was denied. Allow location access to continue with a scan.',
      ),
      findsOneWidget,
    );
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsNothing);
  });

  testWidgets('offers app settings when location permission is blocked',
      (tester) async {
    final locationService =
        _LocationFailureService(LocationFailure.permissionDeniedForever);
    await _pumpSignedInApp(tester, locationService: locationService);

    final useLocation = find.byKey(const Key('set-required-location'));
    await _scrollTo(tester, useLocation);
    await tester.tap(useLocation);
    await tester.pumpAndSettle();

    final settingsButton = find.byKey(const Key('open-location-settings'));
    await _scrollTo(tester, settingsButton);
    await tester.tap(settingsButton);
    await tester.pumpAndSettle();

    expect(locationService.appSettingsRequests, 1);
    expect(locationService.locationSettingsRequests, 0);
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsNothing);
  });

  testWidgets('offers location settings when device location is off',
      (tester) async {
    final locationService =
        _LocationFailureService(LocationFailure.servicesDisabled);
    await _pumpSignedInApp(tester, locationService: locationService);

    final useLocation = find.byKey(const Key('set-required-location'));
    await _scrollTo(tester, useLocation);
    await tester.tap(useLocation);
    await tester.pumpAndSettle();

    final settingsButton = find.byKey(const Key('open-location-settings'));
    await _scrollTo(tester, settingsButton);
    await tester.tap(settingsButton);
    await tester.pumpAndSettle();

    expect(locationService.appSettingsRequests, 0);
    expect(locationService.locationSettingsRequests, 1);
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsNothing);
  });

  testWidgets('explains when a GPS fix times out', (tester) async {
    await _pumpSignedInApp(
      tester,
      locationService:
          _LocationFailureService(LocationFailure.positionUnavailable),
    );

    final useLocation = find.byKey(const Key('set-required-location'));
    await _scrollTo(tester, useLocation);
    await tester.tap(useLocation);
    await tester.pumpAndSettle();

    expect(
      find.text(
        'Could not get a GPS fix within 60 seconds. Check your signal and try again.',
      ),
      findsOneWidget,
    );
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsNothing);
  });

  test('saves and removes geotags with a local scan', () async {
    SharedPreferences.setMockInitialValues({});
    final storage = await StorageService.initialize();
    const record = ScanRecord(
      scanId: 'scan-with-location',
      timestamp: '2026-11-04T00:00:00Z',
      crop: 'Tomato',
      aiPrediction: InferenceResult(
        predictionId: 'prediction-1',
        crop: 'Tomato',
        diseaseLabel: 'Tomato___healthy',
        confidence: 0.95,
        topPredictions: [],
        isLowConfidence: false,
        modelVersion: 'test',
        inferenceTimestamp: '2026-11-04T00:00:00Z',
      ),
      location: ScanLocation(
        latitude: 12.9716,
        longitude: 77.5946,
        hasConsent: true,
      ),
    );

    await storage.saveScan(record);
    expect(storage.getCachedScans().single.location?.latitude, 12.9716);

    await storage.saveScan(record.copyWith(clearLocation: true));
    expect(storage.getCachedScans().single.location, isNull);
  });

  test('marks low-confidence predictions for confirmation', () async {
    final service = MockInferenceService();
    addTearDown(service.dispose);

    final result = await service.runInference(
      imagePath: 'low_conf.png',
      cropHint: 'Tomato',
    );

    expect(result.confidence, 0.48);
    expect(result.isLowConfidence, isTrue);
    expect(result.topPredictions, isNotEmpty);
  });

  test('recognizes common names for supported model crops', () async {
    final service = MockInferenceService();
    addTearDown(service.dispose);

    final result = await service.runInference(
      imagePath: 'plant.png',
      cropHint: 'Bell pepper',
    );

    expect(result.crop, 'Pepper (Bell)');
  });

  test('does not silently classify an unsupported plant as tomato', () async {
    final service = MockInferenceService();
    addTearDown(service.dispose);

    await expectLater(
      service.runInference(imagePath: 'plant.png', cropHint: 'Mango'),
      throwsA(isA<UnsupportedError>()),
    );
  });
}
