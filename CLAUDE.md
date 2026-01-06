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
# Conda (recommended)
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

### Linting

```bash
ruff check .          # Run linting
ruff format .         # Format code
ruff check --fix .    # Auto-fix linting issues
```

## Quick Start (Programmatic Access)

```python
import xarray as xr
import icechunk as ic

# Connect to KLOT data
storage = ic.s3_storage(
    bucket='nexrad-arco',
    prefix='KLOT-RT',
    endpoint_url='https://umn1.osn.mghpcc.org',
    anonymous=True,
    force_path_style=True,
    region='us-east-1',
)
repo = ic.Repository.open(storage)
session = repo.readonly_session("main")

# Open DataTree (lazy loading)
dtree = xr.open_datatree(
    session.store,
    zarr_format=3,
    consolidated=False,
    chunks={},
    engine="zarr",
)
```

## Key Files

- `notebooks/NEXRAD-KLOT-Demo.ipynb`: Main tutorial notebook demonstrating data access and QVP computation
- `notebooks/QVP-Workflow-Comparison.ipynb`: Compares ARCO vs traditional file-based workflows
- `notebooks/demo_functions.py`: Helper functions for QVP computation, visualization, and data utilities
- `environment.yml`: Conda environment specification
- `pyproject.toml`: Python package configuration (for uv/pip installation)

## Helper Functions (demo_functions.py)

Key utilities in `notebooks/demo_functions.py`:
- `compute_qvp(ds, var)`: Computes Quasi-Vertical Profiles via azimuthal averaging
- `rain_depth(z, a, b, t)`: Estimates rainfall depth using Z-R relationships (Marshall-Palmer)
- `ryzhkov_figure(...)`: Creates 2x2 polarimetric variable visualization (Z, ZDR, RhoHV, PhiDP)
- `get_repo_config()`: Returns Icechunk repository configuration with manifest splitting
- `list_nexrad_files(...)`: Lists NEXRAD files from AWS S3 by date/radar/time
- `nexrad_donwload(s3filepath)`: Downloads and parses NEXRAD data from S3

## CI/CD

GitHub Actions workflow (`.github/workflows/render-notebooks.yml`):
- Executes notebooks on push/PR to `main`
- Converts notebooks to HTML
- Deploys to GitHub Pages (main branch only)
- Caches NEXRAD data at `~/.cache/fsspec`

## Reference Paper

Ladino-Rincón & Nesbitt (2025). Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives. arXiv:2510.24943

## License

Apache License 2.0
