# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and Oxlint's TypeScript related rules in your project.

# AgroLens — Research Dashboard

Web frontend for agricultural researchers to monitor crop disease telemetry, farmer validation, and verification statuses.

> **Disclaimer:** Hackathon prototype. This system is not connected to IIHR, government agricultural departments, or any official institutional database.

## Features
- **Overview Metrics:** Total scans, unique crop varieties, identified disease categories, low-confidence scan alerts (<60%), farmer confirmations, and expert-verified records.
- **Disease & Pest Analytics:** Visual distribution charts using Recharts (disease prevalence and crop breakdown).
- **Multi-parameter Filtering:** Instant client-side filtering by crop type, disease label, verification status, and confidence range slider.
- **Scan Telemetry Table & Inspector:** Detailed modal viewer handling optional telemetry (gracefully handles missing GPS coordinates).
- **Backend API:** Loads and records scan data through the FastAPI `/api/scans` endpoints and supports JSON/CSV exports.

## Getting Started

### Installation
```

Start the backend from the repository root before opening the dashboard:

```powershell
python -m uvicorn backend.app.main:app --reload
```

The dashboard uses `http://127.0.0.1:8000` by default. Set
`VITE_API_BASE_URL` when the backend runs at another origin.bash
cd dashboard
npm install