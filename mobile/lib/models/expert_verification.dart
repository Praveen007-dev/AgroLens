/// Represents expert diagnosis or verification (e.g. from an agricultural extension officer or IIHR researcher).
/// Kept strictly separate from the AI prediction and farmer feedback.
class ExpertVerification {
  final bool isVerified;
  final String? verifiedBy;
  final String? diagnosis;
  final String? notes;
  final String? verifiedAt;

  const ExpertVerification({
    required this.isVerified,
    this.verifiedBy,
    this.diagnosis,
    this.notes,
    this.verifiedAt,
  });

  factory ExpertVerification.fromJson(Map<String, dynamic> json) {
    return ExpertVerification(
      isVerified: json['is_verified'] as bool? ?? false,
      verifiedBy: json['verified_by'] as String?,
      diagnosis: json['diagnosis'] as String?,
      notes: json['notes'] as String?,
      verifiedAt: json['verified_at'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'is_verified': isVerified,
      'verified_by': verifiedBy,
      'diagnosis': diagnosis,
      'notes': notes,
      'verified_at': verifiedAt,
    };
  }
}
