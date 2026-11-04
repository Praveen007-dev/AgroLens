import React, { useState, useMemo, useRef } from 'react';
import './App.css';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid, LineChart, Line, Legend
} from 'recharts';

import { MANDI_MARKETS, getMarketPriceData } from './services/mandiData';
import {
  INDIA_ALL_STATES_DISTRICTS,
  getDistrictWeatherData,
  AGRI_NEWS_SCHEMES
} from './services/weatherNewsData';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6'];

// Crop-specific historical surveillance incidence data (Field vs ICAR Benchmark)
const CROP_HISTORICAL_TRENDS = {
  Tomato: [
    { season: 'Kharif 2024', AgroLensObserved: 36, Baseline: 32 },
    { season: 'Rabi 2024-25', AgroLensObserved: 28, Baseline: 30 },
    { season: 'Summer 2025', AgroLensObserved: 20, Baseline: 24 },
    { season: 'Kharif 2025', AgroLensObserved: 44, Baseline: 39 },
    { season: 'Rabi 2025-26', AgroLensObserved: 32, Baseline: 31 },
    { season: 'Kharif 2026', AgroLensObserved: 48, Baseline: 42 }
  ],
  Potato: [
    { season: 'Kharif 2024', AgroLensObserved: 30, Baseline: 28 },
    { season: 'Rabi 2024-25', AgroLensObserved: 42, Baseline: 40 },
    { season: 'Summer 2025', AgroLensObserved: 15, Baseline: 18 },
    { season: 'Kharif 2025', AgroLensObserved: 35, Baseline: 33 },
    { season: 'Rabi 2025-26', AgroLensObserved: 46, Baseline: 44 },
    { season: 'Kharif 2026', AgroLensObserved: 38, Baseline: 36 }
  ],
  Paddy: [
    { season: 'Kharif 2024', AgroLensObserved: 48, Baseline: 45 },
    { season: 'Rabi 2024-25', AgroLensObserved: 22, Baseline: 25 },
    { season: 'Summer 2025', AgroLensObserved: 18, Baseline: 20 },
    { season: 'Kharif 2025', AgroLensObserved: 52, Baseline: 47 },
    { season: 'Rabi 2025-26', AgroLensObserved: 26, Baseline: 27 },
    { season: 'Kharif 2026', AgroLensObserved: 54, Baseline: 49 }
  ],
  Cotton: [
    { season: 'Kharif 2024', AgroLensObserved: 32, Baseline: 30 },
    { season: 'Rabi 2024-25', AgroLensObserved: 25, Baseline: 26 },
    { season: 'Summer 2025', AgroLensObserved: 14, Baseline: 16 },
    { season: 'Kharif 2025', AgroLensObserved: 38, Baseline: 35 },
    { season: 'Rabi 2025-26', AgroLensObserved: 29, Baseline: 28 },
    { season: 'Kharif 2026', AgroLensObserved: 41, Baseline: 37 }
  ],
  Corn: [
    { season: 'Kharif 2024', AgroLensObserved: 26, Baseline: 25 },
    { season: 'Rabi 2024-25', AgroLensObserved: 20, Baseline: 22 },
    { season: 'Summer 2025', AgroLensObserved: 16, Baseline: 18 },
    { season: 'Kharif 2025', AgroLensObserved: 31, Baseline: 29 },
    { season: 'Rabi 2025-26', AgroLensObserved: 24, Baseline: 24 },
    { season: 'Kharif 2026', AgroLensObserved: 34, Baseline: 32 }
  ]
};

// Crop-specific diagnostic metrics compared with institutional standards
const CROP_BENCHMARK_METRICS = {
  Tomato: [
    { metric: 'Accuracy', AgroLens: 92, Benchmark: 90 },
    { metric: 'Precision', AgroLens: 89, Benchmark: 87 },
    { metric: 'Recall', AgroLens: 94, Benchmark: 91 },
    { metric: 'F1-Score', AgroLens: 91, Benchmark: 89 }
  ],
  Potato: [
    { metric: 'Accuracy', AgroLens: 88, Benchmark: 86 },
    { metric: 'Precision', AgroLens: 86, Benchmark: 84 },
    { metric: 'Recall', AgroLens: 90, Benchmark: 88 },
    { metric: 'F1-Score', AgroLens: 88, Benchmark: 86 }
  ],
  Paddy: [
    { metric: 'Accuracy', AgroLens: 95, Benchmark: 93 },
    { metric: 'Precision', AgroLens: 93, Benchmark: 91 },
    { metric: 'Recall', AgroLens: 96, Benchmark: 94 },
    { metric: 'F1-Score', AgroLens: 94, Benchmark: 92 }
  ],
  Cotton: [
    { metric: 'Accuracy', AgroLens: 82, Benchmark: 85 },
    { metric: 'Precision', AgroLens: 80, Benchmark: 82 },
    { metric: 'Recall', AgroLens: 84, Benchmark: 86 },
    { metric: 'F1-Score', AgroLens: 82, Benchmark: 84 }
  ],
  Corn: [
    { metric: 'Accuracy', AgroLens: 89, Benchmark: 88 },
    { metric: 'Precision', AgroLens: 87, Benchmark: 86 },
    { metric: 'Recall', AgroLens: 91, Benchmark: 89 },
    { metric: 'F1-Score', AgroLens: 89, Benchmark: 87 }
  ]
};

// Symmetrical 5-point Agronomic Guide
const AGRONOMIC_GUIDE = {
  "Early Blight": {
    crop: "Tomato / Potato",
    soil: [
      { label: "Soil Texture & Depth", text: "Deep, well-aerated sandy loam or clay loam rich in organic matter (depth > 45 cm)." },
      { label: "Optimal pH Range", text: "6.0 – 6.8 (Avoid high alkalinity; slightly acidic enhances phosphorus absorption)." },
      { label: "Drainage & Aeration", text: "High percolation, well-draining; avoid waterlogged beds or hardpan subsoils." },
      { label: "Nutrient Dynamics (NPK)", text: "Requires balanced N-P-K (120:60:60 kg/ha); ensure calcium (>0.2%) to prevent rot." },
      { label: "Organic Amendments", text: "0.5% – 0.8% organic carbon; incorporate well-rotted FYM @ 20–25 tonnes/ha." }
    ],
    precautions: [
      { label: "Solarization & Beds", text: "Cover nursery beds with 25-micron polyethylene sheets for 30–45 days in peak summer." },
      { label: "Biological Seed Inoculation", text: "Treat seedlings with Trichoderma harzianum or T. viride @ 5g/kg seed or 10g/L root dip." },
      { label: "Canopy & Field Sanitation", text: "Prune lower leaves up to 20 cm from ground to prevent soil splash; burn infected debris." },
      { label: "Moisture & Spacing Protocol", text: "Maintain 60x45 cm plant spacing and utilize drip lines to minimize leaf wetness duration." },
      { label: "Protective Foliar Defense", text: "Apply prophylactic sprays of Mancozeb (0.2%) at first detection of lower-leaf concentric rings." }
    ]
  },
  "Late Blight": {
    crop: "Tomato / Potato",
    soil: [
      { label: "Soil Texture & Depth", text: "Loose, crumbly silt loam or light alluvial soil with high porosity and friability." },
      { label: "Optimal pH Range", text: "5.5 – 6.5 (Neutral to slightly acidic; avoid compacted calcareous soils)." },
      { label: "Drainage & Aeration", text: "Requires excellent internal aeration; stagnant moisture (>12 hrs) triggers oospore germination." },
      { label: "Nutrient Dynamics (NPK)", text: "Avoid high early nitrogen; maintain potassium to reinforce epidermal cell walls." },
      { label: "Organic Amendments", text: ">0.75% organic carbon; apply vermicompost @ 5 t/ha to enrich antagonistic microflora." }
    ],
    precautions: [
      { label: "Certified Clean Tubers", text: "Use certified disease-free seed tubers; reject lots exhibiting internal vascular browning." },
      { label: "Prophylactic Spray Timing", text: "Apply Mancozeb (0.2%) or Copper Oxychloride (0.25%) before forecast high-humidity spells." },
      { label: "Field Sanitation & Cull Piles", text: "Destroy and deeply bury all volunteer solanaceous hosts and discard piles before flowering." },
      { label: "Irrigation Regulation", text: "Regulate furrow water; strictly avoid late-afternoon or overhead night sprinkling." },
      { label: "Post-Infection Mitigation", text: "If blighted canopy exceeds 5%, switch to systemic translaminar fungicides (Cymoxanil/Metalaxyl)." }
    ]
  },
  "Bacterial Blight": {
    crop: "Cotton",
    soil: [
      { label: "Soil Texture & Depth", text: "Deep medium to heavy black cotton soils (Vertisols) or fertile alluvial loam." },
      { label: "Optimal pH Range", text: "6.5 – 7.8 (Tolerates slight alkalinity; avoid saline soils with EC > 2.0 dS/m)." },
      { label: "Drainage & Aeration", text: "Requires dedicated ridge drainage; saturation combined with warm soil triggers vascular wilt." },
      { label: "Nutrient Dynamics (NPK)", text: "Split potassium top-dressing is essential; acute K deficiency heightens leaf necrosis." },
      { label: "Organic Amendments", text: "0.4% – 0.6% organic carbon; apply neem cake @ 250 kg/ha to suppress soil pathogens." }
    ],
    precautions: [
      { label: "Acid Delinting Treatment", text: "Delint cotton seeds with concentrated sulfuric acid (100 ml/kg) followed by washing." },
      { label: "Antibacterial Seed Soak", text: "Treat acid-delinted seeds with Streptocycline (100 ppm) solution for 30 minutes before sowing." },
      { label: "Dew-Period Sanitation", text: "Restrict field workers and machinery while dew or raindrops remain on crop foliage." },
      { label: "Biocontrol Foliar Spray", text: "Apply foliar sprays of Pseudomonas fluorescens @ 10g/L during early vegetative stages." },
      { label: "Bactericide Intervention", text: "Spray Copper Oxychloride (0.3%) combined with Streptocycline (100 ppm) upon lesion spotting." }
    ]
  },
  "Blast Disease": {
    crop: "Paddy",
    soil: [
      { label: "Soil Texture & Depth", text: "Heavy clay or clay loam with high water-holding capacity and active silica reserves." },
      { label: "Optimal pH Range", text: "5.5 – 6.5 (Standard acidic to neutral lowland wetland soil profiles)." },
      { label: "Drainage & Aeration", text: "Controlled saturation; maintain continuous shallow standing water (3–5 cm) during tillering." },
      { label: "Nutrient Dynamics (NPK)", text: "Avoid single heavy urea doses; apply calcium silicate (1–2 t/ha) to build leaf silica barriers." },
      { label: "Organic Amendments", text: "0.6% – 1.0% organic carbon; incorporate green manure (Dhaincha) during puddling." }
    ],
    precautions: [
      { label: "Fungicidal Seed Dressing", text: "Treat paddy seeds with Carbendazim 50% WP (2g/kg) or Trichoderma viride (10g/kg)." },
      { label: "Split Nitrogen Strategy", text: "Adopt 3–4 split nitrogen applications calibrated to a Leaf Color Chart (LCC) index." },
      { label: "Water Level Stabilization", text: "Prevent mid-season moisture stress or field drying during tillering to flowering phases." },
      { label: "Bund Sanitation", text: "Eliminate collateral grass hosts (Echinochloa, Panicum) on field bunds and water channels." },
      { label: "Targeted Chemical Control", text: "Spray Tricyclazole 75% WP @ 0.6g/L at early tillering and late boot-leaf stages." }
    ]
  },
  "Brown Spot": {
    crop: "Paddy",
    soil: [
      { label: "Soil Texture & Depth", text: "Coarse sandy loam, unpuddled alluvial soil, or nutrient-leached degraded profiles." },
      { label: "Optimal pH Range", text: "5.0 – 6.2 (Highly vulnerable in acidic, mineral-depleted, or unbuffered zones)." },
      { label: "Drainage & Aeration", text: "Excessive percolation or drought-prone moisture fluctuations aggravate symptom severity." },
      { label: "Nutrient Dynamics (NPK)", text: "Ameliorate severe soil deficiencies: top-dress Potassium (MOP) and Zinc Sulphate @ 25 kg/ha." },
      { label: "Organic Amendments", text: "Enrich low organic carbon (<0.4%) with FYM @ 12.5 t/ha alongside Azospirillum culture." }
    ],
    precautions: [
      { label: "Hot Water Seed Treatment", text: "Dip seeds in hot water at 52–54°C for 10–12 minutes to eliminate seed-borne mycelium." },
      { label: "Seed Dressing Compound", text: "Dress dry seeds with Thiram or Captan @ 4g/kg seed prior to nursery preparation." },
      { label: "Micronutrient Balancing", text: "Apply basal zinc and manganese amendments to resolve physiological leaf spotting stress." },
      { label: "Green Manure Puddling", text: "Incorporate Sunn hemp or Sesbania green manure 15 days prior to seedling transplanting." },
      { label: "Foliar Fungicide Timing", text: "Spray Mancozeb (2g/L) or Propiconazole (1ml/L) at panicle emergence if spotting expands." }
    ]
  },
  "Common Rust": {
    crop: "Corn",
    soil: [
      { label: "Soil Texture & Depth", text: "Fertile, deep silt loam to well-structured sandy loam with high aeration and friable tilth." },
      { label: "Optimal pH Range", text: "6.0 – 7.2 (Near neutral; highly sensitive to waterlogging at seedling and tasseling)." },
      { label: "Drainage & Aeration", text: "Requires swift percolation; soil saturation exceeding 24 hours impairs root respiration." },
      { label: "Nutrient Dynamics (NPK)", text: "High nitrogen-phosphorus demand (150:75:40 kg/ha); correct zinc white-bud deficiency." },
      { label: "Organic Amendments", text: "0.5% – 0.8% organic carbon; apply decomposed compost @ 10–12 t/ha during tillage." }
    ],
    precautions: [
      { label: "Resistant Hybrid Sowing", text: "Select certified rust-resistant maize hybrids adapted to standard regional planting windows." },
      { label: "Row Spacing Aeration", text: "Maintain 60–75 cm row spacing to foster intra-canopy airflow and reduce leaf wetness." },
      { label: "Crop Rotation Cadence", text: "Rotate fields with non-graminaceous legumes (soybean, gram) to break urediniospore cycles." },
      { label: "Early Pustule Detection", text: "Scout lower leaves prior to tasseling; flag early rust pustules before upward canopy spread." },
      { label: "Foliar Fungicide Spray", text: "Apply Azoxystrobin (1ml/L) or Mancozeb (2.5g/L) upon early detection on lower leaves." }
    ]
  }
};

const initialScans = [
  {
    scan_id: "scan_101",
    timestamp: "2026-11-04T09:30:00Z",
    crop: "Tomato",
    predicted_disease: "Early Blight",
    confidence: 0.92,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 14.6195, lon: 74.8354 },
    farmer: {
      name: "Ramesh Hegde",
      phone: "+91 98451 23450",
      district: "Uttara Kannada",
      state: "Karnataka",
      country: "India"
    }
  },
  {
    scan_id: "scan_102",
    timestamp: "2026-11-04T10:15:00Z",
    crop: "Tomato",
    predicted_disease: "Late Blight",
    confidence: 0.54,
    farmer_feedback: "disputed",
    verification_status: "pending",
    location: { lat: 12.5218, lon: 76.8951 },
    farmer: {
      name: "Suresh Gowda",
      phone: "+91 94482 11982",
      district: "Mandya",
      state: "Karnataka",
      country: "India"
    }
  },
  {
    scan_id: "scan_103",
    timestamp: "2026-11-04T11:00:00Z",
    crop: "Potato",
    predicted_disease: "Early Blight",
    confidence: 0.88,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 15.8497, lon: 74.4977 },
    farmer: {
      name: "Anand Patil",
      phone: "+91 97412 88710",
      district: "Belagavi",
      state: "Karnataka",
      country: "India"
    }
  },
  {
    scan_id: "scan_104",
    timestamp: "2026-11-04T12:40:00Z",
    crop: "Cotton",
    predicted_disease: "Bacterial Blight",
    confidence: 0.49,
    farmer_feedback: "unreviewed",
    verification_status: "pending",
    location: { lat: 16.2076, lon: 77.3463 },
    farmer: {
      name: "Basavaraj Kuruba",
      phone: "+91 96110 54321",
      district: "Raichur",
      state: "Karnataka",
      country: "India"
    }
  },
  {
    scan_id: "scan_105",
    timestamp: "2026-11-04T13:10:00Z",
    crop: "Paddy",
    predicted_disease: "Blast Disease",
    confidence: 0.95,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 13.9299, lon: 75.5681 },
    farmer: {
      name: "Manjunath Bhat",
      phone: "+91 94801 32987",
      district: "Shimoga",
      state: "Karnataka",
      country: "India"
    }
  },
  {
    scan_id: "scan_106",
    timestamp: "2026-11-04T14:20:00Z",
    crop: "Paddy",
    predicted_disease: "Brown Spot",
    confidence: 0.78,
    farmer_feedback: "unreviewed",
    verification_status: "rejected",
    location: { lat: 13.3409, lon: 74.7421 },
    farmer: {
      name: "Prakash Nayak",
      phone: "+91 99002 44123",
      district: "Udupi",
      state: "Karnataka",
      country: "India"
    }
  },
  {
    scan_id: "scan_107",
    timestamp: "2026-11-04T15:00:00Z",
    crop: "Corn",
    predicted_disease: "Common Rust",
    confidence: 0.89,
    farmer_feedback: "confirmed",
    verification_status: "pending",
    location: { lat: 14.4644, lon: 75.9218 },
    farmer: {
      name: "Veeranna Shivaraj",
      phone: "+91 98860 12099",
      district: "Davanagere",
      state: "Karnataka",
      country: "India"
    }
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('telemetry'); // 'telemetry' | 'mandi' | 'weather' | 'news'

  const [scans, setScans] = useState(initialScans);
  const [selectedScan, setSelectedScan] = useState(null);

  // Scanner state
  const [previewUrl, setPreviewUrl] = useState(null);
  const [scanCrop, setScanCrop] = useState('Tomato');
  const [isScanning, setIsScanning] = useState(false);
  const fileInputRef = useRef(null);

  // Farmer Intake Form State
  const [farmerName, setFarmerName] = useState('');
  const [farmerPhone, setFarmerPhone] = useState('');
  const [farmerDistrict, setFarmerDistrict] = useState('');
  const [farmerState, setFarmerState] = useState('Karnataka');
  const [farmerCountry, setFarmerCountry] = useState('India');
  const [customLat, setCustomLat] = useState('14.6195');
  const [customLon, setCustomLon] = useState('74.8354');

  // Standalone Advisory Box State
  const [advisoryDisease, setAdvisoryDisease] = useState('Early Blight');

  // Dedicated Crop Charts State
  const [selectedChartCrop, setSelectedChartCrop] = useState('Tomato');

  // Mandi & Market Analytics State (Interactive Center Selection)
  const [selectedMandiCrop, setSelectedMandiCrop] = useState('Tomato');
  const [selectedMandiMarket, setSelectedMandiMarket] = useState(MANDI_MARKETS[0]);

  // Dynamic Mandi Pricing calculated when center or crop changes
  const currentMandiData = useMemo(() => {
    return getMarketPriceData(selectedMandiCrop, selectedMandiMarket);
  }, [selectedMandiCrop, selectedMandiMarket]);

  // Regional Weather State (Cascading State & District)
  const [selectedState, setSelectedState] = useState('Karnataka');
  const [selectedDistrict, setSelectedDistrict] = useState('Uttara Kannada');

  const handleStateChange = (stateName) => {
    setSelectedState(stateName);
    const districts = INDIA_ALL_STATES_DISTRICTS[stateName] || [];
    if (districts.length > 0) {
      setSelectedDistrict(districts[0]);
    }
  };

  const currentWeather = useMemo(() => {
    return getDistrictWeatherData(selectedDistrict, selectedState);
  }, [selectedDistrict, selectedState]);

  // Filter state
  const [filterCrop, setFilterCrop] = useState('');
  const [filterDisease, setFilterDisease] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [confidenceMin, setConfidenceMin] = useState(0);

  const handleImageUpload = (e) => {
    const file = e.target.files && e.target.files[0];
    if (file) {
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleFetchCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert("Geolocation is not supported by your browser.");
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCustomLat(pos.coords.latitude.toFixed(4));
        setCustomLon(pos.coords.longitude.toFixed(4));
      },
      (err) => {
        alert("Unable to fetch location: " + err.message);
      }
    );
  };

  const handleStartScan = () => {
    if (!previewUrl) {
      alert("Please choose or capture a leaf photo first.");
      return;
    }

    setIsScanning(true);

    setTimeout(() => {
      const latVal = parseFloat(customLat);
      const lonVal = parseFloat(customLon);

      const newRecord = {
        scan_id: `scan_${Date.now().toString().slice(-4)}`,
        timestamp: new Date().toISOString(),
        crop: scanCrop,
        predicted_disease: "Analysis Pending",
        confidence: 0.75,
        farmer_feedback: "unreviewed",
        verification_status: "pending",
        location: (!isNaN(latVal) && !isNaN(lonVal)) ? { lat: latVal, lon: lonVal } : null,
        farmer: {
          name: farmerName.trim() || "Anonymous Farmer",
          phone: farmerPhone.trim() || "Not provided",
          district: farmerDistrict.trim() || "Unspecified",
          state: farmerState.trim() || "Karnataka",
          country: farmerCountry.trim() || "India"
        }
      };

      setScans(prev => [newRecord, ...prev]);
      setIsScanning(false);
      setPreviewUrl(null);
      setFarmerName('');
      setFarmerPhone('');
      setFarmerDistrict('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      alert(`Scan ${newRecord.scan_id} recorded for ${newRecord.farmer.name}!`);
    }, 1200);
  };

  const filteredScans = useMemo(() => {
    return scans.filter(scan => {
      const matchCrop = !filterCrop || scan.crop === filterCrop;
      const matchDisease = !filterDisease || scan.predicted_disease === filterDisease;
      const matchStatus = !filterStatus || scan.verification_status === filterStatus;
      const matchConf = scan.confidence >= confidenceMin;
      return matchCrop && matchDisease && matchStatus && matchConf;
    });
  }, [scans, filterCrop, filterDisease, filterStatus, confidenceMin]);

  const metrics = useMemo(() => {
    const crops = new Set(scans.map(s => s.crop));
    const diseases = new Set(scans.map(s => s.predicted_disease));
    const lowConf = scans.filter(s => s.confidence < 0.6).length;
    const farmerConfirmed = scans.filter(s => s.farmer_feedback === 'confirmed').length;
    const expertVerified = scans.filter(s => s.verification_status === 'expert_verified').length;

    return {
      total: scans.length,
      uniqueCrops: crops.size,
      uniqueDiseases: diseases.size,
      lowConf,
      farmerConfirmed,
      expertVerified
    };
  }, [scans]);

  const diseaseChartData = useMemo(() => {
    const counts = {};
    filteredScans.forEach(s => {
      counts[s.predicted_disease] = (counts[s.predicted_disease] || 0) + 1;
    });
    return Object.entries(counts).map(([name, count]) => ({ name, count }));
  }, [filteredScans]);

  const cropChartData = useMemo(() => {
    const counts = {};
    filteredScans.forEach(s => {
      counts[s.crop] = (counts[s.crop] || 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [filteredScans]);

  return (
    <div className="app-container">
      {/* Prototype Disclaimer Banner */}
      <div className="banner">
        <div>
          <strong>AgroLens Prototype:</strong> Research analytics dashboard. Synthesized comparison models for educational evaluation.
        </div>
        <span className="banner-badge">DEMONSTRATION MOCK DATA ACTIVE</span>
      </div>

      {/* HEADER WITH ICAR-IIHR LOGO & INSTITUTIONAL BADGE */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          {/* ICAR-IIHR Compact Emblem Badge */}
          <div style={{
            background: '#ffffff',
            padding: 3,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.35)',
            border: '2px solid #38bdf8',
            flexShrink: 0
          }}>
            <img
              src="https://upload.wikimedia.org/wikipedia/en/thumb/d/d6/Logo_of_Indian_Institute_of_Horticultural_Research.jpg/250px-Logo_of_Indian_Institute_of_Horticultural_Research.jpg"
              alt="ICAR-IIHR Logo"
              style={{
                width: 44,
                height: 44,
                objectFit: 'contain',
                borderRadius: '50%'
              }}
              onError={(e) => {
                // Fallback to ICAR Council Wheat Sheaf Emblem
                e.target.src = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/Logo_of_the_Indian_Council_of_Agricultural_Research.svg/250px-Logo_of_the_Indian_Council_of_Agricultural_Research.svg.png";
              }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <h1 style={{ fontSize: 28, margin: 0 }}>AgroLens Research Dashboard</h1>
              <span style={{
                background: '#1e3a5f',
                color: '#38bdf8',
                fontSize: 11,
                fontWeight: 600,
                padding: '2px 8px',
                borderRadius: 4,
                border: '1px solid #38bdf8'
              }}>
                ICAR-IIHR Aligned
              </span>
            </div>
            <p style={{ color: '#94a3b8', fontSize: 14, margin: '4px 0 0 0' }}>
              Field Scan Telemetry & Institutional Baseline Analytics
            </p>
          </div>
        </div>

        <div style={{ display: 'flex', gap: 10 }}>
          <button className="export-btn" onClick={() => alert("Backend CSV export will connect to /api/export/scans?format=csv")}>Export CSV</button>
          <button className="export-btn" onClick={() => alert("Backend JSON export will connect to /api/export/scans?format=json")}>Export JSON</button>
        </div>
      </header>

      {/* PRIMARY INTELLIGENCE NAVIGATION TABS */}
      <div style={{
        display: 'flex',
        gap: 8,
        borderBottom: '1px solid #334155',
        marginBottom: 24,
        paddingBottom: 2,
        overflowX: 'auto'
      }}>
        <button
          onClick={() => setActiveTab('telemetry')}
          style={{
            padding: '10px 18px',
            background: activeTab === 'telemetry' ? '#1e293b' : 'transparent',
            color: activeTab === 'telemetry' ? '#38bdf8' : '#94a3b8',
            border: 'none',
            borderBottom: activeTab === 'telemetry' ? '2px solid #38bdf8' : '2px solid transparent',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: 14,
            borderRadius: '6px 6px 0 0'
          }}
        >
          🔍 Disease & Scan Telemetry
        </button>

        <button
          onClick={() => setActiveTab('mandi')}
          style={{
            padding: '10px 18px',
            background: activeTab === 'mandi' ? '#1e293b' : 'transparent',
            color: activeTab === 'mandi' ? '#38bdf8' : '#94a3b8',
            border: 'none',
            borderBottom: activeTab === 'mandi' ? '2px solid #38bdf8' : '2px solid transparent',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: 14,
            borderRadius: '6px 6px 0 0'
          }}
        >
          📈 Mandi Price Analytics
        </button>

        <button
          onClick={() => setActiveTab('weather')}
          style={{
            padding: '10px 18px',
            background: activeTab === 'weather' ? '#1e293b' : 'transparent',
            color: activeTab === 'weather' ? '#38bdf8' : '#94a3b8',
            border: 'none',
            borderBottom: activeTab === 'weather' ? '2px solid #38bdf8' : '2px solid transparent',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: 14,
            borderRadius: '6px 6px 0 0'
          }}
        >
          🌦️ Agrometeorology & Weather
        </button>

        <button
          onClick={() => setActiveTab('news')}
          style={{
            padding: '10px 18px',
            background: activeTab === 'news' ? '#1e293b' : 'transparent',
            color: activeTab === 'news' ? '#38bdf8' : '#94a3b8',
            border: 'none',
            borderBottom: activeTab === 'news' ? '2px solid #38bdf8' : '2px solid transparent',
            fontWeight: 600,
            cursor: 'pointer',
            fontSize: 14,
            borderRadius: '6px 6px 0 0'
          }}
        >
          📰 News & Schemes
        </button>
      </div>

      {/* TAB 1: DISEASE & SCAN TELEMETRY */}
      {activeTab === 'telemetry' && (
        <>
          {/* Leaf Scan & Farmer Intake */}
          <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 20, marginBottom: 24 }}>
            <h3 style={{ marginBottom: 14, fontSize: 18, color: '#f8fafc' }}>Leaf Scan & Field Intake</h3>
            
            {/* Farmer & Location Details Form */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: 12,
              marginBottom: 16,
              background: '#0f172a',
              padding: 14,
              borderRadius: 6,
              border: '1px solid #334155'
            }}>
              <div>
                <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Farmer Name:</label>
                <input
                  type="text"
                  placeholder="e.g. Ramesh Hegde"
                  value={farmerName}
                  onChange={(e) => setFarmerName(e.target.value)}
                  className="filter-input"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Phone Number:</label>
                <input
                  type="tel"
                  placeholder="+91 98450 12345"
                  value={farmerPhone}
                  onChange={(e) => setFarmerPhone(e.target.value)}
                  className="filter-input"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>District:</label>
                <input
                  type="text"
                  placeholder="e.g. Uttara Kannada"
                  value={farmerDistrict}
                  onChange={(e) => setFarmerDistrict(e.target.value)}
                  className="filter-input"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>State:</label>
                <input
                  type="text"
                  value={farmerState}
                  onChange={(e) => setFarmerState(e.target.value)}
                  className="filter-input"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Country:</label>
                <input
                  type="text"
                  value={farmerCountry}
                  onChange={(e) => setFarmerCountry(e.target.value)}
                  className="filter-input"
                  style={{ width: '100%' }}
                />
              </div>

              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <label style={{ fontSize: 12, color: '#94a3b8' }}>Lat / Lon:</label>
                  <button
                    type="button"
                    onClick={handleFetchCurrentLocation}
                    style={{ background: 'transparent', border: 'none', color: '#38bdf8', fontSize: 11, cursor: 'pointer', padding: 0 }}
                  >
                    📍 GPS Detect
                  </button>
                </div>
                <div style={{ display: 'flex', gap: 6 }}>
                  <input
                    type="text"
                    placeholder="Lat"
                    value={customLat}
                    onChange={(e) => setCustomLat(e.target.value)}
                    className="filter-input"
                    style={{ width: '50%' }}
                  />
                  <input
                    type="text"
                    placeholder="Lon"
                    value={customLon}
                    onChange={(e) => setCustomLon(e.target.value)}
                    className="filter-input"
                    style={{ width: '50%' }}
                  />
                </div>
              </div>
            </div>

            {/* Scan Intake Controls */}
            <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'center' }}>
              <div>
                <label style={{ fontSize: 13, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Target Crop:</label>
                <select className="filter-input" value={scanCrop} onChange={(e) => setScanCrop(e.target.value)}>
                  <option value="Tomato">Tomato</option>
                  <option value="Potato">Potato</option>
                  <option value="Paddy">Paddy</option>
                  <option value="Cotton">Cotton</option>
                  <option value="Corn">Corn</option>
                </select>
              </div>

              <div>
                <label style={{ fontSize: 13, color: '#94a3b8', display: 'block', marginBottom: 4 }}>Leaf Photo / Camera:</label>
                <input
                  type="file"
                  accept="image/*"
                  capture="environment"
                  ref={fileInputRef}
                  onChange={handleImageUpload}
                  className="filter-input"
                />
              </div>

              <div style={{ marginTop: 20, display: 'flex', gap: 8 }}>
                <button
                  className="export-btn"
                  onClick={handleStartScan}
                  disabled={!previewUrl || isScanning}
                  style={{ opacity: (!previewUrl || isScanning) ? 0.6 : 1, cursor: previewUrl ? 'pointer' : 'not-allowed' }}
                >
                  {isScanning ? 'Processing Scan...' : 'Record Scan'}
                </button>
                {previewUrl && (
                  <button
                    className="filter-input"
                    style={{ cursor: 'pointer', background: '#334155' }}
                    onClick={() => { setPreviewUrl(null); if (fileInputRef.current) fileInputRef.current.value = ''; }}
                  >
                    Clear
                  </button>
                )}
              </div>
            </div>

            {previewUrl && (
              <div style={{ marginTop: 14 }}>
                <span style={{ fontSize: 12, color: '#94a3b8' }}>Leaf Sample Preview:</span>
                <div style={{ marginTop: 6 }}>
                  <img src={previewUrl} alt="Scan preview" style={{ height: 110, borderRadius: 6, border: '1px solid #475569' }} />
                </div>
              </div>
            )}
          </div>

          {/* DEDICATED SEPARATE BOX: SOIL & PRECAUTIONS ADVISORY */}
          <div style={{
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 8,
            padding: 20,
            marginBottom: 24,
            textAlign: 'left'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
              <div>
                <h3 style={{ margin: 0, fontSize: 18, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 8 }}>
                  🌾 Agronomic Advisory: Soil & Precautions Guide
                </h3>
                <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#94a3b8' }}>
                  Standard crop protection practices and soil condition recommendations.
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <label style={{ fontSize: 13, color: '#94a3b8' }}>Select Disease / Target:</label>
                <select
                  className="filter-input"
                  value={advisoryDisease}
                  onChange={(e) => setAdvisoryDisease(e.target.value)}
                  style={{ minWidth: 200 }}
                >
                  {Object.keys(AGRONOMIC_GUIDE).map((disease) => (
                    <option key={disease} value={disease}>{disease} ({AGRONOMIC_GUIDE[disease].crop})</option>
                  ))}
                </select>
              </div>
            </div>

            {/* 2-Column Equal Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 16, alignItems: 'stretch' }}>
              {/* Soil Information Box */}
              <div style={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 6,
                padding: 18,
                display: 'flex',
                flexDirection: 'column',
                textAlign: 'left'
              }}>
                <h4 style={{ margin: '0 0 14px 0', fontSize: 15, color: '#38bdf8', display: 'flex', alignItems: 'center', gap: 6 }}>
                  🌱 Soil Profile & Health Requirements
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13, color: '#cbd5e1' }}>
                  {AGRONOMIC_GUIDE[advisoryDisease]?.soil.map((item, idx) => (
                    <div key={idx} style={{ lineHeight: 1.5, textAlign: 'left' }}>
                      <strong style={{ color: '#93c5fd' }}>• {item.label}: </strong>
                      <span>{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Precautions Box */}
              <div style={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 6,
                padding: 18,
                display: 'flex',
                flexDirection: 'column',
                textAlign: 'left'
              }}>
                <h4 style={{ margin: '0 0 14px 0', fontSize: 15, color: '#f59e0b', display: 'flex', alignItems: 'center', gap: 6 }}>
                  ⚠️ Standard Precautionary & Management Protocols
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10, fontSize: 13, color: '#cbd5e1' }}>
                  {AGRONOMIC_GUIDE[advisoryDisease]?.precautions.map((item, idx) => (
                    <div key={idx} style={{ lineHeight: 1.5, textAlign: 'left' }}>
                      <strong style={{ color: '#fde68a' }}>• {item.label}: </strong>
                      <span>{item.text}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div style={{ marginTop: 14, fontSize: 11, color: '#64748b', fontStyle: 'italic', textAlign: 'left' }}>
              *Synthesized from standard agricultural research management practices for prototype demonstration.
            </div>
          </div>

          {/* DEDICATED CROP-SPECIFIC HISTORICAL CHARTS WITH DROPDOWN SELECTOR */}
          <div style={{
            background: '#1e293b',
            border: '1px solid #334155',
            borderRadius: 8,
            padding: 20,
            marginBottom: 24
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
              <div>
                <h3 style={{ margin: 0, fontSize: 18, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: 8 }}>
                  📊 Institutional Baseline Comparison & Historical Incidence Trends
                </h3>
                <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#94a3b8' }}>
                  Crop-specific seasonal telemetry benchmarked against ICAR-IIHR/IISR standard surveillance profiles.
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <label style={{ fontSize: 13, color: '#94a3b8', fontWeight: 500 }}>Select Crop Analytics:</label>
                <select
                  className="filter-input"
                  value={selectedChartCrop}
                  onChange={(e) => setSelectedChartCrop(e.target.value)}
                  style={{ minWidth: 140, cursor: 'pointer', borderColor: '#38bdf8' }}
                >
                  <option value="Tomato">Tomato</option>
                  <option value="Potato">Potato</option>
                  <option value="Paddy">Paddy</option>
                  <option value="Cotton">Cotton</option>
                  <option value="Corn">Corn</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 20 }}>
              {/* Crop-Specific Longitudinal Trend Line Chart */}
              <div style={{ background: '#0f172a', padding: 16, borderRadius: 6, border: '1px solid #334155' }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#cbd5e1', marginBottom: 12 }}>
                  {selectedChartCrop} Disease Incidence % (Field vs. Institutional Baseline)
                </div>
                <div style={{ width: '100%', height: 260 }}>
                  <ResponsiveContainer>
                    <LineChart data={CROP_HISTORICAL_TRENDS[selectedChartCrop] || []}>
                      <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                      <XAxis dataKey="season" stroke="#94a3b8" fontSize={11} />
                      <YAxis stroke="#94a3b8" fontSize={11} unit="%" domain={[0, 60]} />
                      <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#475569' }} />
                      <Legend verticalAlign="top" height={36} />
                      <Line type="monotone" dataKey="AgroLensObserved" name={`${selectedChartCrop} Field Scans`} stroke="#38bdf8" strokeWidth={2} dot={{ r: 4 }} />
                      <Line type="monotone" dataKey="Baseline" name="ICAR Institutional Baseline" stroke="#10b981" strokeWidth={2} strokeDasharray="5 5" dot={{ r: 4 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Crop-Specific Diagnostic Standard Metric Comparison */}
              <div style={{ background: '#0f172a', padding: 16, borderRadius: 6, border: '1px solid #334155' }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#cbd5e1', marginBottom: 12 }}>
                  {selectedChartCrop} Model Evaluation vs. Institutional Standard (%)
                </div>
                <div style={{ width: '100%', height: 260 }}>
                  <ResponsiveContainer>
                    <BarChart data={CROP_BENCHMARK_METRICS[selectedChartCrop] || []}>
                      <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                      <XAxis dataKey="metric" stroke="#94a3b8" fontSize={12} />
                      <YAxis stroke="#94a3b8" fontSize={12} domain={[60, 100]} unit="%" />
                      <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#475569' }} />
                      <Legend verticalAlign="top" height={36} />
                      <Bar dataKey="AgroLens" name={`AgroLens ${selectedChartCrop}`} fill="#3b82f6" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="Benchmark" name="ICAR Target Standard" fill="#f59e0b" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>

            <div style={{ marginTop: 12, fontSize: 11, color: '#64748b', fontStyle: 'italic' }}>
              *Synthesized research metrics aligned with published seasonal advisory bulletins. Educational prototype visualization.
            </div>
          </div>

          {/* Metrics Row */}
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-title">Total Scans</div>
              <div className="metric-value">{metrics.total}</div>
            </div>
            <div className="metric-card">
              <div className="metric-title">Unique Crops</div>
              <div className="metric-value">{metrics.uniqueCrops}</div>
            </div>
            <div className="metric-card">
              <div className="metric-title">Diseases / Pests</div>
              <div className="metric-value">{metrics.uniqueDiseases}</div>
            </div>
            <div className="metric-card">
              <div className="metric-title">Low Confidence (&lt;60%)</div>
              <div className="metric-value" style={{ color: '#f59e0b' }}>{metrics.lowConf}</div>
            </div>
            <div className="metric-card">
              <div className="metric-title">Farmer Confirmed</div>
              <div className="metric-value" style={{ color: '#38bdf8' }}>{metrics.farmerConfirmed}</div>
            </div>
            <div className="metric-card">
              <div className="metric-title">Expert Verified</div>
              <div className="metric-value" style={{ color: '#10b981' }}>{metrics.expertVerified}</div>
            </div>
          </div>

          {/* Analytics Charts */}
          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-title">Most Frequent Diseases</div>
              <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer>
                  <BarChart data={diseaseChartData}>
                    <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                    <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                    <YAxis stroke="#94a3b8" fontSize={12} allowDecimals={false} />
                    <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#475569' }} />
                    <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="chart-card">
              <div className="chart-title">Disease Distribution by Crop</div>
              <div style={{ width: '100%', height: 260 }}>
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={cropChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                      {cropChartData.map((_, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#475569' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Filter Bar */}
          <div className="filter-bar">
            <select className="filter-input" value={filterCrop} onChange={e => setFilterCrop(e.target.value)}>
              <option value="">All Crops</option>
              {[...new Set(scans.map(s => s.crop))].map(c => <option key={c} value={c}>{c}</option>)}
            </select>

            <select className="filter-input" value={filterDisease} onChange={e => setFilterDisease(e.target.value)}>
              <option value="">All Diseases</option>
              {[...new Set(scans.map(s => s.predicted_disease))].map(d => <option key={d} value={d}>{d}</option>)}
            </select>

            <select className="filter-input" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
              <option value="">All Verification States</option>
              <option value="pending">Pending</option>
              <option value="expert_verified">Expert Verified</option>
              <option value="rejected">Rejected</option>
            </select>

            <label style={{ fontSize: 13, color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 6 }}>
              Min Conf:
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={confidenceMin}
                onChange={e => setConfidenceMin(parseFloat(e.target.value))}
              />
              {(confidenceMin * 100).toFixed(0)}%
            </label>

            {(filterCrop || filterDisease || filterStatus || confidenceMin > 0) && (
              <button
                className="filter-input"
                style={{ cursor: 'pointer', background: '#334155' }}
                onClick={() => { setFilterCrop(''); setFilterDisease(''); setFilterStatus(''); setConfidenceMin(0); }}
              >
                Clear Filters
              </button>
            )}
          </div>

          {/* Scans Table */}
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Scan ID</th>
                  <th>Farmer Details</th>
                  <th>Region</th>
                  <th>GPS Coordinates</th>
                  <th>Crop</th>
                  <th>Predicted Disease</th>
                  <th>Confidence</th>
                  <th>Feedback</th>
                  <th>Verification</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredScans.length === 0 ? (
                  <tr><td colSpan="10" style={{ textAlign: 'center', padding: 24, color: '#94a3b8' }}>No scans match current filters.</td></tr>
                ) : (
                  filteredScans.map(scan => (
                    <tr key={scan.scan_id}>
                      <td><code>{scan.scan_id}</code></td>
                      <td>
                        <div style={{ fontWeight: 600, color: '#f8fafc' }}>{scan.farmer?.name || "Anonymous"}</div>
                        <div style={{ fontSize: 11, color: '#94a3b8' }}>{scan.farmer?.phone || "No phone"}</div>
                      </td>
                      <td>
                        <div style={{ fontSize: 12 }}>{scan.farmer ? `${scan.farmer.district}, ${scan.farmer.state}` : 'Unspecified'}</div>
                        <div style={{ fontSize: 11, color: '#64748b' }}>{scan.farmer?.country || 'India'}</div>
                      </td>
                      <td>
                        {scan.location ? (
                          <a
                            href={`https://www.google.com/maps?q=${scan.location.lat},${scan.location.lon}`}
                            target="_blank"
                            rel="noreferrer noopener"
                            style={{
                              color: '#38bdf8',
                              textDecoration: 'none',
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: 4,
                              fontSize: 12,
                              background: '#0f172a',
                              padding: '3px 8px',
                              borderRadius: 4,
                              border: '1px solid #334155'
                            }}
                            title="Click to view field location on Google Maps"
                          >
                            📍 {scan.location.lat}, {scan.location.lon}
                          </a>
                        ) : (
                          <span style={{ fontSize: 12, color: '#64748b' }}>Not provided</span>
                        )}
                      </td>
                      <td>{scan.crop}</td>
                      <td>{scan.predicted_disease}</td>
                      <td>
                        <span className={`badge ${scan.confidence < 0.6 ? 'badge-warning' : 'badge-success'}`}>
                          {(scan.confidence * 100).toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        <span className="badge badge-gray">{scan.farmer_feedback}</span>
                      </td>
                      <td>
                        <span className={`badge ${
                          scan.verification_status === 'expert_verified' ? 'badge-success' :
                          scan.verification_status === 'rejected' ? 'badge-warning' : 'badge-info'
                        }`}>
                          {scan.verification_status}
                        </span>
                      </td>
                      <td>
                        <button
                          className="filter-input"
                          style={{ cursor: 'pointer', padding: '4px 8px' }}
                          onClick={() => setSelectedScan(scan)}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* TAB 2: MANDI MARKET & PRICE ANALYTICS */}
      {activeTab === 'mandi' && (
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
            <div>
              <h3 style={{ margin: 0, fontSize: 18, color: '#f8fafc' }}>📈 Commodity & Mandi Price Analytics</h3>
              <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#94a3b8' }}>
                Latest APMC arrivals, modal price benchmarks, and 5-day ML trend projections.
              </p>
            </div>

            <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
              <label style={{ fontSize: 13, color: '#94a3b8' }}>Commodity:</label>
              <select
                className="filter-input"
                value={selectedMandiCrop}
                onChange={(e) => setSelectedMandiCrop(e.target.value)}
                style={{ minWidth: 140, cursor: 'pointer', borderColor: '#38bdf8' }}
              >
                <option value="Tomato">Tomato</option>
                <option value="Potato">Potato</option>
                <option value="Paddy">Paddy</option>
                <option value="Cotton">Cotton</option>
                <option value="Corn">Corn</option>
              </select>
            </div>
          </div>

          {currentMandiData && (
            <>
              {/* Price Metric Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 14, marginBottom: 20 }}>
                <div style={{ background: '#0f172a', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Selected Center & Location</div>
                  <div style={{ fontSize: 16, fontWeight: 600, color: '#f8fafc', marginTop: 4 }}>
                    {currentMandiData.market}
                  </div>
                  <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>
                    Source: {currentMandiData.source}
                  </div>
                </div>

                <div style={{ background: '#0f172a', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Today's Modal Price</div>
                  <div style={{ fontSize: 22, fontWeight: 700, color: '#38bdf8', marginTop: 4 }}>
                    ₹{currentMandiData.modalPrice}
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
                    Unit: {currentMandiData.unit}
                  </div>
                </div>

                <div style={{ background: '#0f172a', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Price Range (Min - Max)</div>
                  <div style={{ fontSize: 20, fontWeight: 600, color: '#10b981', marginTop: 4 }}>
                    ₹{currentMandiData.minPrice} – ₹{currentMandiData.maxPrice}
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
                    Updated: {new Date(currentMandiData.lastUpdated).toLocaleDateString()}
                  </div>
                </div>
              </div>

              {/* Price Trend Chart (Actual vs ML Forecast) */}
              <div style={{ background: '#0f172a', padding: 16, borderRadius: 6, border: '1px solid #334155', marginBottom: 20 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12, flexWrap: 'wrap', gap: 6 }}>
                  <span style={{ fontSize: 14, fontWeight: 600, color: '#f8fafc' }}>
                    {selectedMandiMarket.name} — Price Trajectory & 5-Day ML Projection ({currentMandiData.unit})
                  </span>
                  <div style={{ display: 'flex', gap: 14, fontSize: 12 }}>
                    <span style={{ color: '#38bdf8' }}>● Solid: Recorded APMC Prices</span>
                    <span style={{ color: '#f59e0b' }}>--- Dashed: ML Predictive Forecast</span>
                  </div>
                </div>

                <div style={{ width: '100%', height: 280 }}>
                  <ResponsiveContainer>
                    <LineChart data={currentMandiData.historical}>
                      <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
                      <XAxis dataKey="date" stroke="#94a3b8" fontSize={11} />
                      <YAxis stroke="#94a3b8" fontSize={11} domain={['dataMin - 150', 'dataMax + 150']} />
                      <Tooltip contentStyle={{ background: '#0f172a', borderColor: '#475569' }} />
                      <Legend verticalAlign="top" height={36} />
                      <Line type="monotone" dataKey="modal" name="Modal Price (₹)" stroke="#38bdf8" strokeWidth={2} dot={{ r: 4 }} />
                      <Line type="monotone" dataKey="max" name="Max Price (₹)" stroke="#10b981" strokeWidth={1.5} strokeDasharray="3 3" />
                      <Line type="monotone" dataKey="min" name="Min Price (₹)" stroke="#94a3b8" strokeWidth={1.5} strokeDasharray="3 3" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Active India APMC Monitoring Centers */}
              <div style={{ marginTop: 24 }}>
                <h3 style={{
                  textAlign: 'center',
                  fontSize: 18,
                  fontWeight: 700,
                  color: '#ffffff',
                  marginBottom: 6
                }}>
                  Active India APMC Monitoring Centers
                </h3>
                <p style={{ textAlign: 'center', fontSize: 12, color: '#94a3b8', margin: '0 0 16px 0' }}>
                  (Click any center to view its specific price trajectory and 5-day ML forecast above)
                </p>

                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                  gap: 14
                }}>
                  {MANDI_MARKETS.map(market => {
                    const isSelected = selectedMandiMarket.id === market.id;
                    return (
                      <div
                        key={market.id}
                        onClick={() => setSelectedMandiMarket(market)}
                        style={{
                          background: isSelected ? '#1e3a5f' : '#152238',
                          padding: '18px 16px',
                          borderRadius: 8,
                          border: isSelected ? '2px solid #38bdf8' : '1px solid #1e3a5f',
                          textAlign: 'center',
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center',
                          alignItems: 'center',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                          transform: isSelected ? 'translateY(-2px)' : 'none',
                          boxShadow: isSelected ? '0 4px 12px rgba(56, 189, 248, 0.2)' : 'none'
                        }}
                      >
                        <div style={{
                          fontWeight: 700,
                          color: isSelected ? '#ffffff' : '#38bdf8',
                          fontSize: 16,
                          marginBottom: 6
                        }}>
                          {market.name} {isSelected && '✓'}
                        </div>
                        <div style={{
                          color: isSelected ? '#93c5fd' : '#94a3b8',
                          fontSize: 13
                        }}>
                          {market.district}, {market.state}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* TAB 3: AGROMETEOROLOGY & REGIONAL WEATHER (ALL STATES & ALL DISTRICTS) */}
      {activeTab === 'weather' && (
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 10 }}>
            <div>
              <h3 style={{ margin: 0, fontSize: 18, color: '#f8fafc' }}>🌦️ Agrometeorological & Micro-Climate Intelligence</h3>
              <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#94a3b8' }}>
                District-level climate surveillance linked directly to fungal and bacterial pathogen risk indices across India.
              </p>
            </div>

            {/* Cascading State & District Selectors */}
            <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <label style={{ fontSize: 13, color: '#94a3b8' }}>Select State:</label>
                <select
                  className="filter-input"
                  value={selectedState}
                  onChange={(e) => handleStateChange(e.target.value)}
                  style={{ minWidth: 160, cursor: 'pointer', borderColor: '#38bdf8' }}
                >
                  {Object.keys(INDIA_ALL_STATES_DISTRICTS).map(st => (
                    <option key={st} value={st}>{st}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <label style={{ fontSize: 13, color: '#94a3b8' }}>Select District:</label>
                <select
                  className="filter-input"
                  value={selectedDistrict}
                  onChange={(e) => setSelectedDistrict(e.target.value)}
                  style={{ minWidth: 170, cursor: 'pointer', borderColor: '#38bdf8' }}
                >
                  {(INDIA_ALL_STATES_DISTRICTS[selectedState] || []).map(dist => (
                    <option key={dist} value={dist}>{dist}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {currentWeather && (
            <>
              {/* Weather Telemetry Cards */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 14, marginBottom: 20 }}>
                <div style={{ background: '#0f172a', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Temperature</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#f8fafc', marginTop: 4 }}>
                    {currentWeather.temp}°C
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>Wind: {currentWeather.windSpeed}</div>
                </div>

                <div style={{ background: '#0f172a', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Relative Humidity</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#38bdf8', marginTop: 4 }}>
                    {currentWeather.humidity}%
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>
                    Canopy wetness index: {currentWeather.humidity > 70 ? 'Elevated' : 'Normal'}
                  </div>
                </div>

                <div style={{ background: '#0f172a', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Precipitation Outlook</div>
                  <div style={{ fontSize: 14, fontWeight: 600, color: '#cbd5e1', marginTop: 6, lineHeight: 1.4 }}>
                    {currentWeather.rainfallForecast}
                  </div>
                </div>

                <div style={{ background: '#0f172a', padding: 14, borderRadius: 6, border: '1px solid #334155' }}>
                  <div style={{ fontSize: 12, color: '#94a3b8' }}>Active Micro-Advisories</div>
                  <div style={{ fontSize: 24, fontWeight: 700, color: '#f59e0b', marginTop: 4 }}>
                    {currentWeather.advisoriesCount}
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 4 }}>Current week bulletins</div>
                </div>
              </div>

              {/* Crop Weather Risk Assessment Card */}
              <div style={{
                background: '#0f172a',
                border: '1px solid #334155',
                borderRadius: 6,
                padding: 16
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8, flexWrap: 'wrap' }}>
                  <span style={{ fontSize: 15, fontWeight: 600, color: '#f8fafc' }}>
                    Agrometeorological Risk Summary for {selectedDistrict}, {selectedState}
                  </span>
                  <span className={`badge ${
                    currentWeather.riskSummary.level === 'High' ? 'badge-warning' :
                    currentWeather.riskSummary.level === 'Medium' ? 'badge-info' : 'badge-success'
                  }`}>
                    {currentWeather.riskSummary.level} Risk
                  </span>
                </div>

                <p style={{ margin: '0 0 10px 0', fontSize: 13, color: '#cbd5e1', lineHeight: 1.6 }}>
                  {currentWeather.riskSummary.reason}
                </p>

                <div style={{ fontSize: 12, color: '#94a3b8' }}>
                  <strong>Soil Moisture Status: </strong>
                  <span>{currentWeather.soilMoistureStatus}</span>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* TAB 4: AGRI NEWS & GOVERNMENT SCHEMES */}
      {activeTab === 'news' && (
        <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 20 }}>
          <div style={{ marginBottom: 16 }}>
            <h3 style={{ margin: 0, fontSize: 18, color: '#f8fafc' }}>📰 Agricultural News & Verified Government Schemes</h3>
            <p style={{ margin: '4px 0 0 0', fontSize: 13, color: '#94a3b8' }}>
              Direct government scheme announcements, credit updates, and official institutional portals.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            {AGRI_NEWS_SCHEMES.map(item => (
              <div
                key={item.id}
                style={{
                  background: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: 6,
                  padding: 16,
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  flexWrap: 'wrap',
                  gap: 12
                }}
              >
                <div style={{ flex: '1 1 500px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <span className={`badge ${item.type === 'Scheme' ? 'badge-success' : item.type === 'Advisory' ? 'badge-warning' : 'badge-info'}`}>
                      {item.type}
                    </span>
                    <span style={{ fontSize: 12, color: '#94a3b8' }}>{item.date}</span>
                    <span style={{ fontSize: 12, color: '#64748b' }}>• {item.source}</span>
                  </div>

                  <h4 style={{ margin: '0 0 6px 0', fontSize: 15, color: '#f8fafc' }}>{item.title}</h4>
                  <p style={{ margin: 0, fontSize: 13, color: '#cbd5e1', lineHeight: 1.5 }}>{item.summary}</p>
                </div>

                <div>
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noreferrer noopener"
                    className="export-btn"
                    style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 6 }}
                  >
                    Official Portal ↗
                  </a>
                </div>
              </div>
            ))}
          </div>

          <div style={{ marginTop: 16, fontSize: 11, color: '#64748b', fontStyle: 'italic' }}>
            *Links redirect to external official portals. Data ingested via institutional feeds.
          </div>
        </div>
      )}

      {/* Record Detail Modal */}
      {selectedScan && (
        <div className="modal-backdrop" onClick={() => setSelectedScan(null)}>
          <div className="modal-box" style={{ maxWidth: 620 }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ margin: 0, fontSize: 18 }}>Scan & Farmer Telemetry Details</h3>
              <span className="badge badge-gray">{selectedScan.scan_id}</span>
            </div>

            {/* Farmer Identification Block */}
            <div style={{
              background: '#0f172a',
              padding: '12px 14px',
              borderRadius: 6,
              border: '1px solid #334155',
              marginBottom: 14
            }}>
              <h4 style={{ margin: '0 0 8px 0', fontSize: 14, color: '#38bdf8' }}>👨‍🌾 Farmer & Field Location</h4>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px 12px', fontSize: 13 }}>
                <p style={{ margin: 0 }}><strong>Name:</strong> {selectedScan.farmer?.name || 'Anonymous'}</p>
                <p style={{ margin: 0 }}><strong>Phone:</strong> {selectedScan.farmer?.phone || 'Not provided'}</p>
                <p style={{ margin: 0 }}><strong>District:</strong> {selectedScan.farmer?.district || 'Not specified'}</p>
                <p style={{ margin: 0 }}><strong>State:</strong> {selectedScan.farmer?.state || 'Karnataka'}, {selectedScan.farmer?.country || 'India'}</p>
                <div style={{ margin: 0, gridColumn: 'span 2', marginTop: 4 }}>
                  <strong>Google Maps Location: </strong>
                  {selectedScan.location ? (
                    <a
                      href={`https://www.google.com/maps?q=${selectedScan.location.lat},${selectedScan.location.lon}`}
                      target="_blank"
                      rel="noreferrer noopener"
                      style={{ color: '#38bdf8', textDecoration: 'underline' }}
                    >
                      Open {selectedScan.location.lat}, {selectedScan.location.lon} in Maps ↗
                    </a>
                  ) : (
                    <span style={{ color: '#94a3b8' }}>Not provided</span>
                  )}
                </div>
              </div>
            </div>

            {/* Scan Diagnostics Block */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, fontSize: 13, marginBottom: 14 }}>
              <p><strong>Crop:</strong> {selectedScan.crop}</p>
              <p><strong>Diagnosis:</strong> {selectedScan.predicted_disease}</p>
              <p><strong>Confidence:</strong> {(selectedScan.confidence * 100).toFixed(1)}%</p>
              <p><strong>Farmer Feedback:</strong> {selectedScan.farmer_feedback}</p>
              <p><strong>Verification:</strong> {selectedScan.verification_status}</p>
            </div>

            <button
              className="export-btn"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={() => setSelectedScan(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}