import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../models/agriculture_data.dart';
import 'agriculture_data_service.dart';

class AgricultureApiException implements Exception {
  const AgricultureApiException(this.message);

  final String message;

  @override
  String toString() => message;
}

class HttpAgricultureDataService implements AgricultureDataService {
  HttpAgricultureDataService({
    String? baseUrl,
    http.Client? client,
  })  : _baseUrl = (baseUrl ?? AppConfig.backendBaseUrl).replaceFirst(
          RegExp(r'/$'),
          '',
        ),
        _client = client ?? http.Client();

  final String _baseUrl;
  final http.Client _client;

  @override
  bool get isDemo => false;

  @override
  void close() => _client.close();

  @override
  Future<WeatherData> fetchWeather(String location) async {
    final response = await _get('weather', {'location': location});
    return WeatherData.fromJson(_asMap(response));
  }

  @override
  Future<List<AgricultureScheme>> fetchSchemes({
    String? state,
    String? category,
  }) async {
    final response = await _get('schemes', {
      if (_hasValue(state)) 'state': state!,
      if (_hasValue(category)) 'category': category!,
    });
    return _items(response)
        .map(AgricultureScheme.fromJson)
        .toList(growable: false);
  }

  @override
  Future<List<AgricultureNewsArticle>> fetchNews({String? category}) async {
    final response = await _get('news', {
      if (_hasValue(category)) 'category': category!,
    });
    return _items(response)
        .map(AgricultureNewsArticle.fromJson)
        .toList(growable: false);
  }

  @override
  Future<List<MandiPrice>> fetchMandiPrices({
    required String commodity,
    String? state,
    String? district,
    String? market,
  }) async {
    final response = await _get('market/prices', {
      'commodity': commodity,
      if (_hasValue(state)) 'state': state!,
      if (_hasValue(district)) 'district': district!,
      if (_hasValue(market)) 'market': market!,
    });
    return _items(response).map(MandiPrice.fromJson).toList(growable: false);
  }

  @override
  Future<List<MandiPricePoint>> fetchPriceHistory({
    required String commodity,
    String? market,
    int days = 30,
  }) async {
    final response = await _get('market/history', {
      'commodity': commodity,
      'days': '$days',
      if (_hasValue(market)) 'market': market!,
    });
    return _items(response)
        .map(MandiPricePoint.fromJson)
        .toList(growable: false);
  }

  @override
  Future<List<MandiPriceForecast>> fetchPriceForecast({
    required String commodity,
    String? market,
    int days = 5,
  }) async {
    final response = await _get('market/forecast', {
      'commodity': commodity,
      'days': '$days',
      if (_hasValue(market)) 'market': market!,
    });
    return _items(response)
        .map(MandiPriceForecast.fromJson)
        .toList(growable: false);
  }

  Future<dynamic> _get(String path, Map<String, String> query) async {
    final uri = Uri.parse('$_baseUrl/$path').replace(queryParameters: query);
    final response = await _client.get(
      uri,
      headers: const {
        'Accept': 'application/json',
        'X-Client-App': AppConfig.appName,
        'X-Client-Version': AppConfig.appVersion,
      },
    ).timeout(AppConfig.apiTimeout);
    if (response.statusCode != 200) {
      throw AgricultureApiException(
        'The agriculture service returned HTTP ${response.statusCode}.',
      );
    }

    try {
      return jsonDecode(response.body);
    } on FormatException catch (error) {
      throw AgricultureApiException(
        'The agriculture service returned invalid JSON: ${error.message}',
      );
    }
  }
}

bool _hasValue(String? value) => value != null && value.trim().isNotEmpty;

Map<String, dynamic> _asMap(dynamic value) {
  if (value is Map<String, dynamic>) return value;
  if (value is Map) return Map<String, dynamic>.from(value);
  throw const FormatException('Expected an object response from the server.');
}

List<Map<String, dynamic>> _items(dynamic response) {
  final dynamic values =
      response is List ? response : _asMap(response)['items'];
  if (values is! List) {
    throw const FormatException('Expected a list of items from the server.');
  }
  return values.map(_asMap).toList(growable: false);
}
