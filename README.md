# Engineering Data Query and Spatial Visualization System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646CFF.svg)](https://vitejs.dev/)

An end-to-end academic prototype for processing, querying, and visually exploring heterogeneous engineering component data using an **Entity-Attribute-Value (EAV)** schema transformed into a **Canonical Analytical Model**.

---

## 📌 Project Overview

Engineering systems frequently manage highly dynamic, domain-specific attributes that suit an **EAV storage pattern**. However, querying and visualizing EAV structures at scale introduces performance and data-quality challenges. 

This project bridges that gap by providing a full pipeline:
1. **Generating & Profiling** synthetic EAV engineering datasets to detect schema pollution and anomalies.
2. **Transforming** semi-structured EAV data into a structured **Canonical Model**.
3. **Exposing** performant querying endpoints through a **FastAPI** backend.
4. **Visualizing & Inspecting** components interactively via an SVG-based 2D spatial viewer in **React**.

> **Academic Disclaimer:** This independent project uses **100% synthetically generated data**. It contains no proprietary, corporate, or confidential datasets, models, or internal tooling.

---

## 🏗️ Architecture & Core Workflow

```text
┌─────────────────────────┐
│ Synthetic EAV Data Gen  │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│   SQLite / EAV Storage  │
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│ Profiling & Quality     │ ──► (Detect Schema Pollution & Anomalies)
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│ Canonical Data Model    │ ──► [Component ID | Type | Discipline | Zone | Geometry | Attributes]
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│ Backend REST API        │ ──► FastAPI Services (Query & Intelligence/Recommendation Engine)
└───────────┬─────────────┘
            │
            v
┌─────────────────────────┐
│ Interactive React UI    │ ──► Query Builder + 2D SVG Spatial Viewer & Component Inspector
└─────────────────────────┘

```

---

## 🛠️ Tech Stack

| Layer | Technologies |
| --- | --- |
| **Backend API** | Python 3.x, FastAPI, Pydantic, Uvicorn |
| **Database & Analytics** | SQLite, Pandas, NumPy |
| **Frontend UI** | React 18, TypeScript, Vite, SVG, Lucide React |
| **Testing & Scripting** | `unittest`, Matplotlib, PowerShell Automation |

---

## 📂 Project Structure

```text
engineering-data-query-system/
├── backend/                  # FastAPI Application Layer
│   ├── app/
│   │   ├── models/           # Pydantic schemas & canonical models
│   │   ├── repositories/     # SQLite / EAV abstraction layer
│   │   ├── services/         # Query execution & recommendation engine
│   │   ├── storage/          # Local database storage handler
│   │   ├── engine.py         # Query execution logic
│   │   ├── main.py           # API routes & server initialization
│   │   └── profiler.py       # Data quality & schema profiling
│   └── tests/                # Unit and service-level integration tests
├── frontend/                 # React + TypeScript Frontend
│   └── src/
│       ├── components/       # UI Components (EngineeringViewer.tsx, etc.)
│       ├── App.tsx           # Main application state & layout
│       └── main.tsx          # Application entry point
├── data/                     # Data directory (benchmarks, canonical, generated)
├── results/                  # Generated figures, tables, and benchmark reports
├── scripts/                  # Data transformation, generation, and profiling tools
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies
└── run.ps1                   # Unified PowerShell control script

```

---

## 🚀 Quick Start Guide

### Prerequisites

* **Python 3.10+**
* **Node.js 18+** & `npm`
* **PowerShell** (for automated execution)

### 1. Setup & Installation

Clone the repository and install dependencies:

```powershell
# Clone the repository
git clone [https://github.com/Yashhchopraa/engineering-data-query-system.git](https://github.com/Yashhchopraa/engineering-data-query-system.git)
cd engineering-data-query-system

# Create and activate Python Virtual Environment
python -m venv .venv
.\.venv\Scripts\activate

# Install Backend Dependencies
pip install -r requirements.txt

# Install Frontend Dependencies
cd frontend
npm install
cd ..

```

### 2. Running the Application

Use the consolidated PowerShell utility script `run.ps1`:

```powershell
# Start both Backend API and Frontend Dev Server
.\run.ps1 start

```

Once started, access the interfaces at:

* **Frontend App:** `http://localhost:5173`
* **Backend Swagger Docs:** `http://127.0.0.1:8000/docs`

---

## ⚡ PowerShell Command Reference

The `run.ps1` script provides convenient commands to manage the system life cycle:

| Command | Action |
| --- | --- |
| `.\run.ps1 start` | Launches FastAPI backend and Vite frontend server simultaneously |
| `.\run.ps1 generate` | Triggers synthetic EAV component data generation |
| `.\run.ps1 benchmark` | Runs performance and execution time benchmarks |
| `.\run.ps1 tree` | Displays clean project directory topology |

---

## 🎯 Key Features & Capabilities

* **EAV Data Profiling:** Automatically flags missing attributes, duplicate records, non-standard unit types, and schema drift.
* **Canonical Model Transformation:** Converts EAV structures into standardized JSON/Relational structures for performant downstream analytical processing.
* **2D Spatial Viewer:** Interactive SVG canvas supporting pan, zoom, fit-to-view, full-screen, and dynamic spatial component highlighting.
* **Attribute & Discipline Filtering:** Real-time component filtering by engineering domain (e.g., Mechanical, Electrical, Structural) and specific custom parameters.
* **Backend Intelligence Layer:** Built-in recommendation service built on top of component attributes to identify matching and replacement parts (backend capability).

---

## 📈 Future Scope

* [ ] Extend recommendation engine integration directly into the React UI.
* [ ] Add 3D model visualization support (e.g., via Three.js / WebGL).
* [ ] Support Industry Foundation Classes (IFC) and CAD file format ingestion.
* [ ] Implement advanced cross-discipline multi-attribute queries.

---

## 📜 License & Acknowledgments

Distributed under the **MIT License**. Developed as an independent academic prototype exploring EAV query optimization and spatial data handling.

```

```