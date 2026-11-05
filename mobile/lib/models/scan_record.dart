import 'dart:convert';
import 'inference_result.dart';
import 'farmer_feedback.dart';
import 'expert_verification.dart';

/// Sync status with backend
enum SyncStatus {
  pending,
  synced,
  failed,
}

/// Optional, consent-based geographic location
class ScanLocation {
  final double latitude;
  final double longitude;
  final String? region;
  final bool hasConsent;

  const ScanLocation({
    required this.latitude,
    required this.longitude,
    this.region,
    this.hasConsent = true,
  });

  factory ScanLocation.fromJson(Map<String, dynamic> json) {
    return ScanLocation(
      latitude: (json['latitude'] as num?)?.toDouble() ?? 0.0,
      longitude: (json['longitude'] as num?)?.toDouble() ?? 0.0,
      region: json['region'] as String?,
      hasConsent: json['has_consent'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'latitude': latitude,
      'longitude': longitude,
      'region': region,
      'has_consent': hasConsent,
    };
  }
}

/// Structured Scan Record adhering to coordination/PROJECT_SPEC.md.
/// Represents a complete scan event submitted to FastAPI backend and saved locally.
class ScanRecord {
  final String scanId;
  final String timestamp; // ISO-8601
  final String crop;
  final String? imagePath;
  final String? imageReference;
  final InferenceResult aiPrediction;
  final FarmerFeedback? farmerFeedback;
  final ExpertVerification? expertVerification;
  final ScanLocation? location;
  final SyncStatus syncStatus;
  final Map<String, dynamic>? metadata;

  const ScanRecord({
    required this.scanId,
    required this.timestamp,
    required this.crop,
    this.imagePath,
    this.imageReference,
    required this.aiPrediction,
    this.farmerFeedback,
    this.expertVerification,
    this.location,
    this.syncStatus = SyncStatus.pending,
    this.metadata,
  });

  ScanRecord copyWith({
    String? scanId,
    String? timestamp,
    String? crop,
    String? imagePath,
    String? imageReference,
    InferenceResult? aiPrediction,
    FarmerFeedback? farmerFeedback,
    ExpertVerification? expertVerification,
    ScanLocation? location,
    bool clearLocation = false,
    SyncStatus? syncStatus,
    Map<String, dynamic>? metadata,
  }) {
    return ScanRecord(
      scanId: scanId ?? this.scanId,
      timestamp: timestamp ?? this.timestamp,
      crop: crop ?? this.crop,
      imagePath: imagePath ?? this.imagePath,
      imageReference: imageReference ?? this.imageReference,
      aiPrediction: aiPrediction ?? this.aiPrediction,
      farmerFeedback: farmerFeedback ?? this.farmerFeedback,
      expertVerification: expertVerification ?? this.expertVerification,
      location: clearLocation ? null : location ?? this.location,
      syncStatus: syncStatus ?? this.syncStatus,
      metadata: metadata ?? this.metadata,
    );
  }

  factory ScanRecord.fromJson(Map<String, dynamic> json) {
    return ScanRecord(
      scanId: json['scan_id'] as String? ?? '',
      timestamp:
          json['timestamp'] as String? ?? DateTime.now().toIso8601String(),
      crop: json['crop'] as String? ?? 'Unknown',
      imagePath: json['image_path'] as String?,
      imageReference: json['image_reference'] as String?,
      aiPrediction: InferenceResult.fromJson(
        json['ai_prediction'] as Map<String, dynamic>? ?? {},
      ),
      farmerFeedback: json['farmer_feedback'] != null
          ? FarmerFeedback.fromJson(
              json['farmer_feedback'] as Map<String, dynamic>)
          : null,
      expertVerification: json['expert_verification'] != null
          ? ExpertVerification.fromJson(
              json['expert_verification'] as Map<String, dynamic>)
          : null,
      location: json['location'] != null
          ? ScanLocation.fromJson(json['location'] as Map<String, dynamic>)
          : null,
      syncStatus: _parseSyncStatus(json['sync_status'] as String?),
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  static SyncStatus _parseSyncStatus(String? status) {
    switch (status) {
      case 'synced':
        return SyncStatus.synced;
      case 'failed':
        return SyncStatus.failed;
      default:
        return SyncStatus.pending;
    }
  }

  Map<String, dynamic> toJson() {
    return {
      'scan_id': scanId,
      'timestamp': timestamp,
      'crop': crop,
      'image_path': imagePath,
      'image_reference': imageReference,
      'ai_prediction': aiPrediction.toJson(),
      'farmer_feedback': farmerFeedback?.toJson(),
      'expert_verification': expertVerification?.toJson(),
      'location': location?.toJson(),
      'sync_status': syncStatus.name,
      'metadata': metadata,
    };
  }

  String toJsonString() => jsonEncode(toJson());

  String get verificationSummary {
    if (expertVerification != null && expertVerification!.isVerified) {
      return 'Expert Verified';
    }
    if (farmerFeedback != null) {
      return farmerFeedback!.statusDisplay;
    }
    return 'AI Predicted (Unverified)';
  }
}
