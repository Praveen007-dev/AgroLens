import '../models/scan_record.dart';

/// Abstract API service contract for communication with the AgroLens FastAPI backend (Member 3).
/// Adheres to coordination/PROJECT_SPEC.md and data collection guidelines.
abstract class ScanApiService {
  /// Submits a scan record with AI prediction, optional farmer feedback, and optional location.
  /// Returns true if successfully acknowledged by the backend.
  Future<bool> submitScan(ScanRecord record);

  /// Submits a batch of offline-queued scan records when connection is restored.
  Future<int> submitBatch(List<ScanRecord> records);

  /// Updates farmer feedback on an existing scan record.
  Future<bool> updateFeedback(String scanId, Map<String, dynamic> feedbackData);

  /// Retrieves previously recorded scans from the backend.
  Future<List<ScanRecord>> fetchScans({int limit = 20, int offset = 0});

  /// Retrieves a specific scan record by ID.
  Future<ScanRecord?> getScan(String scanId);

  /// Health check endpoint to verify backend connectivity.
  Future<bool> checkHealth();
}
