import 'package:agrolens/main.dart';
import 'package:agrolens/models/inference_result.dart';
import 'package:agrolens/models/scan_record.dart';
import 'package:agrolens/services/location_service.dart';
import 'package:agrolens/services/mock_inference_service.dart';
import 'package:agrolens/services/storage_service.dart';
import 'package:flutter/material.dart' show ChoiceChip, Key, Scrollable;
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
  testWidgets('shows the AgroLens scan screen and demo notice', (tester) async {
    await tester.pumpWidget(const AgroLensApp());

    expect(find.text('AgroLens'), findsOneWidget);
    expect(find.text('A healthier harvest starts here'), findsOneWidget);
    expect(
      find.text(
        'Any plant name can be entered. This demo uses simulated results, not image recognition. Its placeholder labels cover tomato, potato, corn, bell pepper, and rice only.',
      ),
      findsOneWidget,
    );
    final analyzeButton = find.byKey(const Key('analyze-photo'));
    await _scrollTo(tester, analyzeButton);
    expect(analyzeButton, findsOneWidget);
  });

  testWidgets('lets the user select a crop', (tester) async {
    await tester.pumpWidget(const AgroLensApp());

    final potatoChip = find.byKey(const Key('crop-chip-Potato'));
    await _scrollTo(tester, potatoChip);
    await tester.tap(potatoChip);
    await tester.pumpAndSettle();

    expect(tester.widget<ChoiceChip>(potatoChip).selected, isTrue);
  });

  testWidgets('accepts a plant name not in the quick-select list', (
    tester,
  ) async {
    await tester.pumpWidget(const AgroLensApp());

    await tester.enterText(
      find.byKey(const Key('plant-name-field')),
      'Mango',
    );

    expect(find.text('Mango'), findsOneWidget);
    expect(
      find.textContaining('Any plant name can be entered'),
      findsOneWidget,
    );
  });

  testWidgets('supports Hindi, Telugu, Tamil, and Kannada', (tester) async {
    await tester.pumpWidget(const AgroLensApp());

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

  testWidgets('requests location only after the user opts in', (tester) async {
    final locationService = _FakeLocationService();
    await tester.pumpWidget(
      AgroLensApp(locationService: locationService),
    );

    expect(locationService.requestCount, 0);
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsNothing);

    final addLocation = find.text('Add location');
    await _scrollTo(tester, addLocation);
    await tester.tap(addLocation);
    await tester.pumpAndSettle();

    expect(locationService.requestCount, 1);
    expect(find.text('Coordinates: 12.9716, 77.5946'), findsOneWidget);
    expect(find.text('Remove location'), findsOneWidget);
  });

  testWidgets('explains when location permission is denied', (tester) async {
    await tester.pumpWidget(
      AgroLensApp(locationService: _DeniedLocationService()),
    );

    final addLocation = find.text('Add location');
    await _scrollTo(tester, addLocation);
    await tester.tap(addLocation);
    await tester.pumpAndSettle();

    expect(
      find.text(
        'Location permission was denied. Allow location access to add a location to this scan.',
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
