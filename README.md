# Engineering Data Query and Spatial Visualization System Using EAV Data

## Overview

This repository contains an independently developed academic prototype for analysing heterogeneous engineering data represented using an Entity-Attribute-Value model.

The system will generate synthetic engineering component data, store it in SQLite, perform data profiling and quality analysis, transform EAV records into an analytical representation, and benchmark different query approaches.

A simplified spatial visualization interface may be added after the core data processing system has been implemented and validated.

## Objectives

1. Generate synthetic engineering component datasets programmatically.
2. Store heterogeneous metadata using an EAV-style schema.
3. Perform data profiling and quality checks.
4. Detect controlled anomalies.
5. Transform EAV records into a Pandas analytical representation.
6. Compare direct SQLite EAV queries with Pandas filtering.
7. Benchmark performance at multiple dataset sizes.
8. Optionally visualize filtered components on a simplified 2D layout.

## Technology Stack

Core technologies:

- Python
- SQLite
- Pandas
- NumPy
- Matplotlib

Planned backend:

- FastAPI
- Pydantic
- Uvicorn

Possible frontend:

- TypeScript
- React
- SVG spatial visualization

## Academic Disclaimer

This is an independently developed academic prototype inspired by general concepts encountered during a summer internship.

No proprietary company datasets, databases, engineering models, software systems, or internal tools are used.

All experimental datasets are generated synthetically using Python.

## Development Status

Repository initialized.

Next step:

Implement and validate the synthetic engineering dataset generator.
