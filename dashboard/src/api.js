const browserApiBaseUrl = typeof window === 'undefined'
  ? 'http://127.0.0.1:8000'
  : `${window.location.protocol}//${window.location.hostname}:8000`;
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || browserApiBaseUrl
).replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: 'application/json',
      ...(options.body ? { 'Content-Type': 'application/json' } : {}),
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    let detail = `Request failed with HTTP ${response.status}.`;
    try {
      const body = await response.json();
      if (body.detail) detail = body.detail;
    } catch {
      // Preserve the HTTP error when the server does not return JSON.
    }
    throw new Error(detail);
  }

  return response;
}

function mapScan(scan) {
  const hasLocation = scan.location_consent && (
    scan.latitude !== null && scan.latitude !== undefined &&
    scan.longitude !== null && scan.longitude !== undefined
  );
  return {
    scan_id: scan.scan_id,
    timestamp: scan.scan_timestamp,
    crop: scan.crop,
    predicted_disease: scan.disease_label,
    confidence: scan.confidence,
    farmer_feedback: 'unreviewed',
    verification_status: scan.verification_status || 'pending',
    location: hasLocation ? { lat: scan.latitude, lon: scan.longitude } : null,
    farmer: null,
  };
}

export async function fetchScans({ page = 1, limit = 100 } = {}) {
  const response = await request(
    `/api/scans?page=${page}&limit=${limit}`,
  );
  const body = await response.json();
  return body.scans.map(mapScan);
}

export async function createScan({
  crop,
  timestamp,
  diseaseLabel = 'Analysis Pending',
  confidence = 0.75,
  location,
  farmer,
}) {
  const response = await request('/api/scans', {
    method: 'POST',
    body: JSON.stringify({
      scan_id: `dashboard-${crypto.randomUUID()}`,
      crop,
      scan_timestamp: timestamp,
      model_version: 'dashboard-intake',
      disease_label: diseaseLabel,
      confidence,
      location_consent: Boolean(location),
      latitude: location?.lat,
      longitude: location?.lon,
      additional_metadata: farmer ? { farmer } : null,
    }),
  });
  return response.json();
}

export function exportScans(format) {
  window.open(
    `${API_BASE_URL}/api/export/scans?format=${format}`,
    '_blank',
    'noopener,noreferrer',
  );
}
