export const mockScans = [
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
    confidence: 0.54, // low confidence (<0.60)
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
    confidence: 0.49, // low confidence
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