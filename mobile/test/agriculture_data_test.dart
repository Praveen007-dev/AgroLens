import 'dart:convert';

import 'package:agrolens/models/agriculture_data.dart';
import 'package:agrolens/services/http_agriculture_data_service.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';

void main() {
  group('Agriculture data models', () {
    test('keeps unavailable weather fields null and parses forecast values',
        () {
      final weather = WeatherData.fromJson({
        'location': 'Bengaluru',
        'temperature_c': 26,
        'forecast': [
          {
            'date': '2026-11-05',
            'min_temperature_c': 19,
            'max_temperature_c': 28,
            'rain_probability_pct': 45,
          },
        ],
      });

      expect(weather.location, 'Bengaluru');
      expect(weather.temperatureC, 26);
      expect(weather.humidityPct, isNull);
      expect(weather.advisory, isNull);
      expect(weather.forecast.single.minTemperatureC, 19);
      expect(weather.forecast.single.rainProbabilityPct, 45);
    });

    test('parses scheme aliases and leaves unknown details unavailable', () {
      final scheme = AgricultureScheme.fromJson({
        'title': 'Scheme title',
        'required_documents': ['Identity proof'],
      });

      expect(scheme.name, 'Scheme title');
      expect(scheme.requiredDocuments, ['Identity proof']);
      expect(scheme.eligibility, isNull);
      expect(scheme.benefits, isNull);
      expect(scheme.applicationDeadline, isNull);
      expect(scheme.officialUrl, isNull);
    });

    test('parses prices without inventing currency or unit', () {
      final price = MandiPrice.fromJson({
        'commodity': 'Tomato',
        'modal_price': 2410,
      });

      expect(price.modalPrice, 2410);
      expect(price.minPrice, isNull);
      expect(price.currency, isNull);
      expect(price.unit, isNull);
    });

    test('rejects non-finite numeric values as unavailable', () {
      final point = MandiPricePoint.fromJson({
        'date': '2026-11-04',
        'modal_price': double.infinity,
        'currency': 'INR',
        'unit': 'quintal',
      });

      expect(point.modalPrice, isNull);
      expect(point.currency, 'INR');
      expect(point.unit, 'quintal');
    });
  });

  group('HttpAgricultureDataService', () {
    test('uses the documented endpoints and parses list responses', () async {
      final requests = <http.Request>[];
      final service = HttpAgricultureDataService(
        baseUrl: 'https://api.example.test/api/v1/',
        client: MockClient((request) async {
          requests.add(request);
          if (request.url.path.endsWith('/weather')) {
            return http.Response(
              jsonEncode({'location': 'Bengaluru', 'temperature_c': 27}),
              200,
            );
          }
          if (request.url.path.endsWith('/schemes')) {
            return http.Response(
              jsonEncode({
                'items': [
                  {'name': 'Sample scheme'},
                ],
              }),
              200,
            );
          }
          if (request.url.path.endsWith('/news')) {
            return http.Response(
              jsonEncode([
                {
                  'title': 'News title',
                  'summary': 'Summary text',
                  'source': 'News source',
                  'original_url': 'https://news.example.test/article',
                },
              ]),
              200,
            );
          }
          if (request.url.path.endsWith('/market/prices')) {
            return http.Response(
              jsonEncode({
                'items': [
                  {
                    'commodity': 'Tomato',
                    'state': 'Karnataka',
                    'district': 'Bengaluru Urban',
                    'market': 'Bengaluru',
                    'min_price': 1800,
                    'modal_price': 2200,
                    'max_price': 2600,
                    'currency': 'INR',
                    'unit': 'quintal',
                  },
                ],
              }),
              200,
            );
          }
          if (request.url.path.endsWith('/market/forecast')) {
            return http.Response(
              jsonEncode([
                {
                  'date': '2026-11-05',
                  'predicted_modal_price': 2250,
                  'currency': 'INR',
                  'unit': 'quintal',
                },
              ]),
              200,
            );
          }
          return http.Response('[]', 200);
        }),
      );
      addTearDown(service.close);

      final weather = await service.fetchWeather('Bengaluru & Rural');
      final schemes = await service.fetchSchemes(
        state: 'Tamil Nadu',
        category: 'Input support',
      );
      final news = await service.fetchNews(category: 'Markets');
      final prices = await service.fetchMandiPrices(
        commodity: 'Tomato',
        state: 'Karnataka',
        district: 'Bengaluru Urban',
        market: 'Bengaluru',
      );
      final forecasts = await service.fetchPriceForecast(
        commodity: 'Tomato',
        market: 'Bengaluru',
      );

      expect(weather.temperatureC, 27);
      expect(requests[0].url.path, '/api/v1/weather');
      expect(requests[0].url.queryParameters['location'], 'Bengaluru & Rural');
      expect(schemes.single.name, 'Sample scheme');
      expect(requests[1].url.queryParameters, {
        'state': 'Tamil Nadu',
        'category': 'Input support',
      });
      expect(news.single.originalUrl, 'https://news.example.test/article');
      expect(requests[2].url.path, '/api/v1/news');
      expect(requests[2].url.queryParameters['category'], 'Markets');
      expect(prices.single.modalPrice, 2200);
      expect(prices.single.unit, 'quintal');
      expect(requests[3].url.path, '/api/v1/market/prices');
      expect(requests[3].url.queryParameters, {
        'commodity': 'Tomato',
        'state': 'Karnataka',
        'district': 'Bengaluru Urban',
        'market': 'Bengaluru',
      });
      expect(forecasts.single.predictedModalPrice, 2250);
      expect(requests[4].url.path, '/api/v1/market/forecast');
      expect(requests[4].url.queryParameters['days'], '5');
    });

    test('sends commodity, market and bounded history query values', () async {
      late Uri requestedUri;
      final service = HttpAgricultureDataService(
        baseUrl: 'https://api.example.test/api/v1',
        client: MockClient((request) async {
          requestedUri = request.url;
          return http.Response(
            jsonEncode([
              {
                'date': '2026-11-04',
                'modal_price': 2100,
                'currency': 'INR',
                'unit': 'quintal',
              },
            ]),
            200,
          );
        }),
      );
      addTearDown(service.close);

      await service.fetchPriceHistory(
        commodity: 'Potato',
        market: 'Mysuru',
        days: 30,
      );

      expect(requestedUri.path, '/api/v1/market/history');
      expect(requestedUri.queryParameters, {
        'commodity': 'Potato',
        'market': 'Mysuru',
        'days': '30',
      });
      final point = await service.fetchPriceHistory(
        commodity: 'Potato',
        market: 'Mysuru',
      );
      expect(point.single.currency, 'INR');
      expect(point.single.unit, 'quintal');
    });

    test('surfaces HTTP failures instead of returning success-shaped empties',
        () async {
      final service = HttpAgricultureDataService(
        baseUrl: 'https://api.example.test/api/v1',
        client: MockClient(
          (_) async => http.Response('service unavailable', 503),
        ),
      );
      addTearDown(service.close);

      await expectLater(
        service.fetchNews(),
        throwsA(
          isA<AgricultureApiException>().having(
            (error) => error.message,
            'message',
            contains('HTTP 503'),
          ),
        ),
      );
    });

    test('surfaces malformed JSON and unexpected response shapes', () async {
      final service = HttpAgricultureDataService(
        baseUrl: 'https://api.example.test/api/v1',
        client: MockClient((request) async {
          return http.Response(
            request.url.path.endsWith('/weather') ? '{bad json' : '{"bad":1}',
            200,
          );
        }),
      );
      addTearDown(service.close);

      await expectLater(
        service.fetchWeather('Bengaluru'),
        throwsA(isA<AgricultureApiException>()),
      );
      await expectLater(
        service.fetchNews(),
        throwsA(isA<FormatException>()),
      );
    });

    test('reports optional forecast data as an empty backend result', () async {
      final service = HttpAgricultureDataService(
        baseUrl: 'https://api.example.test/api/v1',
        client: MockClient((_) async => http.Response('{"items":[]}', 200)),
      );
      addTearDown(service.close);

      final forecast = await service.fetchPriceForecast(
        commodity: 'Rice',
        days: 5,
      );

      expect(forecast, isEmpty);
    });
  });
}
