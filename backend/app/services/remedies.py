"""Agronomic remedy guidance knowledge base for AgroLens."""

from typing import Any

DEFAULT_REMEDY = {
    "common_name": "General Foliar Condition",
    "crop": "Unknown",
    "severity": "Moderate",
    "description": "Foliar spotting or discoloration detected on the leaf tissue.",
    "cultural_practices": [
        "Avoid overhead irrigation; water at the base of the plant.",
        "Prune and dispose of visibly affected foliage.",
        "Ensure adequate plant spacing for adequate air circulation.",
    ],
    "biological_controls": [
        "Apply neem oil (0.5%) or Trichoderma viride bio-fungicide formulation.",
    ],
    "chemical_guidelines": [
        "Consult your local Krishi Vigyan Kendra (KVK) or extension officer for registered crop-specific fungicides.",
    ],
    "next_steps": [
        "Isolate heavily diseased plants and monitor new leaf growth.",
    ],
    "disclaimer": "AgroLens provides decision-support information. Always verify with local agricultural extension officers before applying chemical inputs.",
}

REMEDIES_DATABASE: dict[str, dict[str, Any]] = {
    "Background_without_leaves": {
        "common_name": "No Crop Leaf Detected",
        "crop": "Non-plant",
        "severity": "None",
        "description": "The uploaded photograph does not contain a recognizable plant leaf. Vehicles, household items, animals, human faces, or plain backgrounds cannot be diagnosed.",
        "cultural_practices": [],
        "biological_controls": [],
        "chemical_guidelines": [],
        "next_steps": [
            "Take a close-up, focused photo of a single agricultural crop leaf in daylight.",
            "Ensure the leaf fills at least 60% of the camera frame.",
        ],
        "disclaimer": "Please take a photo of an agricultural crop leaf (Tomato, Potato, Corn, Pepper, Grape, etc.).",
    },
    "Potato___Early_blight": {
        "common_name": "Potato Early Blight (Alternaria solani)",
        "crop": "Potato",
        "severity": "Moderate",
        "description": "Fungal pathogen causing circular to angular dark brown necrotic spots with concentric rings ('target board' pattern) on older lower leaves.",
        "cultural_practices": [
            "Rotate crops with non-solanaceous crops (e.g. cereals, legumes) for at least 2-3 years.",
            "Maintain wide ridge spacing to maximize canopy aeration and rapid drying.",
            "Avoid overhead irrigation; use drip irrigation to prevent prolonged leaf wetness.",
            "Destroy crop debris and infected haulms after harvesting.",
        ],
        "biological_controls": [
            "Foliar spray of Trichoderma harzianum or Bacillus subtilis @ 5-10 g/L.",
            "Neem Seed Kernel Extract (NSKE 5%) spray during early vegetative stage.",
        ],
        "chemical_guidelines": [
            "Protective spray of Mancozeb 75 WP @ 2.0-2.5 g/L of water at first symptom onset.",
            "For active spread: Chlorothalonil 75 WP @ 2.0 g/L or Azoxystrobin 23 SC @ 1.0 ml/L.",
            "Ensure thorough coverage of both upper and lower leaf surfaces.",
        ],
        "next_steps": [
            "Prune severely blighted bottom leaves to prevent upward spore splash.",
            "Apply protective fungicide spray before expected humid or rainy spells.",
            "Inspect tubers at harvest for brown corky dry rot.",
        ],
        "disclaimer": "Adhere strictly to waiting periods before harvesting after chemical sprays.",
    },
    "Potato___Late_blight": {
        "common_name": "Potato Late Blight (Phytophthora infestans)",
        "crop": "Potato",
        "severity": "Severe",
        "description": "Devastating water-mold pathogen causing water-soaked pale green lesions that rapidly turn purplish-black with white cottony mildew under the leaf in cool humid conditions.",
        "cultural_practices": [
            "Plant only certified, disease-free seed tubers.",
            "Ensure thorough earthing up (15-20 cm high ridges) to prevent spores washing into soil.",
            "Destroy volunteer potato plants and cull piles near fields.",
            "De-haulm (cut foliage) 10-14 days prior to digging tubers.",
        ],
        "biological_controls": [
            "Preventive application of Pseudomonas fluorescens @ 10 g/L as foliar and seed treatment.",
        ],
        "chemical_guidelines": [
            "Protective contact spray: Mancozeb 75 WP @ 2.5 g/L or Copper Oxychloride 50 WP @ 3.0 g/L.",
            "Systemic curative spray at disease onset: Metalaxyl 8% + Mancozeb 64% WP (Ridomil MZ @ 2.5 g/L) or Cymoxanil + Mancozeb @ 2.0 g/L.",
            "Alternate fungicides with different modes of action to prevent resistance.",
        ],
        "next_steps": [
            "Spray entire field immediately when cool (<20 C) and humid (>90% RH) weather persists.",
            "Halt overhead irrigation immediately.",
            "Do not harvest during wet soil conditions to avoid tuber rot in storage.",
        ],
        "disclaimer": "Late blight spreads rapidly; prompt community-wide preventive spraying is essential.",
    },
    "Potato___healthy": {
        "common_name": "Healthy Potato Foliage",
        "crop": "Potato",
        "severity": "None (Healthy)",
        "description": "Vigorous, dark green potato foliage free from leaf spots, chlorosis, or mildew.",
        "cultural_practices": [
            "Maintain balanced N-P-K fertilizer application; avoid excess nitrogen.",
            "Perform regular hilling up to protect developing tubers from sunlight and pests.",
            "Maintain uniform soil moisture without waterlogging.",
        ],
        "biological_controls": [
            "Preventive soil drench of Trichoderma viride enriched farmyard manure.",
        ],
        "chemical_guidelines": [
            "No chemical fungicides or bactericides required at this stage.",
        ],
        "next_steps": [
            "Continue scouting lower canopy twice a week for early blight or aphid signs.",
            "Ensure clean weeding around field margins.",
        ],
        "disclaimer": "Maintain preventive hygiene to keep the crop healthy until harvest.",
    },
    "Tomato___Early_blight": {
        "common_name": "Tomato Early Blight (Alternaria solani)",
        "crop": "Tomato",
        "severity": "Moderate",
        "description": "Dark brown concentric target-like rings on older leaves, with yellow halos surrounding lesions.",
        "cultural_practices": [
            "Stake plants and prune bottom suckers up to 30 cm from the ground for ventilation.",
            "Use drip irrigation and mulch beds with straw or plastic film.",
            "Rotate away from solanaceous crops (potato, brinjal, chilli) for 2 years.",
        ],
        "biological_controls": [
            "Trichoderma viride foliar spray @ 5 g/L with wetting agent.",
            "Neem oil spray (3000 ppm @ 3 ml/L) for protective barrier.",
        ],
        "chemical_guidelines": [
            "Mancozeb 75 WP @ 2.5 g/L or Chlorothalonil @ 2 g/L at early signs.",
            "Difenoconazole 25 EC @ 0.5 ml/L for curative action.",
        ],
        "next_steps": [
            "Remove and destroy lower affected leaves.",
            "Maintain consistent soil moisture to prevent plant stress.",
        ],
        "disclaimer": "Follow safe harvest interval after any fungicide spray.",
    },
    "Tomato___Late_blight": {
        "common_name": "Tomato Late Blight (Phytophthora infestans)",
        "crop": "Tomato",
        "severity": "Severe",
        "description": "Large irregular greenish-grey water-soaked spots on leaves and stems, turning brown and papery, with white fungal growth underneath.",
        "cultural_practices": [
            "Ensure full sun exposure and wide row spacing.",
            "Promptly rogue out and bury severely infected plants away from field.",
        ],
        "biological_controls": [
            "Pseudomonas fluorescens @ 10 g/L preventive spray.",
        ],
        "chemical_guidelines": [
            "Metalaxyl + Mancozeb (Ridomil MZ @ 2.5 g/L) or Dimethomorph 50 WP @ 1 g/L.",
        ],
        "next_steps": [
            "Immediate spray application required upon first observation.",
        ],
        "disclaimer": "Do not harvest fruit with late blight rot.",
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "common_name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "crop": "Tomato",
        "severity": "Severe",
        "description": "Upward curling and cupping of leaflets, marked yellowing (chlorosis) of leaf margins, stunting of plants, and flower drop.",
        "cultural_practices": [
            "Use yellow sticky traps (15-20 traps/acre) to monitor and trap whitefly vectors.",
            "Grow vector-resistant tomato hybrids (e.g. Arka Rakshak, Arka Samrat).",
            "Erect nylon insect-proof net (40-50 mesh) in nursery beds.",
        ],
        "biological_controls": [
            "Spray neem formulation (Azadirachtin 1% @ 2 ml/L) to repel whiteflies.",
            "Encourage natural predators like ladybird beetles and mirid bugs.",
        ],
        "chemical_guidelines": [
            "Control whitefly vector: Imidacloprid 17.8 SL @ 0.3 ml/L or Thiamethoxam 25 WG @ 0.3 g/L.",
        ],
        "next_steps": [
            "Rogue out and destroy viral infected plants immediately to prevent whitefly transmission.",
        ],
        "disclaimer": "Viral diseases cannot be cured once inside the plant; focus on vector control.",
    },
    "Tomato___healthy": {
        "common_name": "Healthy Tomato Foliage",
        "crop": "Tomato",
        "severity": "None (Healthy)",
        "description": "Dark green, upright tomato foliage with active vegetative growth and no leaf lesions or virus symptoms.",
        "cultural_practices": [
            "Maintain trellis support and consistent drip irrigation schedule.",
            "Apply balanced fertilizer with micronutrients (Calcium/Boron) to prevent blossom end rot.",
        ],
        "biological_controls": ["Preventive soil application of beneficial mycorrhizae."],
        "chemical_guidelines": ["No chemical treatment needed."],
        "next_steps": ["Continue standard agronomic monitoring."],
        "disclaimer": "Good canopy management ensures optimum fruit set.",
    },
    "Corn___Common_rust": {
        "common_name": "Corn Common Rust (Puccinia sorghi)",
        "crop": "Corn",
        "severity": "Moderate",
        "description": "Small, powdery cinnamon-brown to dark reddish-brown pustules scattered across both leaf surfaces.",
        "cultural_practices": [
            "Plant rust-tolerant hybrid maize varieties.",
            "Early planting to avoid high humidity late-season rust spore showers.",
        ],
        "biological_controls": ["Foliar spray of Trichoderma @ 5 g/L."],
        "chemical_guidelines": [
            "Spray Mancozeb 75 WP @ 2.5 g/L or Propiconazole 25 EC @ 1 ml/L at first appearance.",
        ],
        "next_steps": ["Inspect upper ear leaf canopy weekly."],
        "disclaimer": "Treat before pustules cover more than 5% of leaf area above the ear.",
    },
    "Corn___healthy": {
        "common_name": "Healthy Corn Foliage",
        "crop": "Corn",
        "severity": "None (Healthy)",
        "description": "Vibrant green maize leaves with no rust pustules or blight lesions.",
        "cultural_practices": ["Side-dress nitrogen at knee-high and tasseling stages."],
        "biological_controls": [],
        "chemical_guidelines": ["No chemical application needed."],
        "next_steps": ["Monitor whorls for fall armyworm larvae."],
        "disclaimer": "Maintain optimum soil moisture through grain-filling stage.",
    },
}


def get_remedy(disease_label: str) -> dict[str, Any]:
    """Retrieve remedy details for a given disease label."""
    if disease_label in REMEDIES_DATABASE:
        return REMEDIES_DATABASE[disease_label]
    
    # Check for healthy variations
    if "healthy" in disease_label.lower():
        crop = disease_label.split("___")[0].replace("_", " ") if "___" in disease_label else "Crop"
        return {
            "common_name": f"Healthy {crop} Foliage",
            "crop": crop,
            "severity": "None (Healthy)",
            "description": f"Vigorous green {crop} foliage free of active disease lesions or viral symptoms.",
            "cultural_practices": ["Maintain standard balanced fertilization and weed management."],
            "biological_controls": ["Apply organic bio-fertilizers and compost."],
            "chemical_guidelines": ["No chemical treatment required."],
            "next_steps": ["Continue routine scouting."],
            "disclaimer": "Maintain crop hygiene.",
        }

    # Extract crop from label
    crop = disease_label.split("___")[0].replace("_", " ") if "___" in disease_label else "Crop"
    disease = disease_label.split("___")[1].replace("_", " ") if "___" in disease_label else disease_label
    result = dict(DEFAULT_REMEDY)
    result["crop"] = crop
    result["common_name"] = f"{crop} {disease}"
    result["description"] = f"Symptoms indicative of {disease} observed on {crop} leaf foliage."
    return result
