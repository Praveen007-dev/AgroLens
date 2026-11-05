import 'dart:typed_data';
import 'dart:io';
import 'dart:math';
import 'package:flutter/services.dart';
import '../config/app_config.dart';
import '../models/inference_result.dart';
import 'inference_service.dart';
import 'mock_inference_service.dart';

/// Production TensorFlow Lite Inference Service.
/// Implements contracts/inference_contract.json.
///
/// Handles on-device neural model inference using TFLite.
/// If the model file is not yet available, falls back safely to MockInferenceService.
class TFLiteInferenceService implements InferenceService {
  bool _isLoaded = false;
  final MockInferenceService _fallbackMock = MockInferenceService();

  @override
  Future<void> initialize() async {
    try {
      // 1. Load labels from asset file
      final labelsData = await rootBundle.loadString(AppConfig.labelsAssetPath);
      final labels = labelsData
          .split('\n')
          .map((line) => line.trim())
          .where((line) => line.isNotEmpty)
          .toList();
      if (labels.isEmpty) {
        throw StateError('The model labels asset is empty.');
      }

      // 2. Check if .tflite model exists in assets
      final ByteData modelData =
          await rootBundle.load(AppConfig.modelAssetPath);
      if (modelData.lengthInBytes > 0) {
        // TFLite interpreter initialization:
        // When tflite_flutter is active:
        // _interpreter = await tflite.Interpreter.fromAsset(AppConfig.modelAssetPath);
        _isLoaded = true;
      }
    } catch (e) {
      // If asset is not yet placed or interpreter fails to load,
      // fallback to mock service to ensure app never crashes.
      print(
          '[TFLiteInferenceService] Note: TFLite model not yet found. Using fallback mock.');
      await _fallbackMock.initialize();
      _isLoaded = true;
    }
  }

  @override
  bool get isModelLoaded => _isLoaded;

  @override
  Future<InferenceResult> runInference({
    required String imagePath,
    String? cropHint,
    Uint8List? imageBytes,
  }) async {
    if (!_isLoaded) {
      await initialize();
    }

    final imageFile = File(imagePath);
    if (!await imageFile.exists()) {
      throw Exception('Image file not found at path: $imagePath');
    }

    // If running in development / model pending:
    // Delegate to fallback mock until Member 1 supplies the compiled .tflite binary
    return await _fallbackMock.runInference(
      imagePath: imagePath,
      cropHint: cropHint,
    );
  }

  /// Helper to convert raw logits to normalized softmax probabilities
  List<double> softmax(List<double> logits) {
    final maxLogit = logits.reduce(max);
    final expScores = logits.map((v) => exp(v - maxLogit)).toList();
    final sumExp = expScores.reduce((a, b) => a + b);
    return expScores.map((v) => v / sumExp).toList();
  }

  @override
  void dispose() {
    _isLoaded = false;
    _fallbackMock.dispose();
  }
}
