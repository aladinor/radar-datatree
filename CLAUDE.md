# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

radar-datatree is a public-facing repository that provides examples and tutorials for accessing Analysis-Ready Cloud-Optimized (ARCO) weather radar data using the Radar DataTree framework.

**Important Context**: This is the public companion to `raw2zarr` (a private repository). The conversion tool is private due to licensing discussions with UIUC OTM. This repository focuses on **reading and analyzing** already-converted data, not converting raw data.

## Architecture

The Radar DataTree framework uses:
- **xarray.DataTree**: Hierarchical data representation
- **Zarr v3**: Cloud-optimized storage format
- **Icechunk**: ACID-compliant transactional storage with version control
- **xradar**: Radar-specific I/O and analysis tools

Data is organized hierarchically by Volume Coverage Pattern (VCP) and sweep:
```
/VCP-34/sweep_0/  # Variables: DBZH, ZDR, RHOHV, PHIDP, VELOCITY
/VCP-34/sweep_1/
/VCP-12/sweep_0/
...
```

## Available Data

NEXRAD KLOT data on OSN:
- Bucket: `nexrad-arco`
- Prefix: `KLOT-RT`
- Endpoint: `https://umn1.osn.mghpcc.org`
- Access: Anonymous

## Common Commands

### Environment Setup

```bash
# Conda
conda env create -f environment.yml
conda activate radar-datatree

# uv
uv sync

# pip
pip install -e ".[dev]"
```

### Running Notebooks

```bash
cd notebooks
jupyter lab
```

## Key Files

- `notebooks/NEXRAD-KLOT-Demo.ipynb`: Main tutorial notebook demonstrating data access and QVP computation
- `notebooks/demo_functions.py`: Helper functions for QVP computation, visualization, and data utilities
- `environment.yml`: Conda environment specification
- `pyproject.toml`: Python package configuration (for uv/pip installation)

## Reference Paper

Ladino-Rincón & Nesbitt (2025). Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives. arXiv:2510.24943

## License

Apache License 2.0
