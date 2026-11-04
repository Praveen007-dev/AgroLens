import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/scan_record.dart';

/// Local offline-first storage service for scans, settings, and pending queue.
class StorageService {
  static const String _kScansKey = 'agrolens_scans_cache';
  static const String _kPendingQueueKey = 'agrolens_pending_queue';
  static const String _kLocationConsentKey = 'agrolens_location_consent';
  static const String _kBackendUrlKey = 'agrolens_backend_url';
  static const String _kMockApiModeKey = 'agrolens_mock_api_mode';
  static const String _kMockInferenceKey = 'agrolens_mock_inference_mode';

  final SharedPreferences _prefs;

  StorageService(this._prefs);

  static Future<StorageService> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    return StorageService(prefs);
  }

  // --- Scans Cache ---

  List<ScanRecord> getCachedScans() {
    final rawJson = _prefs.getString(_kScansKey);
    if (rawJson == null || rawJson.isEmpty) return [];

    try {
      final List<dynamic> list = jsonDecode(rawJson);
      return list
          .map((item) => ScanRecord.fromJson(item as Map<String, dynamic>))
          .toList();
    } catch (e) {
      print('[StorageService] Error reading cached scans: $e');
      return [];
    }
  }

  Future<void> saveScan(ScanRecord record) async {
    final scans = getCachedScans();
    final index = scans.indexWhere((r) => r.scanId == record.scanId);
    if (index >= 0) {
      scans[index] = record;
    } else {
      scans.insert(0, record);
    }

    final rawJson = jsonEncode(scans.map((r) => r.toJson()).toList());
    await _prefs.setString(_kScansKey, rawJson);
  }

  Future<void> saveScans(List<ScanRecord> newScans) async {
    final scans = getCachedScans();
    for (final s in newScans) {
      final idx = scans.indexWhere((r) => r.scanId == s.scanId);
      if (idx >= 0) {
        scans[idx] = s;
      } else {
        scans.add(s);
      }
    }
    scans.sort((a, b) => b.timestamp.compareTo(a.timestamp));
    final rawJson = jsonEncode(scans.map((r) => r.toJson()).toList());
    await _prefs.setString(_kScansKey, rawJson);
  }

  // --- Offline Queue ---

  List<ScanRecord> getPendingQueue() {
    final rawJson = _prefs.getString(_kPendingQueueKey);
    if (rawJson == null || rawJson.isEmpty) return [];

    try {
      final List<dynamic> list = jsonDecode(rawJson);
      return list
          .map((item) => ScanRecord.fromJson(item as Map<String, dynamic>))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> addToPendingQueue(ScanRecord record) async {
    final queue = getPendingQueue();
    final idx = queue.indexWhere((r) => r.scanId == record.scanId);
    if (idx >= 0) {
      queue[idx] = record;
    } else {
      queue.add(record);
    }
    await _prefs.setString(
      _kPendingQueueKey,
      jsonEncode(queue.map((r) => r.toJson()).toList()),
    );
  }

  Future<void> removeFromPendingQueue(String scanId) async {
    final queue = getPendingQueue();
    queue.removeWhere((r) => r.scanId == scanId);
    await _prefs.setString(
      _kPendingQueueKey,
      jsonEncode(queue.map((r) => r.toJson()).toList()),
    );
  }

  Future<void> clearPendingQueue() async {
    await _prefs.remove(_kPendingQueueKey);
  }

  // --- Privacy & Consent Settings ---

  bool getLocationConsent() {
    return _prefs.getBool(_kLocationConsentKey) ?? false;
  }

  Future<void> setLocationConsent(bool consent) async {
    await _prefs.setBool(_kLocationConsentKey, consent);
  }

  // --- Backend Settings ---

  String? getCustomBackendUrl() {
    return _prefs.getString(_kBackendUrlKey);
  }

  Future<void> setCustomBackendUrl(String url) async {
    await _prefs.setString(_kBackendUrlKey, url);
  }

  bool? getMockApiMode() {
    return _prefs.getBool(_kMockApiModeKey);
  }

  Future<void> setMockApiMode(bool enabled) async {
    await _prefs.setBool(_kMockApiModeKey, enabled);
  }

  bool? getMockInferenceMode() {
    return _prefs.getBool(_kMockInferenceKey);
  }

  Future<void> setMockInferenceMode(bool enabled) async {
    await _prefs.setBool(_kMockInferenceKey, enabled);
  }

  Future<void> clearAll() async {
    await _prefs.clear();
  }
}
