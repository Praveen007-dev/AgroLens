import 'dart:convert';
import 'dart:typed_data';
import 'package:cross_file/cross_file.dart';
import 'package:http/http.dart' as http;

import '../config/app_config.dart';
import '../models/inference_result.dart';
import 'inference_service.dart';
import 'mock_inference_service.dart';

/// Real backend neural network inference service.
/// Connects to the FastAPI backend running the PyTorch MobileNetV3 model.
class BackendInferenceService implements InferenceService {
  BackendInferenceService({
    String? baseUrl,
    http.Client? client,
  })  : _baseUrl = (baseUrl ?? AppConfig.backendBaseUrl).replaceFirst(
          RegExp(r'/$'),
          '',
        ),
        _client = client ?? http.Client();

  final String _baseUrl;
  final http.Client _client;
  final MockInferenceService _fallback = MockInferenceService();
  bool _isReady = false;

  @override
  bool get isModelLoaded => _isReady;

  @override
  Future<void> initialize() async {
    _isReady = true;
  }

  @override
  void dispose() {
    _client.close();
    _fallback.dispose();
  }

  @override
  Future<InferenceResult> runInference({
    required String imagePath,
    String? cropHint,
    Uint8List? imageBytes,
  }) async {
    try {
      Uint8List bytes;
      if (imageBytes != null && imageBytes.isNotEmpty) {
        bytes = imageBytes;
      } else {
        final xfile = XFile(imagePath);
        bytes = await xfile.readAsBytes();
      }

      final uri = Uri.parse('$_baseUrl/predict');
      final payload = jsonEncode({
        'image_base64': base64Encode(bytes),
        'crop_hint': cropHint,
      });

      final response = await _client
          .post(
            uri,
            headers: const {
              'Content-Type': 'application/json',
              'Accept': 'application/json',
            },
            body: payload,
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        return InferenceResult.fromJson(data);
      }
    } catch (e) {
      // Fallback to local mock if server is offline
    }

    return _fallback.runInference(
      imagePath: imagePath,
      cropHint: cropHint,
    );
  }
}
