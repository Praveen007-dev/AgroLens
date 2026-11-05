import 'package:flutter/foundation.dart';

/// AgroLens Mobile Configuration
/// Provides centralized configuration parameters for AI inference,
/// backend endpoints, privacy thresholds, and feature flags.
class AppConfig {
  static const String appName = 'AgroLens';
  static const String appVersion = '1.0.0';
  static const String buildNumber = '1';

  // AI Inference Configuration
  static const double lowConfidenceThreshold = 0.60;
  static const String defaultModelVersion = 'agrolens-tflite-v1.0.0-rc1';
  static const String modelAssetPath =
      'assets/models/crop_disease_model.tflite';
  static const String labelsAssetPath = 'assets/models/labels.txt';
  static const int modelInputSize = 224; // 224x224 RGB

  // Backend Integration (Member 3 - FastAPI)
  // Override AGROLENS_API_HOST for a physical device on the same LAN.
  static String get backendBaseUrl {
    const configuredHost = String.fromEnvironment('AGROLENS_API_HOST');
    final host = configuredHost.isNotEmpty
        ? configuredHost
        : (kIsWeb ? Uri.base.host : '10.0.2.2');
    return 'http://$host:8000/api/v1';
  }
  static const Duration apiTimeout = Duration(seconds: 10);

  // Runtime Mode Flags
  static bool useMockInference =
      true; // Set to false when Member 1's TFLite model is dropped in
  // Agriculture feature responses remain development samples until the
  // corresponding backend endpoints are implemented.
  static bool useMockApi = false;
  static bool allowOfflineQueue =
      true; // Stores scans locally if backend is unavailable

  // Supported Crops
  static const List<String> supportedCrops = [
    'Tomato',
    'Potato',
    'Corn',
    'Pepper (Bell)',
    'Rice',
    'Other / Unspecified',
  ];
}
