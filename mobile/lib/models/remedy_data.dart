/// Model representing scientific and cultural remedy guidance for a crop disease.
/// Strictly adheres to agronomy safety guidelines: avoids fabricating dosages or unsupported claims.
class RemedyData {
  final String diseaseLabel;
  final String commonName;
  final String crop;
  final String severity; // Low, Moderate, High, Severe, None (Healthy)
  final String description;
  final List<String> culturalPractices;
  final List<String> biologicalControls;
  final List<String> chemicalGuidelines;
  final List<String> nextSteps;
  final String disclaimer;

  const RemedyData({
    required this.diseaseLabel,
    required this.commonName,
    required this.crop,
    required this.severity,
    required this.description,
    required this.culturalPractices,
    required this.biologicalControls,
    required this.chemicalGuidelines,
    required this.nextSteps,
    this.disclaimer =
        'Disclaimer: AgroLens is an agricultural decision-support prototype. Always verify with your local agricultural extension officer, Krishi Vigyan Kendra (KVK), or certified agronomist before purchasing or applying commercial chemical inputs.',
  });

  bool get isHealthy =>
      diseaseLabel.toLowerCase().contains('healthy') || severity == 'None';
}
