import React, { useState, useMemo } from 'react';
import './App.css';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, CartesianGrid
} from 'recharts';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ec4899', '#8b5cf6'];

const mockScans = [
  {
    scan_id: "scan_101",
    timestamp: "2026-11-01T09:30:00Z",
    crop: "Tomato",
    predicted_disease: "Early Blight",
    confidence: 0.92,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 14.62, lon: 74.83 }
  },
  {
    scan_id: "scan_102",
    timestamp: "2026-11-01T11:15:00Z",
    crop: "Tomato",
    predicted_disease: "Late Blight",
    confidence: 0.54,
    farmer_feedback: "disputed",
    verification_status: "pending",
    location: null
  },
  {
    scan_id: "scan_103",
    timestamp: "2026-11-02T08:00:00Z",
    crop: "Potato",
    predicted_disease: "Early Blight",
    confidence: 0.88,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 14.61, lon: 74.85 }
  },
  {
    scan_id: "scan_104",
    timestamp: "2026-11-02T14:40:00Z",
    crop: "Cotton",
    predicted_disease: "Bacterial Blight",
    confidence: 0.49,
    farmer_feedback: "unreviewed",
    verification_status: "pending",
    location: null
  },
  {
    scan_id: "scan_105",
    timestamp: "2026-11-03T10:10:00Z",
    crop: "Paddy",
    predicted_disease: "Blast Disease",
    confidence: 0.95,
    farmer_feedback: "confirmed",
    verification_status: "expert_verified",
    location: { lat: 14.63, lon: 74.82 }
  },
  {
    scan_id: "scan_106",
    timestamp: "2026-11-03T16:20:00Z",
    crop: "Paddy",
    predicted_disease: "Brown Spot",
    confidence: 0.78,
    farmer_feedback: "unreviewed",
    verification_status: "rejected",
    location: null
  },
  {
    scan_id: "scan_107",
    timestamp: "2026-11-04T07:45:00Z",
    crop: "Corn",
    predicted_disease: "Common Rust",
    confidence: 0.89,
    farmer_feedback: "confirmed",
    verification_status: "pending",
    location: { lat: 14.60, lon: 74.80 }
  }
];

export default function App() {
  const [scans] = useState(mockScans);
  const [selectedScan, setSelectedScan] = useState(null);

  const [filterCrop, setFilterCrop] = useState('');
  const [filterDisease, setFilterDisease] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [confidenceMin, setConfidenceMin] = useState(0);

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
              <tr><td colSpan="8" style={{ textAlign: 'center', padding: 24, color: '#94a3b8' }}>No scans match the current filters.</td></tr>
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

      {selectedScan && (
        <div className="modal-backdrop" onClick={() => setSelectedScan(null)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h3 style={{ marginBottom: 12 }}>Scan Record Details</h3>
            <p><strong>Scan ID:</strong> {selectedScan.scan_id}</p>
            <p><strong>Crop:</strong> {selectedScan.crop}</p>
            <p><strong>Predicted Diagnosis:</strong> {selectedScan.predicted_disease}</p>
            <p><strong>Confidence:</strong> {(selectedScan.confidence * 100).toFixed(1)}%</p>
            <p><strong>Farmer Feedback:</strong> {selectedScan.farmer_feedback}</p>
            <p><strong>Verification Status:</strong> {selectedScan.verification_status}</p>
            <p><strong>Location Coordinates:</strong> {selectedScan.location ? `${selectedScan.location.lat}, ${selectedScan.location.lon}` : 'Not provided'}</p>
            <button
              className="export-btn"
              style={{ marginTop: 16 }}
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