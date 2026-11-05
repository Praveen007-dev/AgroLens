import '../models/inference_result.dart';

/// Abstract service contract for on-device AI crop disease inference.
/// Implementations must adhere strictly to contracts/inference_contract.json.
abstract class InferenceService {
  /// Initializes the model and label assets.
  Future<void> initialize();

  /// Runs inference on an image from the local filesystem.
  /// [imagePath] is the absolute path to the captured or selected image.
  /// [cropHint] is an optional farmer-selected crop (e.g. "Tomato", "Potato").
  Future<InferenceResult> runInference({
    required String imagePath,
    String? cropHint,
  });

  /// Returns true if the inference engine is ready.
  bool get isModelLoaded;

  /// Releases resources held by the inference engine.
  void dispose();
}
