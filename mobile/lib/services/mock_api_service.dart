import '../models/scan_record.dart';
import '../models/inference_result.dart';
import '../models/farmer_feedback.dart';
import '../models/expert_verification.dart';
import 'api_service.dart';

/// Mock API Service simulating Member 3's FastAPI backend.
/// Enables offline testing, demo runs, and zero-dependency UI development.
class MockApiServiceImpl implements ScanApiService {
  final List<ScanRecord> _records = [];

  MockApiServiceImpl() {
    _populateSeedData();
  }

  void _populateSeedData() {
    // Seed realistic historical scans
    _records.addAll([
      ScanRecord(
        scanId: 'scan-demo-001',
        timestamp:
            DateTime.now().subtract(const Duration(hours: 3)).toIso8601String(),
        crop: 'Tomato',
        imagePath: null,
        aiPrediction: const InferenceResult(
          predictionId: 'pred-001',
          crop: 'Tomato',
          diseaseLabel: 'Tomato___Early_blight',
          confidence: 0.942,
          topPredictions: [
            PredictionItem(label: 'Tomato___Early_blight', confidence: 0.942),
            PredictionItem(label: 'Tomato___Target_Spot', confidence: 0.038),
            PredictionItem(
                label: 'Tomato___Septoria_leaf_spot', confidence: 0.020),
          ],
          isLowConfidence: false,
          modelVersion: 'agrolens-v1.0.0',
          inferenceTimestamp: '2026-11-04T09:00:00Z',
        ),
        farmerFeedback: FarmerFeedback(
          isConfirmed: true,
          notes:
              'Lower leaves turning yellow with dark target-like concentric rings.',
          submittedAt: DateTime.now()
              .subtract(const Duration(hours: 2, minutes: 45))
              .toIso8601String(),
        ),
        expertVerification: const ExpertVerification(
          isVerified: true,
          verifiedBy: 'Dr. Ramesh Kumar (Agronomist, KVK)',
          diagnosis: 'Alternaria solani confirmed.',
          notes: 'Typical early blight symptoms on older foliage.',
          verifiedAt: '2026-11-04T10:15:00Z',
        ),
        location: const ScanLocation(
          latitude: 13.0827,
          longitude: 77.5877,
          region: 'Hessaraghatta, Bengaluru Rural',
          hasConsent: true,
        ),
        syncStatus: SyncStatus.synced,
      ),
      ScanRecord(
        scanId: 'scan-demo-002',
        timestamp: DateTime.now()
            .subtract(const Duration(days: 1, hours: 2))
            .toIso8601String(),
        crop: 'Potato',
        imagePath: null,
        aiPrediction: const InferenceResult(
          predictionId: 'pred-002',
          crop: 'Potato',
          diseaseLabel: 'Potato___Late_blight',
          confidence: 0.895,
          topPredictions: [
            PredictionItem(label: 'Potato___Late_blight', confidence: 0.895),
            PredictionItem(label: 'Potato___Early_blight', confidence: 0.082),
            PredictionItem(label: 'Potato___healthy', confidence: 0.023),
          ],
          isLowConfidence: false,
          modelVersion: 'agrolens-v1.0.0',
          inferenceTimestamp: '2026-11-03T10:00:00Z',
        ),
        farmerFeedback: FarmerFeedback(
          isConfirmed: true,
          notes: 'Water soaked lesions spreading fast after overnight rain.',
          submittedAt: DateTime.now()
              .subtract(const Duration(days: 1, hours: 1))
              .toIso8601String(),
        ),
        expertVerification: null,
        location: const ScanLocation(
          latitude: 13.3409,
          longitude: 77.1010,
          region: 'Tumakuru',
          hasConsent: true,
        ),
        syncStatus: SyncStatus.synced,
      ),
      ScanRecord(
        scanId: 'scan-demo-003',
        timestamp:
            DateTime.now().subtract(const Duration(days: 2)).toIso8601String(),
        crop: 'Corn',
        imagePath: null,
        aiPrediction: const InferenceResult(
          predictionId: 'pred-003',
          crop: 'Corn',
          diseaseLabel: 'Corn___Common_rust',
          confidence: 0.931,
          topPredictions: [
            PredictionItem(label: 'Corn___Common_rust', confidence: 0.931),
            PredictionItem(
                label: 'Corn___Northern_Leaf_Blight', confidence: 0.051),
            PredictionItem(label: 'Corn___healthy', confidence: 0.018),
          ],
          isLowConfidence: false,
          modelVersion: 'agrolens-v1.0.0',
          inferenceTimestamp: '2026-11-02T14:30:00Z',
        ),
        farmerFeedback: null,
        expertVerification: null,
        location: null,
        syncStatus: SyncStatus.synced,
      ),
      ScanRecord(
        scanId: 'scan-demo-004',
        timestamp:
            DateTime.now().subtract(const Duration(days: 3)).toIso8601String(),
        crop: 'Tomato',
        imagePath: null,
        aiPrediction: const InferenceResult(
          predictionId: 'pred-004',
          crop: 'Tomato',
          diseaseLabel: 'Tomato___Target_Spot',
          confidence: 0.485,
          topPredictions: [
            PredictionItem(label: 'Tomato___Target_Spot', confidence: 0.485),
            PredictionItem(label: 'Tomato___Early_blight', confidence: 0.320),
            PredictionItem(label: 'Tomato___Bacterial_spot', confidence: 0.195),
          ],
          isLowConfidence: true,
          modelVersion: 'agrolens-v1.0.0',
          inferenceTimestamp: '2026-11-01T11:15:00Z',
        ),
        farmerFeedback: FarmerFeedback(
          isConfirmed: false,
          correctedLabel: 'Tomato___Bacterial_spot',
          notes:
              'Leaf lesions look more like bacterial specks with yellow halos.',
          submittedAt: DateTime.now()
              .subtract(const Duration(days: 3))
              .toIso8601String(),
        ),
        expertVerification: null,
        location: const ScanLocation(
          latitude: 12.9716,
          longitude: 77.5946,
          region: 'Bengaluru South',
          hasConsent: true,
        ),
        syncStatus: SyncStatus.synced,
      ),
    ]);
  }

  @override
  Future<bool> submitScan(ScanRecord record) async {
    // Simulate API network roundtrip
    await Future.delayed(const Duration(milliseconds: 600));

    // Update or insert
    final index = _records.indexWhere((r) => r.scanId == record.scanId);
    if (index >= 0) {
      _records[index] = record.copyWith(syncStatus: SyncStatus.synced);
    } else {
      _records.insert(0, record.copyWith(syncStatus: SyncStatus.synced));
    }
    return true;
  }

  @override
  Future<int> submitBatch(List<ScanRecord> records) async {
    await Future.delayed(const Duration(milliseconds: 800));
    int syncedCount = 0;
    for (final record in records) {
      final success = await submitScan(record);
      if (success) syncedCount++;
    }
    return syncedCount;
  }

  @override
  Future<bool> updateFeedback(
      String scanId, Map<String, dynamic> feedbackData) async {
    await Future.delayed(const Duration(milliseconds: 400));
    final index = _records.indexWhere((r) => r.scanId == scanId);
    if (index >= 0) {
      final existing = _records[index];
      _records[index] = existing.copyWith(
        farmerFeedback: FarmerFeedback.fromJson(feedbackData),
        syncStatus: SyncStatus.synced,
      );
      return true;
    }
    return false;
  }

  @override
  Future<List<ScanRecord>> fetchScans({int limit = 20, int offset = 0}) async {
    await Future.delayed(const Duration(milliseconds: 400));
    final list = _records.skip(offset).take(limit).toList();
    return list;
  }

  @override
  Future<ScanRecord?> getScan(String scanId) async {
    await Future.delayed(const Duration(milliseconds: 200));
    try {
      return _records.firstWhere((r) => r.scanId == scanId);
    } catch (_) {
      return null;
    }
  }

  @override
  Future<bool> checkHealth() async {
    await Future.delayed(const Duration(milliseconds: 150));
    return true;
  }
}
