import React, { useState, useMemo, useRef } from 'react';
import './App.css';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid
} from 'recharts';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6'];

const AGRONOMIC_GUIDE = {
  "Early Blight": {
    soil: "Well-aerated sandy loam rich in organic matter; pH 6.0–6.8. Avoid waterlogged or hardpan soils that restrict root aeration.",
    precautions: [
      "Soil Solarization: Cover nursery beds with transparent polyethylene sheets (25-micron) for 30–45 days during summer.",
      "Biological Seed/Root Dip: Treat seedlings with Trichoderma harzianum or T. viride @ 5g/kg seed or 10g/L root dip prior to planting.",
      "Cultural Sanitation: Prune lower leaves up to 20 cm from the ground to prevent splash-borne fungal inocula; burn infected debris.",
      "Canopy Management: Maintain 60x45 cm plant spacing and avoid overhead irrigation to minimize leaf wetness duration."
    ]
  },
  "Late Blight": {
    soil: "Light, fertile loam with high drainage capacity; pH 5.8–6.5. Avoid heavy clay soil prone to prolonged moisture saturation.",
    precautions: [
      "Certified Planting Material: Use certified disease-free seed tubers; discard seed tubers exhibiting internal rust-brown discoloration.",
      "Prophylactic Spray: During overcast, humid (>85%), or cool (12–20°C) spells, apply Mancozeb (0.2%) or Copper Oxychloride (0.25%).",
      "Field Hygiene: Destroy and deeply bury all volunteer solanaceous plants and infected dump heaps before flowering.",
      "Water Management: Regulate furrow irrigation; avoid night-time watering and prolonged standing water."
    ]
  },
  "Bacterial Blight": {
    soil: "Deep, well-drained medium black to alluvial clay loam; pH 6.5–7.5. Avoid soils with acute potassium deficiency.",
    precautions: [
      "Acid Delinting & Seed Dressing: Delint cotton seeds with concentrated sulfuric acid (100 ml/kg) followed by Streptocycline (100 ppm) treatment.",
      "Nutrient Balance: Ensure split applications of potassium to enhance natural plant resistance; prevent excessive basal nitrogen.",
      "Sanitary Field Routine: Restrict movement of workers and machinery through fields while morning dew or raindrops coat foliage.",
      "Biocontrol Foliar Spray: Spray Pseudomonas fluorescens @ 10g/L at early vegetative stage."
    ]
  },
  "Blast Disease": {
    soil: "Clay loam or alluvial soil with high silica content and moderate organic carbon; pH 5.5–6.5. Avoid silica-deficient fields.",
    precautions: [
      "Split N-Fertilization: Avoid heavy single basal doses of nitrogenous fertilizers; adopt split applications based on leaf color chart (LCC).",
      "Seed Soak: Soak seeds in Carbendazim 50% WP (2g/kg) or Trichoderma viride (10g/kg) for 24 hours prior to incubation.",
      "Water Level Regulation: Maintain continuous 3–5 cm shallow water standing in the field during peak tillering; avoid moisture stress.",
      "Weed Sanitation: Eliminate alternate hosts such as Echinochloa grass along bunds and irrigation channels."
    ]
  },
  "Brown Spot": {
    soil: "Nutrient-depleted soils, specifically those deficient in potassium, zinc, manganese, and organic carbon; pH 5.0–6.5.",
    precautions: [
      "Micronutrient Amelioration: Apply Zinc Sulphate (25 kg/ha) and Potassium Chloride (MOP) as basal or early top-dressing.",
      "Hot Water Seed Treatment: Treat seeds in hot water at 52–54°C for 10–12 minutes to eradicate seed-borne fungal mycelium.",
      "Soil Health Enrichment: Apply Farm Yard Manure (FYM @ 10 t/ha) or green manure (Dhaincha/Sunn hemp) prior to puddling.",
      "Chemical Control: Spray Mancozeb (2g/L) or Tricyclazole (0.6g/L) at boot leaf and early grain-filling stages if spotting appears."
    ]
  },
  "Common Rust": {
    soil: "Loose, well-drained silt loam to sandy loam with neutral pH (6.0–7.2) and balanced N-P-K reserves.",
    precautions: [
      "Resistant Hybrid Selection: Plant certified rust-resistant hybrids during the standard planting window.",
      "Optimum Plant Density: Avoid excessive plant population density; maintain 60–75 cm row spacing to foster airflow.",
      "Timely Protective Spray: Apply Mancozeb (2.5g/L) or Azoxystrobin (1ml/L) as soon as early pustules appear on lower leaves.",
      "Crop Rotation: Rotate fields with non-graminaceous legumes (soybean, gram) to disrupt the pathogen cycle."
    ]
  },
  "Analysis Pending": {
    soil: "Maintain recommended crop-specific pH and adequate drainage according to standard soil health recommendations.",
    precautions: [
      "Isolate suspected leaves and monitor symptom progression for 24–48 hours.",
      "Avoid indiscriminate chemical spraying until diagnosis is verified by an agronomy expert."
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
    location: { lat: 14.62, lon: 74.83 }
  },
  {
    scan_id: "scan_102",
    timestamp: "2026-11-04T10:15:00Z",
    crop: "Tomato",
    predicted_disease: "Late Blight",
    confidence: 0.54,
    farmer_feedback: "disputed",
    verification_status: "pending",
    location: null
  },
  {
    scan_id: "scan_103",
    timestamp: "2026-11-04T11:00:00Z",
    crop: "Potato",
    predicted_disease: "Early Blight",
    confidence: 0.88,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 14.61, lon: 74.85 }
  },
  {
    scan_id: "scan_104",
    timestamp: "2026-11-04T12:40:00Z",
    crop: "Cotton",
    predicted_disease: "Bacterial Blight",
    confidence: 0.49,
    farmer_feedback: "unreviewed",
    verification_status: "pending",
    location: null
  },
  {
    scan_id: "scan_105",
    timestamp: "2026-11-04T13:10:00Z",
    crop: "Paddy",
    predicted_disease: "Blast Disease",
    confidence: 0.95,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 14.63, lon: 74.82 }
  },
  {
    scan_id: "scan_106",
    timestamp: "2026-11-04T14:20:00Z",
    crop: "Paddy",
    predicted_disease: "Brown Spot",
    confidence: 0.78,
    farmer_feedback: "unreviewed",
    verification_status: "rejected",
    location: null
  },
  {
    scan_id: "scan_107",
    timestamp: "2026-11-04T15:00:00Z",
    crop: "Corn",
    predicted_disease: "Common Rust",
    confidence: 0.89,
    farmer_feedback: "confirmed",
    verification_status: "pending",
    location: { lat: 14.60, lon: 74.80 }
  }
];

export default function App() {
  const [scans, setScans] = useState(initialScans);
  const [selectedScan, setSelectedScan] = useState(null);

  // Scanner state
  const [previewUrl, setPreviewUrl] = useState(null);
  const [scanCrop, setScanCrop] = useState('Tomato');
  const [isScanning, setIsScanning] = useState(false);
  const fileInputRef = useRef(null);

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

  const handleStartScan = () => {
    if (!previewUrl) {
      alert("Please choose or capture a leaf photo first.");
      return;
    }

    setIsScanning(true);

    setTimeout(() => {
      const newRecord = {
        scan_id: `scan_${Date.now().toString().slice(-4)}`,
        timestamp: new Date().toISOString(),
        crop: scanCrop,
        predicted_disease: "Analysis Pending",
        confidence: 0.75,
        farmer_feedback: "unreviewed",
        verification_status: "pending",
        location: null
      };

      setScans(prev => [newRecord, ...prev]);
      setIsScanning(false);
      setPreviewUrl(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      alert(`Scan ${newRecord.scan_id} recorded! Ready for model inference.`);
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
      <div className="banner">
        <div>
          <strong>AgroLens Prototype:</strong> Research analytics dashboard. Not connected to IIHR or government agencies.
        </div>
        <span className="banner-badge">DEMONSTRATION MOCK DATA ACTIVE</span>
      </div>

      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28 }}>AgroLens Research Dashboard</h1>
          <p style={{ color: '#94a3b8', fontSize: 14 }}>Field Scan Telemetry & Disease Analytics</p>
        </div>
        <div style={{ display: 'flex', gap: 10 }}>
          <button className="export-btn" onClick={() => alert("Backend CSV export will connect to /api/export/scans?format=csv")}>Export CSV</button>
          <button className="export-btn" onClick={() => alert("Backend JSON export will connect to /api/export/scans?format=json")}>Export JSON</button>
        </div>
      </header>

      {/* Leaf Scan & Image Intake */}
      <div style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: 20, marginBottom: 24 }}>
        <h3 style={{ marginBottom: 12, fontSize: 17, color: '#f8fafc' }}>Leaf Scan & Image Intake</h3>
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

        {/* Dynamic Crop Soil Preview */}
        <div style={{
          marginTop: 14,
          padding: '10px 14px',
          background: '#0f172a',
          borderRadius: 6,
          border: '1px solid #334155',
          fontSize: 12,
          color: '#94a3b8'
        }}>
          <strong style={{ color: '#38bdf8' }}>Optimal Soil for {scanCrop}: </strong>
          {scanCrop === 'Tomato' && 'Loamy, well-draining, pH 6.0–6.8. Rich in calcium to avoid blossom end rot.'}
          {scanCrop === 'Potato' && 'Loose, well-aerated sandy loam, pH 5.0–6.0. High organic matter.'}
          {scanCrop === 'Paddy' && 'Clay or clayey loam, pH 5.5–6.5. High water holding capacity.'}
          {scanCrop === 'Cotton' && 'Deep black clayey soils (regur) or fertile alluvium, pH 6.0–7.5.'}
          {scanCrop === 'Corn' && 'Well-aerated silt loam or sandy loam, pH 6.0–7.2. High nitrogen requirement.'}
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
              <th>Timestamp</th>
              <th>Crop</th>
              <th>Predicted Disease</th>
              <th>Confidence</th>
              <th>Farmer Feedback</th>
              <th>Verification</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filteredScans.length === 0 ? (
              <tr><td colSpan="8" style={{ textAlign: 'center', padding: 24, color: '#94a3b8' }}>No scans match current filters.</td></tr>
            ) : (
              filteredScans.map(scan => (
                <tr key={scan.scan_id}>
                  <td><code>{scan.scan_id}</code></td>
                  <td>{new Date(scan.timestamp).toLocaleString()}</td>
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

      {/* Record Detail Modal with Soil & Precautions */}
      {selectedScan && (
        <div className="modal-backdrop" onClick={() => setSelectedScan(null)}>
          <div className="modal-box" style={{ maxWidth: 620 }} onClick={e => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ margin: 0, fontSize: 18 }}>Field Record & Agronomic Advisory</h3>
              <span className="badge badge-gray">{selectedScan.scan_id}</span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, fontSize: 13, marginBottom: 14 }}>
              <p><strong>Crop:</strong> {selectedScan.crop}</p>
              <p><strong>Diagnosis:</strong> {selectedScan.predicted_disease}</p>
              <p><strong>Confidence:</strong> {(selectedScan.confidence * 100).toFixed(1)}%</p>
              <p><strong>Farmer Feedback:</strong> {selectedScan.farmer_feedback}</p>
              <p><strong>Verification:</strong> {selectedScan.verification_status}</p>
              <p><strong>Location:</strong> {selectedScan.location ? `${selectedScan.location.lat}, ${selectedScan.location.lon}` : 'Not provided'}</p>
            </div>

            <hr style={{ borderColor: '#334155', margin: '14px 0' }} />

            {/* Soil Health Section */}
            <div style={{ marginBottom: 14 }}>
              <h4 style={{ fontSize: 14, color: '#38bdf8', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                🌱 Soil Profile & Condition Guidelines
              </h4>
              <p style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.5, background: '#0f172a', padding: '10px 12px', borderRadius: 6, border: '1px solid #334155' }}>
                {AGRONOMIC_GUIDE[selectedScan.predicted_disease]?.soil || "Standard fertile agricultural loam with proper drainage."}
              </p>
            </div>

            {/* Precautions & Management Section */}
            <div style={{ marginBottom: 16 }}>
              <h4 style={{ fontSize: 14, color: '#f59e0b', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                ⚠️ Standard Agronomic Precautions & Management Practices
              </h4>
              <ul style={{ fontSize: 13, color: '#cbd5e1', paddingLeft: 20, lineHeight: 1.5 }}>
                {(AGRONOMIC_GUIDE[selectedScan.predicted_disease]?.precautions || [
                  "Monitor plant progression daily.",
                  "Avoid moisture stagnation around roots."
                ]).map((precaution, idx) => (
                  <li key={idx} style={{ marginBottom: 6 }}>{precaution}</li>
                ))}
              </ul>
            </div>

            <p style={{ fontSize: 11, color: '#64748b', fontStyle: 'italic', marginBottom: 14 }}>
              *Standard agricultural management practices shown for prototype educational purposes only. Not affiliated with real institutional servers.
            </p>

            <button
              className="export-btn"
              style={{ width: '100%', justifyContent: 'center' }}
              onClick={() => setSelectedScan(null)}
            >
              Close Advisory
            </button>
          </div>
        </div>
      )}
    </div>
  );
}