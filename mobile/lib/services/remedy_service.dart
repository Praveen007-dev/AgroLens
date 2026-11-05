import '../models/remedy_data.dart';

/// Agronomic remedy service providing scientific cultural, biological, and
/// chemical control guidance for identified plant diseases.
class RemedyService {
  static const Map<String, RemedyData> _database = {
    'Potato___Early_blight': RemedyData(
      diseaseLabel: 'Potato___Early_blight',
      commonName: 'Potato Early Blight (Alternaria solani)',
      crop: 'Potato',
      severity: 'Moderate',
      description:
          'Dark brown necrotic spots with concentric target-board rings on older lower leaves. Spreads via spore splash and high humidity.',
      culturalPractices: [
        'Rotate crops with non-solanaceous crops (cereals/legumes) for 2-3 years.',
        'Maintain wide ridge spacing to maximize airflow and canopy drying.',
        'Use drip irrigation; avoid overhead sprinkler watering.',
        'Destroy and bury crop residues after tuber harvest.',
      ],
      biologicalControls: [
        'Foliar spray of Trichoderma harzianum or Bacillus subtilis (5-10 g/L).',
        'Neem Seed Kernel Extract (NSKE 5%) spray at first vegetative stage.',
      ],
      chemicalGuidelines: [
        'Protective contact spray: Mancozeb 75 WP @ 2.0-2.5 g/L at early signs.',
        'Curative spray: Chlorothalonil 75 WP @ 2.0 g/L or Azoxystrobin 23 SC @ 1.0 ml/L.',
        'Ensure complete coverage of lower leaf canopy.',
      ],
      nextSteps: [
        'Prune severely diseased bottom leaves to stop upward infection spread.',
        'Apply protective spray before anticipated rain or fog.',
      ],
    ),
    'Potato___Late_blight': RemedyData(
      diseaseLabel: 'Potato___Late_blight',
      commonName: 'Potato Late Blight (Phytophthora infestans)',
      crop: 'Potato',
      severity: 'Severe',
      description:
          'Water-soaked dark purplish lesions with white cottony mildew under the leaf surface in cool, damp conditions. Spreads rapidly across entire fields.',
      culturalPractices: [
        'Plant only certified disease-free seed tubers.',
        'Maintain high earthing up (15-20 cm ridges) to shield tubers from spore wash.',
        'Rogue out and destroy infected volunteer potato plants.',
        'De-haulm (cut foliage) 10-14 days prior to tuber digging.',
      ],
      biologicalControls: [
        'Preventive spray of Pseudomonas fluorescens @ 10 g/L.',
      ],
      chemicalGuidelines: [
        'Protective spray: Mancozeb 75 WP @ 2.5 g/L or Copper Oxychloride 50 WP @ 3.0 g/L.',
        'Curative systemic spray: Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ @ 2.5 g/L) or Cymoxanil + Mancozeb @ 2.0 g/L.',
      ],
      nextSteps: [
        'Immediate whole-field preventive spray required upon first detection in the region.',
        'Halt overhead irrigation immediately.',
      ],
    ),
    'Potato___healthy': RemedyData(
      diseaseLabel: 'Potato___healthy',
      commonName: 'Healthy Potato Foliage',
      crop: 'Potato',
      severity: 'None',
      description:
          'Vigorous, dark green potato foliage free from leaf spots, chlorosis, or mildew.',
      culturalPractices: [
        'Maintain balanced N-P-K fertilizer application; avoid excess nitrogen.',
        'Continue regular hilling up to cover developing tubers.',
        'Maintain uniform soil moisture without waterlogging.',
      ],
      biologicalControls: [
        'Preventive soil application of Trichoderma viride enriched compost.',
      ],
      chemicalGuidelines: [
        'No chemical fungicides or inputs required at this stage.',
      ],
      nextSteps: [
        'Continue routine field scouting twice a week.',
      ],
    ),
    'Tomato___Early_blight': RemedyData(
      diseaseLabel: 'Tomato___Early_blight',
      commonName: 'Tomato Early Blight (Alternaria solani)',
      crop: 'Tomato',
      severity: 'Moderate',
      description:
          'Concentric target-like rings on older leaves with yellow chlorotic halos.',
      culturalPractices: [
        'Stake plants and prune bottom suckers up to 30 cm for ventilation.',
        'Mulch soil with straw or plastic to avoid soil splash.',
        'Rotate with non-solanaceous crops for 2 years.',
      ],
      biologicalControls: [
        'Trichoderma viride foliar spray @ 5 g/L.',
        'Neem oil spray (3000 ppm @ 3 ml/L) for protective barrier.',
      ],
      chemicalGuidelines: [
        'Mancozeb 75 WP @ 2.5 g/L or Chlorothalonil @ 2 g/L.',
        'Difenoconazole 25 EC @ 0.5 ml/L for curative action.',
      ],
      nextSteps: [
        'Remove and burn infected lower leaves.',
        'Water only at the root zone.',
      ],
    ),
    'Tomato___Late_blight': RemedyData(
      diseaseLabel: 'Tomato___Late_blight',
      commonName: 'Tomato Late Blight (Phytophthora infestans)',
      crop: 'Tomato',
      severity: 'Severe',
      description:
          'Large water-soaked lesions turning brown with white fungal growth on leaf undersides.',
      culturalPractices: [
        'Ensure open canopy and full sun exposure.',
        'Promptly remove and destroy heavily infected plants.',
      ],
      biologicalControls: [
        'Pseudomonas fluorescens @ 10 g/L.',
      ],
      chemicalGuidelines: [
        'Metalaxyl + Mancozeb (Ridomil MZ @ 2.5 g/L) or Dimethomorph 50 WP @ 1 g/L.',
      ],
      nextSteps: [
        'Immediate spray application upon first observation in weather conditions favorable to blight.',
      ],
    ),
    'Tomato___healthy': RemedyData(
      diseaseLabel: 'Tomato___healthy',
      commonName: 'Healthy Tomato Foliage',
      crop: 'Tomato',
      severity: 'None',
      description:
          'Dark green, upright tomato foliage with active vegetative growth and no lesions.',
      culturalPractices: [
        'Maintain trellis staking and drip irrigation schedule.',
        'Apply balanced fertilizer with calcium to avoid blossom end rot.',
      ],
      biologicalControls: ['Preventive mycorrhizal root inoculation.'],
      chemicalGuidelines: ['No chemical treatment needed.'],
      nextSteps: ['Continue routine crop care.'],
    ),
    'Background_without_leaves': RemedyData(
      diseaseLabel: 'Background_without_leaves',
      commonName: 'No Crop Leaf Detected',
      crop: 'Non-plant',
      severity: 'None',
      description:
          'The captured photograph does not contain a recognizable plant leaf. Non-plant objects (vehicles, furniture, animals, human faces) cannot be diagnosed.',
      culturalPractices: [],
      biologicalControls: [],
      chemicalGuidelines: [],
      nextSteps: [
        'Take a clear, focused close-up photo of a single crop leaf in natural light.',
        'Make sure the leaf covers most of the camera view.',
      ],
      disclaimer: 'Point your camera directly at a crop leaf to get a disease diagnosis.',
    ),
  };

  static RemedyData getRemedy(String diseaseLabel, {String? crop}) {
    if (_database.containsKey(diseaseLabel)) {
      return _database[diseaseLabel]!;
    }

    final isHealthy = diseaseLabel.toLowerCase().contains('healthy');
    final detectedCrop = crop ??
        (diseaseLabel.contains('___')
            ? diseaseLabel.split('___')[0].replaceAll('_', ' ')
            : 'Crop');
    final condition = diseaseLabel.contains('___')
        ? diseaseLabel.split('___')[1].replaceAll('_', ' ')
        : diseaseLabel.replaceAll('_', ' ');

    if (isHealthy) {
      return RemedyData(
        diseaseLabel: diseaseLabel,
        commonName: 'Healthy $detectedCrop Foliage',
        crop: detectedCrop,
        severity: 'None',
        description:
            'Vigorous green $detectedCrop foliage free of active disease lesions or symptoms.',
        culturalPractices: [
          'Maintain balanced nutrition and recommended plant spacing.',
          'Ensure regular irrigation without waterlogging.',
        ],
        biologicalControls: ['Apply organic compost or bio-fertilizers.'],
        chemicalGuidelines: ['No chemical inputs needed.'],
        nextSteps: ['Continue standard crop management and monitoring.'],
      );
    }

    return RemedyData(
      diseaseLabel: diseaseLabel,
      commonName: '$detectedCrop $condition',
      crop: detectedCrop,
      severity: 'Moderate',
      description:
          'Symptoms indicative of $condition observed on $detectedCrop leaf tissue.',
      culturalPractices: [
        'Avoid overhead watering; irrigate at root zone.',
        'Prune and destroy infected leaves to reduce spore spread.',
        'Ensure good air circulation between plants.',
      ],
      biologicalControls: [
        'Apply neem oil spray (3-5 ml/L) or Trichoderma viride formulation.',
      ],
      chemicalGuidelines: [
        'Consult your local Krishi Vigyan Kendra (KVK) for recommended fungicides for $detectedCrop in your agro-climatic zone.',
      ],
      nextSteps: [
        'Isolate heavily infected plants and monitor nearby rows.',
      ],
    );
  }
}
