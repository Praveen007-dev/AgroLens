import 'dart:typed_data';
import 'dart:math';
import '../config/app_config.dart';
import '../models/inference_result.dart';
import 'inference_service.dart';

/// High-fidelity Mock Inference Service.
/// Implements contracts/inference_contract.json to enable full UI and pipeline
/// development while Member 1 (ML Engineer) prepares the production TFLite model.
class MockInferenceService implements InferenceService {
  bool _isLoaded = false;
  final Random _random = Random();
  static const Map<String, String> _cropAliases = {
    'bell pepper': 'Pepper (Bell)',
    'capsicum': 'Pepper (Bell)',
    'maize': 'Corn',
    'paddy': 'Rice',
  };

  // Disease database with realistic probabilities
  static const Map<String, List<_MockDiseaseEntry>> _cropDiseases = {
    'Tomato': [
      _MockDiseaseEntry('Tomato___Early_blight', 0.92, [
        PredictionItem(label: 'Tomato___Early_blight', confidence: 0.92),
        PredictionItem(label: 'Tomato___Target_Spot', confidence: 0.05),
        PredictionItem(label: 'Tomato___Septoria_leaf_spot', confidence: 0.03),
      ]),
      _MockDiseaseEntry('Tomato___Late_blight', 0.88, [
        PredictionItem(label: 'Tomato___Late_blight', confidence: 0.88),
        PredictionItem(label: 'Tomato___Early_blight', confidence: 0.08),
        PredictionItem(label: 'Tomato___Leaf_Mold', confidence: 0.04),
      ]),
      _MockDiseaseEntry('Tomato___Bacterial_spot', 0.85, [
        PredictionItem(label: 'Tomato___Bacterial_spot', confidence: 0.85),
        PredictionItem(label: 'Tomato___Septoria_leaf_spot', confidence: 0.10),
        PredictionItem(label: 'Tomato___healthy', confidence: 0.05),
      ]),
      _MockDiseaseEntry('Tomato___healthy', 0.96, [
        PredictionItem(label: 'Tomato___healthy', confidence: 0.96),
        PredictionItem(label: 'Tomato___Early_blight', confidence: 0.03),
        PredictionItem(label: 'Tomato___Target_Spot', confidence: 0.01),
      ]),
      // Low confidence edge case
      _MockDiseaseEntry('Tomato___Target_Spot', 0.52, [
        PredictionItem(label: 'Tomato___Target_Spot', confidence: 0.52),
        PredictionItem(label: 'Tomato___Early_blight', confidence: 0.31),
        PredictionItem(label: 'Tomato___Bacterial_spot', confidence: 0.17),
      ]),
    ],
    'Potato': [
      _MockDiseaseEntry('Potato___Early_blight', 0.89, [
        PredictionItem(label: 'Potato___Early_blight', confidence: 0.89),
        PredictionItem(label: 'Potato___Late_blight', confidence: 0.08),
        PredictionItem(label: 'Potato___healthy', confidence: 0.03),
      ]),
      _MockDiseaseEntry('Potato___Late_blight', 0.91, [
        PredictionItem(label: 'Potato___Late_blight', confidence: 0.91),
        PredictionItem(label: 'Potato___Early_blight', confidence: 0.06),
        PredictionItem(label: 'Potato___healthy', confidence: 0.03),
      ]),
      _MockDiseaseEntry('Potato___healthy', 0.97, [
        PredictionItem(label: 'Potato___healthy', confidence: 0.97),
        PredictionItem(label: 'Potato___Early_blight', confidence: 0.03),
      ]),
    ],
    'Corn': [
      _MockDiseaseEntry('Corn___Common_rust', 0.93, [
        PredictionItem(label: 'Corn___Common_rust', confidence: 0.93),
        PredictionItem(label: 'Corn___Northern_Leaf_Blight', confidence: 0.05),
        PredictionItem(label: 'Corn___healthy', confidence: 0.02),
      ]),
      _MockDiseaseEntry('Corn___Northern_Leaf_Blight', 0.87, [
        PredictionItem(label: 'Corn___Northern_Leaf_Blight', confidence: 0.87),
        PredictionItem(label: 'Corn___Common_rust', confidence: 0.09),
        PredictionItem(label: 'Corn___healthy', confidence: 0.04),
      ]),
      _MockDiseaseEntry('Corn___healthy', 0.95, [
        PredictionItem(label: 'Corn___healthy', confidence: 0.95),
        PredictionItem(label: 'Corn___Common_rust', confidence: 0.05),
      ]),
    ],
    'Pepper (Bell)': [
      _MockDiseaseEntry('Pepper__bell___Bacterial_spot', 0.86, [
        PredictionItem(
            label: 'Pepper__bell___Bacterial_spot', confidence: 0.86),
        PredictionItem(label: 'Pepper__bell___healthy', confidence: 0.14),
      ]),
      _MockDiseaseEntry('Pepper__bell___healthy', 0.94, [
        PredictionItem(label: 'Pepper__bell___healthy', confidence: 0.94),
        PredictionItem(
            label: 'Pepper__bell___Bacterial_spot', confidence: 0.06),
      ]),
    ],
    'Rice': [
      _MockDiseaseEntry('Rice___Leaf_Blast', 0.89, [
        PredictionItem(label: 'Rice___Leaf_Blast', confidence: 0.89),
        PredictionItem(label: 'Rice___Brown_Spot', confidence: 0.08),
        PredictionItem(label: 'Rice___healthy', confidence: 0.03),
      ]),
      _MockDiseaseEntry('Rice___Brown_Spot', 0.87, [
        PredictionItem(label: 'Rice___Brown_Spot', confidence: 0.87),
        PredictionItem(label: 'Rice___Leaf_Blast', confidence: 0.09),
        PredictionItem(label: 'Rice___healthy', confidence: 0.04),
      ]),
      _MockDiseaseEntry('Rice___healthy', 0.98, [
        PredictionItem(label: 'Rice___healthy', confidence: 0.98),
        PredictionItem(label: 'Rice___Brown_Spot', confidence: 0.02),
      ]),
    ],
  };

  @override
  Future<void> initialize() async {
    // Simulate loading model into memory
    await Future.delayed(const Duration(milliseconds: 300));
    _isLoaded = true;
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

    // Emulate on-device inference latency (1.0 to 1.5 seconds)
    await Future.delayed(const Duration(milliseconds: 1200));

    final normalizedCrop = cropHint?.trim().toLowerCase();
    final cropAlias = _cropAliases[normalizedCrop];
    final selectedCrop = normalizedCrop == null || normalizedCrop.isEmpty
        ? 'Tomato'
        : _cropDiseases.keys.cast<String?>().firstWhere(
              (crop) =>
                  crop?.toLowerCase() ==
                  (cropAlias ?? normalizedCrop).toLowerCase(),
              orElse: () => null,
            );
    if (selectedCrop == null) {
      throw UnsupportedError(
        'The demo model only supports ${_cropDiseases.keys.join(', ')}.',
      );
    }

    final diseases = _cropDiseases[selectedCrop]!;

    // Select disease entry
    _MockDiseaseEntry entry;
    if (imagePath.toLowerCase().contains('low_conf') ||
        imagePath.toLowerCase().contains('blurry')) {
      final candidates = diseases.reversed.take(3).toList();
      final probabilities = <double>[0.48, 0.32, 0.20];
      final predictions = candidates.indexed
          .map(
            (item) => PredictionItem(
              label: item.$2.label,
              confidence: probabilities[item.$1],
            ),
          )
          .toList();
      entry = _MockDiseaseEntry(
        candidates.first.label,
        probabilities.first,
        predictions,
      );
    } else {
      entry = diseases[_random.nextInt(diseases.length)];
    }

    final isLow = entry.confidence < AppConfig.lowConfidenceThreshold;
    final now = DateTime.now().toUtc().toIso8601String();
    final predictionId =
        'pred-${DateTime.now().millisecondsSinceEpoch}-${_random.nextInt(9999)}';

    return InferenceResult(
      predictionId: predictionId,
      crop: selectedCrop,
      diseaseLabel: entry.label,
      confidence: entry.confidence,
      topPredictions: entry.topPredictions,
      isLowConfidence: isLow,
      modelVersion: '${AppConfig.defaultModelVersion}-mock',
      inferenceTimestamp: now,
    );
  }

  @override
  void dispose() {
    _isLoaded = false;
  }
}

class _MockDiseaseEntry {
  final String label;
  final double confidence;
  final List<PredictionItem> topPredictions;

  const _MockDiseaseEntry(this.label, this.confidence, this.topPredictions);
}
