# AgroLens — Project Specification

## 1. Project Overview

AgroLens is an AI-powered crop disease and pest early-detection system designed to help farmers identify crop health issues using images captured through a mobile application.

The application performs on-device AI inference, provides disease-specific remedies, and records structured scan information in a centralized agricultural data collection system.

The collected data simulates the type of agricultural information that could be shared with agricultural research institutions such as the Indian Institute of Horticultural Research (IIHR), subject to future data-sharing arrangements.

## 2. Core Objectives

- Detect crop diseases and pest infestations from plant images.
- Perform AI inference locally on the mobile device.
- Provide disease/pest predictions and confidence scores.
- Recommend appropriate remedies and next steps.
- Record every scan and its associated agricultural metadata.
- Provide a research dashboard for viewing and analyzing scan records.
- Simulate the preparation and export of agricultural research datasets.

## 3. System Architecture

### Layer 1 — Farmer Mobile Application
Technology: Flutter

Responsibilities:
- Capture images using the camera.
- Select images from the gallery.
- Collect crop and optional farm information.
- Run local AI inference.
- Display prediction, confidence, and remedies.
- Submit scan records to the backend.
- Display scan history where supported.

### Layer 2 — On-device AI Inference
Technology: Python for model development; TensorFlow Lite for mobile deployment.

Responsibilities:
- Preprocess crop images.
- Classify diseases and pests.
- Return the predicted class and confidence.
- Handle low-confidence predictions.
- Provide model version information.

### Layer 3 — Backend and Agricultural Data Collection
Technology: Python, FastAPI, SQLite.

Responsibilities:
- Receive scan records from the mobile application.
- Validate incoming data.
- Store scan records and metadata.
- Store optional image references.
- Provide APIs for scan history and research data retrieval.
- Provide data export functionality.

### Layer 4 — Agricultural Research Dashboard
Technology: React or an equivalent lightweight web framework.

Responsibilities:
- Display scan records.
- Visualize disease/pest distribution.
- Filter data by crop, disease, location, and date.
- Display geographic distribution when location is available.
- Show model confidence and feedback information.
- Simulate research data preparation for IIHR.

## 4. Data Collection Principles

Each scan should have a unique scan identifier.

The system should distinguish:
- AI-predicted disease/pest.
- AI confidence score.
- Farmer-provided crop information.
- Farmer confirmation or correction, if available.
- Expert-verified diagnosis, if available.

An AI prediction must not automatically be treated as an expert-confirmed diagnosis.

Location, farmer identity, and environmental information are optional and must only be collected when available and appropriately consented to.

## 5. Shared Development Rules

- All developers work in separate Git branches.
- All modules must follow shared contracts under `contracts/`.
- Each module must be independently runnable and testable.
- Use mock data when another module is unavailable.
- Do not modify another developer's module without coordination.
- Do not change shared contracts without approval.
- Each module must include setup instructions and tests.
- All modules must be integrated and tested before the final demonstration.

## 6. Prototype Limitations

AgroLens is a hackathon prototype.

The application is not connected to IIHR or any government agricultural department unless a formal integration is established.

The database and research dashboard simulate the collection and preparation of agricultural scan data for future research use.
