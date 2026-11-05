import 'dart:convert';

/// Top prediction candidate item adhering to contracts/inference_contract.json
class PredictionItem {
  final String label;
  final double confidence;

  const PredictionItem({
    required this.label,
    required this.confidence,
  });

  factory PredictionItem.fromJson(Map<String, dynamic> json) {
    return PredictionItem(
      label: json['label'] as String? ?? 'Unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'label': label,
      'confidence': double.parse(confidence.toStringAsFixed(4)),
    };
  }

  @override
  String toString() => 'PredictionItem(label: $label, confidence: ${(confidence * 100).toStringAsFixed(1)}%)';
}

/// Standard output format for AgroLens on-device crop disease and pest inference.
/// Strictly implements contracts/inference_contract.json
class InferenceResult {
  final String predictionId;
  final String crop;
  final String diseaseLabel;
  final double confidence; // Must be between 0.0 and 1.0
  final List<PredictionItem> topPredictions;
  final bool isLowConfidence;
  final String modelVersion;
  final String inferenceTimestamp; // ISO-8601

  const InferenceResult({
    required this.predictionId,
    required this.crop,
    required this.diseaseLabel,
    required this.confidence,
    required this.topPredictions,
    required this.isLowConfidence,
    required this.modelVersion,
    required this.inferenceTimestamp,
  });

  /// Factory constructor to deserialize from JSON matching contract
  factory InferenceResult.fromJson(Map<String, dynamic> json) {
    final rawTop = json['top_predictions'] as List<dynamic>? ?? [];
    final topList = rawTop
        .map((item) => PredictionItem.fromJson(item as Map<String, dynamic>))
        .toList();

    return InferenceResult(
      predictionId: json['prediction_id'] as String? ?? '',
      crop: json['crop'] as String? ?? 'Unknown',
      diseaseLabel: json['disease_label'] as String? ?? 'Unknown',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      topPredictions: topList,
      isLowConfidence: json['is_low_confidence'] as bool? ?? false,
      modelVersion: json['model_version'] as String? ?? 'unknown',
      inferenceTimestamp: json['inference_timestamp'] as String? ??
          DateTime.now().toIso8601String(),
    );
  }

  /// Serialize to JSON matching contract
  Map<String, dynamic> toJson() {
    return {
      'prediction_id': predictionId,
      'crop': crop,
      'disease_label': diseaseLabel,
      'confidence': double.parse(confidence.toStringAsFixed(4)),
      'top_predictions': topPredictions.map((p) => p.toJson()).toList(),
      'is_low_confidence': isLowConfidence,
      'model_version': modelVersion,
      'inference_timestamp': inferenceTimestamp,
    };
  }

  String toJsonString() => jsonEncode(toJson());

  /// Returns friendly formatted display name for the disease label
  String get formattedDiseaseName {
    // Labels often come formatted like 'Tomato___Early_blight' or 'Tomato___healthy'
    if (diseaseLabel.contains('___')) {
      final parts = diseaseLabel.split('___');
      if (parts.length > 1) {
        final condition = parts[1].replaceAll('_', ' ');
        return condition.toLowerCase() == 'healthy'
            ? 'Healthy Plant (No Disease Detected)'
            : condition;
      }
    }
    return diseaseLabel.replaceAll('_', ' ');
  }

  /// Returns formatted percentage string (e.g. "94.2%")
  String get formattedConfidence {
    return '${(confidence * 100).toStringAsFixed(1)}%';
  }
}
