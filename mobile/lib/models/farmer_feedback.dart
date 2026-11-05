/// Represents feedback provided by the farmer regarding an AI scan prediction.
/// Kept strictly separate from the AI prediction itself and any expert verification.
class FarmerFeedback {
  final bool isConfirmed;
  final String? correctedLabel;
  final String? notes;
  final String submittedAt; // ISO-8601

  const FarmerFeedback({
    required this.isConfirmed,
    this.correctedLabel,
    this.notes,
    required this.submittedAt,
  });

  factory FarmerFeedback.fromJson(Map<String, dynamic> json) {
    return FarmerFeedback(
      isConfirmed: json['is_confirmed'] as bool? ?? false,
      correctedLabel: json['corrected_label'] as String?,
      notes: json['notes'] as String?,
      submittedAt: json['submitted_at'] as String? ??
          DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'is_confirmed': isConfirmed,
      'corrected_label': correctedLabel,
      'notes': notes,
      'submitted_at': submittedAt,
    };
  }

  String get statusDisplay {
    if (isConfirmed) {
      return 'Farmer Confirmed';
    } else if (correctedLabel != null && correctedLabel!.isNotEmpty) {
      return 'Farmer Corrected ($correctedLabel)';
    } else {
      return 'Farmer Flagged Incorrect';
    }
  }
}
