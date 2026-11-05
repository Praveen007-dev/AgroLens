import 'dart:convert';
import 'package:http/http.dart' as http;
import '../config/app_config.dart';
import '../models/scan_record.dart';
import 'api_service.dart';

/// Real HTTP implementation of ScanApiService connecting to Member 3's FastAPI backend.
class HttpScanApiService implements ScanApiService {
  String baseUrl;
  final http.Client _client;

  HttpScanApiService({
    String? baseUrl,
    http.Client? client,
  })  : baseUrl = baseUrl ?? AppConfig.backendBaseUrl,
        _client = client ?? http.Client();

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Client-App': AppConfig.appName,
        'X-Client-Version': AppConfig.appVersion,
      };

  @override
  Future<bool> checkHealth() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final response = await _client.get(uri).timeout(AppConfig.apiTimeout);
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  @override
  Future<bool> submitScan(ScanRecord record) async {
    try {
      final uri = Uri.parse('$baseUrl/scans');
      final recordJson = record.toJson();
      if (record.location == null) recordJson.remove('location');
      final payload = jsonEncode(recordJson);

      final response = await _client
          .post(uri, headers: _headers, body: payload)
          .timeout(AppConfig.apiTimeout);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      }
      return false;
    } catch (e) {
      print('[HttpScanApiService] Submit failed: $e');
      return false;
    }
  }

  @override
  Future<int> submitBatch(List<ScanRecord> records) async {
    try {
      final uri = Uri.parse('$baseUrl/scans/batch');
      final payload = jsonEncode(records.map((record) {
        final recordJson = record.toJson();
        if (record.location == null) recordJson.remove('location');
        return recordJson;
      }).toList());

      final response = await _client
          .post(uri, headers: _headers, body: payload)
          .timeout(AppConfig.apiTimeout * 2);

      if (response.statusCode == 200 || response.statusCode == 201) {
        final data = jsonDecode(response.body);
        return (data['synced_count'] as num?)?.toInt() ?? records.length;
      }
      return 0;
    } catch (e) {
      print('[HttpScanApiService] Batch sync failed: $e');
      return 0;
    }
  }

  @override
  Future<bool> updateFeedback(String scanId, Map<String, dynamic> feedbackData) async {
    try {
      final uri = Uri.parse('$baseUrl/scans/$scanId/feedback');
      final response = await _client
          .post(uri, headers: _headers, body: jsonEncode(feedbackData))
          .timeout(AppConfig.apiTimeout);

      return response.statusCode == 200 || response.statusCode == 204;
    } catch (e) {
      print('[HttpScanApiService] Feedback update failed: $e');
      return false;
    }
  }

  @override
  Future<List<ScanRecord>> fetchScans({int limit = 20, int offset = 0}) async {
    try {
      final uri = Uri.parse('$baseUrl/scans?limit=$limit&offset=$offset');
      final response = await _client.get(uri, headers: _headers).timeout(AppConfig.apiTimeout);

      if (response.statusCode == 200) {
        final dynamic decoded = jsonDecode(response.body);
        final List<dynamic> items = decoded is List ? decoded : (decoded['items'] ?? []);
        return items
            .map((item) => ScanRecord.fromJson(item as Map<String, dynamic>))
            .toList();
      }
      return [];
    } catch (e) {
      print('[HttpScanApiService] Fetch scans failed: $e');
      return [];
    }
  }

  @override
  Future<ScanRecord?> getScan(String scanId) async {
    try {
      final uri = Uri.parse('$baseUrl/scans/$scanId');
      final response = await _client.get(uri, headers: _headers).timeout(AppConfig.apiTimeout);

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return ScanRecord.fromJson(data);
      }
      return null;
    } catch (e) {
      print('[HttpScanApiService] Get scan failed: $e');
      return null;
    }
  }
}
