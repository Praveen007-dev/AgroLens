import 'dart:async';

import 'package:agrolens/main.dart';
import 'package:agrolens/models/agriculture_data.dart';
import 'package:agrolens/models/inference_result.dart';
import 'package:agrolens/models/scan_record.dart';
import 'package:agrolens/services/agriculture_data_service.dart';
import 'package:agrolens/services/auth_service.dart';
import 'package:agrolens/services/storage_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

class _SignedInAuthService implements AuthService {
  @override
  Future<AuthSession?> restoreSession() async =>
      const AuthSession(email: 'farmer@example.test');

  @override
  Future<AuthSession> login({
    required String identifier,
    required String password,
  }) async =>
      const AuthSession(email: 'farmer@example.test');

  @override
  Future<AuthSession> signUp({
    required String username,
    required String email,
    required String password,
  }) async =>
      const AuthSession(email: 'farmer@example.test');

  @override
  Future<void> signOut() async {}
}

class _FakeAgricultureDataService implements AgricultureDataService {
  @override
  bool get isDemo => true;

  final weatherLocations = <String>[];
  Completer<WeatherData>? weatherCompleter;
  bool failPrices = false;
  bool failForecast = false;
  List<AgricultureScheme> schemeResults = const [
    AgricultureScheme(
      name: 'Sample scheme',
      scope: 'State',
      requiredDocuments: ['Identity proof'],
    ),
  ];
  List<MandiPriceForecast> forecastResults = const [
    MandiPriceForecast(
      date: 'Estimate 1',
      predictedModalPrice: 2220,
      currency: 'INR',
      unit: 'quintal',
    ),
    MandiPriceForecast(
      date: 'Estimate 2',
      predictedModalPrice: 2230,
      currency: 'INR',
      unit: 'quintal',
    ),
    MandiPriceForecast(
      date: 'Estimate 3',
      predictedModalPrice: 2240,
      currency: 'INR',
      unit: 'quintal',
    ),
    MandiPriceForecast(
      date: 'Estimate 4',
      predictedModalPrice: 2250,
      currency: 'INR',
      unit: 'quintal',
    ),
    MandiPriceForecast(
      date: 'Estimate 5',
      predictedModalPrice: 2260,
      currency: 'INR',
      unit: 'quintal',
    ),
    MandiPriceForecast(
      date: 'Estimate 6',
      predictedModalPrice: 2270,
      currency: 'INR',
      unit: 'quintal',
    ),
  ];
  String? lastSchemeState;
  String? lastSchemeCategory;
  String? lastCommodity;

  @override
  void close() {}

  @override
  Future<WeatherData> fetchWeather(String location) async {
    weatherLocations.add(location);
    if (weatherCompleter case final completer?) return completer.future;
    return WeatherData(
      location: location,
      condition: 'Cloudy',
      temperatureC: 25,
      rainfallMm: 0,
      rainProbabilityPct: 20,
      humidityPct: 60,
      windSpeedKph: 10,
      forecast: const [
        WeatherForecastDay(
          date: 'Tomorrow',
          condition: 'Clear',
          minTemperatureC: 18,
          maxTemperatureC: 27,
        ),
      ],
    );
  }

  @override
  Future<List<AgricultureScheme>> fetchSchemes({
    String? state,
    String? category,
  }) async {
    lastSchemeState = state;
    lastSchemeCategory = category;
    return schemeResults;
  }

  @override
  Future<List<AgricultureNewsArticle>> fetchNews({String? category}) async {
    return const [
      AgricultureNewsArticle(
        title: 'Sample news headline',
        summary: 'A separate backend-provided summary.',
        source: 'Sample source',
        publishedAt: '2026-11-04',
        category: 'Markets',
      ),
    ];
  }

  @override
  Future<List<MandiPrice>> fetchMandiPrices({
    required String commodity,
    String? state,
    String? district,
    String? market,
  }) async {
    lastCommodity = commodity;
    if (failPrices) throw StateError('prices unavailable');
    return [
      MandiPrice(
        commodity: commodity,
        state: state,
        district: district,
        market: market,
        minPrice: 1800,
        modalPrice: 2200,
        maxPrice: 2600,
        currency: 'INR',
        unit: 'quintal',
        priceDate: '2026-11-04',
      ),
    ];
  }

  @override
  Future<List<MandiPricePoint>> fetchPriceHistory({
    required String commodity,
    String? market,
    int days = 30,
  }) async {
    return const [
      MandiPricePoint(
        date: 'Day 1',
        modalPrice: 1900,
        currency: 'INR',
        unit: 'quintal',
      ),
      MandiPricePoint(
        date: 'Day 2',
        modalPrice: 2000,
        currency: 'INR',
        unit: 'quintal',
      ),
      MandiPricePoint(
        date: 'Day 3',
        modalPrice: 2100,
        currency: 'INR',
        unit: 'quintal',
      ),
    ];
  }

  @override
  Future<List<MandiPriceForecast>> fetchPriceForecast({
    required String commodity,
    String? market,
    int days = 5,
  }) async {
    if (failForecast) throw StateError('forecast unavailable');
    return forecastResults;
  }
}

Future<void> _openHub(
    WidgetTester tester, _FakeAgricultureDataService service) async {
  await tester.pumpWidget(
    AgroLensApp(
      authService: _SignedInAuthService(),
      agricultureDataService: service,
    ),
  );
  await tester.pumpAndSettle();
  await tester.tap(find.byKey(const Key('open-agriculture-tools')));
  await tester.pumpAndSettle();
}

Future<void> _openFeature(
  WidgetTester tester,
  _FakeAgricultureDataService service,
  String key,
) async {
  await _openHub(tester, service);
  await tester.tap(find.byKey(Key(key)));
  await tester.pumpAndSettle();
}

Future<void> _scrollTo(WidgetTester tester, Finder finder) async {
  for (var attempt = 0; attempt < 8; attempt++) {
    if (finder.evaluate().isNotEmpty) {
      await tester.ensureVisible(finder);
      await tester.pumpAndSettle();
      return;
    }
    await tester.drag(find.byType(Scrollable).last, const Offset(0, -450));
    await tester.pumpAndSettle();
  }
  expect(finder, findsOneWidget);
}

void main() {
  testWidgets('agriculture hub is reachable without replacing the scan screen',
      (tester) async {
    final service = _FakeAgricultureDataService();
    await tester.pumpWidget(
      AgroLensApp(
        authService: _SignedInAuthService(),
        agricultureDataService: service,
      ),
    );
    await tester.pumpAndSettle();
    await _scrollTo(tester, find.byKey(const Key('analyze-photo')));
    expect(find.byKey(const Key('analyze-photo')), findsOneWidget);
    await tester.tap(find.byKey(const Key('open-agriculture-tools')));
    await tester.pumpAndSettle();

    expect(find.text('Agriculture tools'), findsOneWidget);
    expect(find.byKey(const Key('agriculture-weather')), findsOneWidget);
    expect(find.byKey(const Key('agriculture-schemes')), findsOneWidget);
    expect(find.byKey(const Key('agriculture-news')), findsOneWidget);
    expect(find.byKey(const Key('agriculture-markets')), findsOneWidget);
    expect(find.byKey(const Key('agriculture-scan-history')), findsOneWidget);
    expect(
      find.text('Development sample data - not live information or advice.'),
      findsOneWidget,
    );
  });

  testWidgets('weather waits for an explicit location and shows available data',
      (tester) async {
    final service = _FakeAgricultureDataService();
    await _openFeature(tester, service, 'agriculture-weather');

    expect(service.weatherLocations, isEmpty);
    await tester.tap(find.byKey(const Key('weather-load')));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('weather-location-error')), findsOneWidget);
    expect(service.weatherLocations, isEmpty);

    await tester.enterText(
      find.byKey(const Key('weather-location')),
      'Bengaluru',
    );
    await tester.tap(find.byKey(const Key('weather-load')));
    await tester.pumpAndSettle();

    expect(service.weatherLocations, ['Bengaluru']);
    expect(find.text('Temperature'), findsWidgets);
    expect(find.text('25 °C'), findsOneWidget);
    expect(find.text('Humidity'), findsWidgets);
    expect(find.text('Crop advisory'), findsOneWidget);
    expect(find.text('Unavailable'), findsWidgets);
    expect(find.text('Tomorrow'), findsOneWidget);
  });

  testWidgets('weather errors can be retried without leaving the feature',
      (tester) async {
    final service = _FakeAgricultureDataService()
      ..weatherCompleter = Completer<WeatherData>();
    await _openFeature(tester, service, 'agriculture-weather');
    await tester.enterText(
      find.byKey(const Key('weather-location')),
      'Mysuru',
    );
    await tester.tap(find.byKey(const Key('weather-load')));
    await tester.pump();
    service.weatherCompleter!.completeError(StateError('weather unavailable'));
    await tester.pumpAndSettle();

    expect(find.textContaining('weather unavailable'), findsOneWidget);
    expect(find.text('Try again'), findsOneWidget);
    service.weatherCompleter = null;
    await tester.tap(find.byKey(const Key('feature-retry')));
    await tester.pumpAndSettle();

    expect(service.weatherLocations, ['Mysuru', 'Mysuru']);
    expect(find.text('Cloudy'), findsOneWidget);
  });

  testWidgets('weather displays a loading state while the request is pending',
      (tester) async {
    final service = _FakeAgricultureDataService()
      ..weatherCompleter = Completer<WeatherData>();
    await _openFeature(tester, service, 'agriculture-weather');
    await tester.enterText(
      find.byKey(const Key('weather-location')),
      'Tumakuru',
    );
    await tester.tap(find.byKey(const Key('weather-load')));
    await tester.pump();

    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    service.weatherCompleter!.complete(
      const WeatherData(location: 'Tumakuru', condition: 'Clear'),
    );
    await tester.pumpAndSettle();

    expect(find.text('Clear'), findsOneWidget);
  });

  testWidgets('schemes are filterable and unknown details are unavailable',
      (tester) async {
    final service = _FakeAgricultureDataService();
    await _openFeature(tester, service, 'agriculture-schemes');

    expect(find.text('Sample scheme'), findsOneWidget);
    expect(find.text('Eligibility'), findsOneWidget);
    expect(find.text('Benefits / subsidy'), findsOneWidget);
    expect(find.text('Application deadline'), findsOneWidget);
    expect(find.text('Official link'), findsOneWidget);
    expect(find.byKey(const Key('scheme-official-link')), findsNothing);

    await tester.tap(find.byKey(const Key('schemes-state')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Karnataka').last);
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('schemes-category')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Insurance').last);
    await tester.pumpAndSettle();

    expect(service.lastSchemeState, 'Karnataka');
    expect(service.lastSchemeCategory, 'Insurance');
  });

  testWidgets('schemes show a clear empty state when no results are returned',
      (tester) async {
    final service = _FakeAgricultureDataService()..schemeResults = const [];
    await _openFeature(tester, service, 'agriculture-schemes');

    expect(
      find.text('No schemes are available for these filters.'),
      findsOneWidget,
    );
    expect(find.text('Sample scheme'), findsNothing);
  });

  testWidgets('news labels summaries separately from original articles',
      (tester) async {
    final service = _FakeAgricultureDataService();
    await _openFeature(tester, service, 'agriculture-news');

    expect(find.text('Sample news headline'), findsOneWidget);
    expect(find.text('Summary'), findsOneWidget);
    expect(find.text('A separate backend-provided summary.'), findsOneWidget);
    expect(find.text('Sample source'), findsOneWidget);
    expect(find.text('2026-11-04'), findsOneWidget);
    expect(find.text('Original article link'), findsOneWidget);
    expect(find.byKey(const Key('news-original-link')), findsNothing);
  });

  testWidgets('market keeps latest prices visible if forecast request fails',
      (tester) async {
    final service = _FakeAgricultureDataService()..failForecast = true;
    await _openFeature(tester, service, 'agriculture-markets');

    expect(find.text('Minimum price'), findsOneWidget);
    expect(find.text('INR 1800.00 / quintal'), findsOneWidget);
    expect(find.text('Modal price'), findsOneWidget);
    expect(find.text('INR 2200.00 / quintal'), findsOneWidget);
    expect(find.text('Maximum price'), findsOneWidget);
    expect(find.text('INR 2600.00 / quintal'), findsOneWidget);

    await _scrollTo(tester, find.byKey(const Key('market-price-chart')));
    expect(find.byKey(const Key('market-price-chart')), findsOneWidget);
    expect(find.text('Tomato modal price (INR / quintal)'), findsOneWidget);
    expect(find.text('Could not load data: Bad state: forecast unavailable'),
        findsOneWidget);
    expect(find.text('Forecasts are estimates, not guaranteed prices.'),
        findsOneWidget);
    expect(find.text('INR 2220.00 / quintal'), findsNothing);
  });

  testWidgets('market price errors do not hide history or forecast data',
      (tester) async {
    final service = _FakeAgricultureDataService()..failPrices = true;
    await _openFeature(tester, service, 'agriculture-markets');

    expect(
      find.text('Could not load data: Bad state: prices unavailable'),
      findsOneWidget,
    );
    await _scrollTo(tester, find.byKey(const Key('market-price-chart')));
    expect(find.byKey(const Key('market-price-chart')), findsOneWidget);
    await _scrollTo(tester, find.text('Estimate 5'));
    expect(find.text('Estimate 5'), findsOneWidget);
  });

  testWidgets('market shows an unavailable forecast without disturbing prices',
      (tester) async {
    final service = _FakeAgricultureDataService()..forecastResults = const [];
    await _openFeature(tester, service, 'agriculture-markets');

    expect(find.text('INR 2200.00 / quintal'), findsOneWidget);
    await _scrollTo(tester, find.text('No price forecast is available.'));
    expect(find.text('No price forecast is available.'), findsOneWidget);
  });

  testWidgets(
      'market displays only five backend forecasts and labels estimates',
      (tester) async {
    final service = _FakeAgricultureDataService();
    await _openFeature(tester, service, 'agriculture-markets');
    await _scrollTo(tester, find.text('Estimate 5'));

    expect(find.text('Estimate 5'), findsOneWidget);
    expect(find.text('Estimate 6'), findsNothing);
    expect(find.text('Forecasts are estimates, not guaranteed prices.'),
        findsOneWidget);
    expect(find.text('INR 2260.00 / quintal'), findsOneWidget);
  });

  testWidgets('market commodity selection refreshes backend queries',
      (tester) async {
    final service = _FakeAgricultureDataService();
    await _openFeature(tester, service, 'agriculture-markets');

    await tester.tap(find.byKey(const Key('market-commodity')));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Potato').last);
    await tester.pumpAndSettle();

    expect(service.lastCommodity, 'Potato');
    expect(find.text('Potato · Bengaluru'), findsOneWidget);
  });

  testWidgets('scan history reads existing locally saved disease scans',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    final storage = await StorageService.initialize();
    const scan = ScanRecord(
      scanId: 'history-scan',
      timestamp: '2026-11-04T10:00:00Z',
      crop: 'Tomato',
      aiPrediction: InferenceResult(
        predictionId: 'history-prediction',
        crop: 'Tomato',
        diseaseLabel: 'Tomato___Early_blight',
        confidence: 0.9,
        topPredictions: [],
        isLowConfidence: false,
        modelVersion: 'test',
        inferenceTimestamp: '2026-11-04T10:00:00Z',
      ),
    );
    await storage.saveScan(scan);
    final service = _FakeAgricultureDataService();
    await _openHub(tester, service);
    await tester.tap(find.byKey(const Key('agriculture-scan-history')));
    await tester.pumpAndSettle();

    expect(find.text('Tomato'), findsOneWidget);
    expect(find.text('Early blight'), findsOneWidget);
    expect(find.text('90%'), findsOneWidget);
    expect(find.text('pending'), findsOneWidget);
  });

  testWidgets('empty scan history is explained instead of fabricated',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    final storage = await StorageService.initialize();
    final service = _FakeAgricultureDataService();
    await _openHub(tester, service);
    await tester.tap(find.byKey(const Key('agriculture-scan-history')));
    await tester.pumpAndSettle();

    expect(
      find.text('No scans have been saved on this device yet.'),
      findsOneWidget,
    );
    expect(storage.getCachedScans(), isEmpty);
  });
}
