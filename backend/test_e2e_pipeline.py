import urllib.request
import json
from uuid import uuid4
from datetime import datetime, timezone

def test_pipeline():
    print("==================================================")
    print("AGROLENS END-TO-END PIPELINE & TELEMETRY TEST")
    print("==================================================")
    
    # 1. Simulate Image Capture & AI Model Inference
    scan_id = "iihr-test-" + str(uuid4())[:8]
    sample_crop = "Tomato"
    disease_label = "Tomato___Early_blight"
    confidence = 0.942

    remedies = {
        "disease": "Early Blight (Alternaria solani)",
        "organic_control": "Spray neem oil (0.5%) or Trichoderma viride culture.",
        "chemical_control": "Mancozeb 75 WP @ 2g/L or Chlorothalonil 75 WP @ 2g/L.",
        "cultural_practices": "Crop rotation with non-solanaceous crops, staking plants, removing lower infected leaves."
    }
    print(f"\n[STEP 1] Mobile Camera Image Captured & Processed:")
    print(f"  - Crop Identified: {sample_crop}")
    print(f"  - AI Disease Prediction: {disease_label} (Confidence: {confidence * 100:.1f}%)")
    print(f"  - Agronomic Remedy (Chemical): {remedies['chemical_control']}")
    print(f"  - Agronomic Remedy (Organic): {remedies['organic_control']}")

    # 2. Package Scan with IIHR Bengaluru Geotag
    payload = {
        "scan_id": scan_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "crop": sample_crop,
        "image_path": "file:///device/camera/photo_tomato_leaf_01.jpg",
        "image_reference": "tomato_early_blight_iihr_sample.jpg",
        "ai_prediction": {
            "prediction_id": "pred-" + scan_id,
            "crop": sample_crop,
            "disease_label": disease_label,
            "confidence": confidence,
            "top_predictions": [
                {"label": "Tomato___Early_blight", "confidence": 0.942},
                {"label": "Tomato___Late_blight", "confidence": 0.038},
                {"label": "Tomato___healthy", "confidence": 0.020}
            ],
            "is_low_confidence": False,
            "model_version": "agrolens-mobilenetv3-v1.0",
            "inference_timestamp": datetime.now(timezone.utc).isoformat()
        },
        "farmer_feedback": {
            "is_confirmed": True,
            "corrected_label": None,
            "notes": "Spotted dark concentric rings on lower leaves at Hesaraghatta farm",
            "submitted_at": datetime.now(timezone.utc).isoformat()
        },
        "location": {
            "latitude": 13.1348,
            "longitude": 77.4965,
            "region": "Karnataka",
            "has_consent": True
        },
        "sync_status": "synced",
        "metadata": {
            "source": "mobile_flutter_app",
            "device": "Pixel 8",
            "app_version": "1.0.0+1"
        }
    }

    # 3. Submit Scan via Mobile API endpoint (POST /api/v1/scans)
    print(f"\n[STEP 2] Submitting to AgroLens Mobile API (/api/v1/scans)...")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/v1/scans",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-Client-App": "AgroLens"}
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read().decode())
    assert resp.status == 201, f"Expected 201 Created, got {resp.status}"
    print(f"  [OK] Submission Success: Status {resp.status}, Response: {result}")

    # 4. Fetch Scan Detail (/api/scans/{scan_id})
    print(f"\n[STEP 3] Verifying Scan Persistence in Database (/api/scans/{scan_id})...")
    req2 = urllib.request.Request(f"http://127.0.0.1:8000/api/scans/{scan_id}")
    resp2 = urllib.request.urlopen(req2)
    scan_record = json.loads(resp2.read().decode())
    assert scan_record["scan_id"] == scan_id
    assert scan_record["crop"] == sample_crop
    assert scan_record["disease_label"] == disease_label
    print(f"  [OK] Record Verified: ID={scan_record['scan_id']}, Crop={scan_record['crop']}, Disease={scan_record['disease_label']}, Confidence={scan_record['confidence']}")

    # 5. Verify Research Dashboard Telemetry (/api/scans?limit=10)
    print(f"\n[STEP 4] Verifying Research Dashboard Data Feed (/api/scans)...")
    req3 = urllib.request.Request("http://127.0.0.1:8000/api/scans?limit=10")
    resp3 = urllib.request.urlopen(req3)
    dashboard_scans = json.loads(resp3.read().decode())
    found_in_feed = any(s["scan_id"] == scan_id for s in dashboard_scans["scans"])
    assert found_in_feed, "Scan record not found in dashboard scans feed!"
    matching_scan = next(s for s in dashboard_scans["scans"] if s["scan_id"] == scan_id)
    print(f"  [OK] Found in Dashboard Feed! Total Scans in DB = {dashboard_scans['total']}")
    print(f"  [OK] Geolocation Received: Lat {matching_scan['latitude']}, Long {matching_scan['longitude']} (Consent: {bool(matching_scan['location_consent'])})")

    # 6. Verify Dashboard Summary (/api/analytics/summary)
    print(f"\n[STEP 5] Verifying Dashboard Analytics Summary (/api/analytics/summary)...")
    req4 = urllib.request.Request("http://127.0.0.1:8000/api/analytics/summary")
    resp4 = urllib.request.urlopen(req4)
    summary = json.loads(resp4.read().decode())
    assert summary["total_scans"] >= 1
    assert sample_crop in summary["crop_counts"]
    print(f"  [OK] Total Scans Tracked: {summary['total_scans']}")
    print(f"  [OK] Crop Breakdown: {summary['crop_counts']}")
    print(f"  [OK] Disease Breakdown: {summary['disease_counts']}")

    # 7. Verify IIHR Research Export (/api/export/scans?format=json & csv)
    print(f"\n[STEP 6] Verifying IIHR Research Data Export (/api/export/scans)...")
    req5 = urllib.request.Request("http://127.0.0.1:8000/api/export/scans?format=json")
    resp5 = urllib.request.urlopen(req5)
    export_json = json.loads(resp5.read().decode())
    iihr_entry = next((s for s in export_json if s["scan_id"] == scan_id), None)
    assert iihr_entry is not None, "Export does not contain the scan!"
    # Verify privacy preservation: private farmer notes & exact coordinates are omitted from research export
    assert "farmer_feedback" not in iihr_entry
    assert "feedback_text" not in iihr_entry
    assert "latitude" not in iihr_entry
    print(f"  [OK] IIHR JSON Export Validated: {iihr_entry}")
    print(f"  [OK] Privacy Preserved: Farmer feedback and private device info excluded from research export.")

    req6 = urllib.request.Request("http://127.0.0.1:8000/api/export/scans?format=csv")
    resp6 = urllib.request.urlopen(req6)
    csv_text = resp6.read().decode("utf-8")
    assert scan_id in csv_text
    print(f"  [OK] IIHR CSV Export Validated ({len(csv_text.splitlines())} rows).")

    print("\n==================================================")
    print("ALL PIPELINE STAGES PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    test_pipeline()
