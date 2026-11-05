import 'dart:typed_data';
import '../models/inference_result.dart';

/// Abstract service contract for AI crop disease inference.
/// Implementations must adhere strictly to contracts/inference_contract.json.
abstract class InferenceService {
  /// Initializes the model and label assets.
  Future<void> initialize();

  /// Runs inference on an image from the local filesystem or raw bytes.
  /// [imagePath] is the path to the captured or selected image.
  /// [cropHint] is an optional farmer-selected crop (e.g. "Tomato", "Potato").
  /// [imageBytes] are the optional raw bytes of the image (ideal for web).
  Future<InferenceResult> runInference({
    required String imagePath,
    String? cropHint,
    Uint8List? imageBytes,
  });

  /// Returns true if the inference engine is ready.
  bool get isModelLoaded;

  /// Releases resources held by the inference engine.
  void dispose();
}
