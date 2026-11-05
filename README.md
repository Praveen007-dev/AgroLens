# AgroLens

## AI-Powered Crop Disease and Pest Detection

AgroLens is an AI-powered agricultural application designed to help farmers identify crop diseases and pest infestations at an early stage using image-based detection.

The application performs AI inference locally on the farmer's mobile device, provides disease-specific remedies and recommendations, and records scan information in a centralized agricultural data collection system.

The collected data will simulate the type of structured agricultural information that could be shared with agricultural research institutions such as the Indian Institute of Horticultural Research (IIHR), subject to appropriate data-sharing arrangements.

## Core Features

- Crop disease and pest detection using AI.
- On-device inference through a mobile application.
- Image capture and gallery upload.
- Disease prediction and confidence score.
- Disease-specific remedies and recommendations.
- Scan history and agricultural data logging.
- Optional location and crop metadata collection.
- Agricultural research dashboard.
- Simulated research data export for IIHR.

## Architecture

1. Mobile Application — Farmer-facing Flutter application.
2. AI/ML Inference — Crop disease and pest classification.
3. Backend and Database — Scan logging, metadata storage, and API services.
4. Research Dashboard — Agricultural data visualization and research data export.

## Technology Stack

- Flutter and Dart
- Python
- TensorFlow / PyTorch
- TensorFlow Lite
- FastAPI
- SQLite
- React or an equivalent lightweight dashboard framework
- Git and GitHub

## Project Status

Initial repository setup.

## Run locally

Start the backend from the repository root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Start the dashboard in a second terminal:

```powershell
Set-Location dashboard
npm install
npm run dev -- --host 0.0.0.0
```

Start the Flutter web app in a third terminal. If Flutter is installed at a
different location, replace the executable path:

```powershell
Set-Location mobile
& C:\Users\wwwpr\AgroLens\flutter\bin\flutter.bat pub get
& C:\Users\wwwpr\AgroLens\flutter\bin\flutter.bat run -d web-server --web-hostname 0.0.0.0 --web-port 5000
```

The local URLs are:

- Backend API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- Research dashboard: `http://127.0.0.1:5173`
- Flutter Web: `http://127.0.0.1:5000`

The Flutter client uses the backend for authentication, agriculture data, and
scan submission. Android emulators use `10.0.2.2`; Flutter Web derives the
backend host from the browser URL. For a physical Android device, pass
`--dart-define=AGROLENS_API_HOST=YOUR_LAN_IP`.

From another system on the same Wi-Fi, replace `127.0.0.1` with this computer's
LAN address, currently `172.17.26.24`.

## Disclaimer

AgroLens is a prototype developed for demonstration and research purposes. It is not connected to IIHR or any government agricultural department unless a formal integration is established.
