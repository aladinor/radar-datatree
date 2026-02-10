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

This is a documentation-focused repository. The actual library code under `src/radar_datatree/` is minimal — the core utilities live in `notebooks/demo_functions.py`, and the primary content is three progressive Jupyter notebook tutorials built with Sphinx + MyST-NB.

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

### Linting and Formatting

CI runs all three checks — they must all pass:

```bash
ruff check .          # Linting (rules: E, W, F, I, B, UP; ignores E501; allows E402 in notebooks)
ruff format .         # Ruff formatting
black notebooks/      # Black formatting (notebooks directory)
ruff check --fix .    # Auto-fix linting issues
```

Pre-commit hooks (`.pre-commit-config.yaml`) run trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files (max 1000KB), black, and ruff on commit.

### Building Documentation

```bash
sphinx-build -b html docs _build/html
```

Sphinx uses `myst_nb` in `cache` execution mode with a 40-second per-cell timeout. Notebooks are re-executed only when code changes.

## Pinned / Custom Dependencies

- **xarray**: Uses a custom async fork (`git+https://github.com/aladinor/xarray.git@async-dtreec`), not the official release
- **icechunk**: Pinned to a specific commit (`d11af22`) from git
- **zarr**: `>=3.1.2`
- **s3fs**: `>=2025.5.1`
- **uv**: Uses `unsafe-best-match` index strategy with `scientific-python-nightly-wheels` as extra index

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

- `notebooks/1.NEXRAD-KLOT-Demo.ipynb`: Beginner tutorial — data access and polarimetric visualization
- `notebooks/2.QVP-Workflow-Comparison.ipynb`: Intermediate — QVP reproduction, ARCO vs file-based performance comparison
- `notebooks/3.QPE-Snow-Storm.ipynb`: Advanced — snow accumulation estimation using Z-R relationships
- `notebooks/demo_functions.py`: All helper functions (QVP, rainfall, visualization, data access)
- `docs/conf.py`: Sphinx configuration (myst_nb, sphinx_book_theme)

## Helper Functions (demo_functions.py)

Key utilities in `notebooks/demo_functions.py`:
- `compute_qvp(ds, var)`: Quasi-Vertical Profiles via azimuthal averaging (handles dBZ log/linear conversion)
- `rain_depth(z, a, b, t)`: Rainfall/snowfall depth using Z-R relationships (Marshall-Palmer rain: a=200,b=1.6; Sekhon-Srivastava snow: a=1780,b=2.21)
- `ryzhkov_figure(...)`: 2x2 polarimetric variable contourf visualization (Z, ZDR, RhoHV, PhiDP)
- `concat_sweep_across_vcps(dtree, sweep_name, ...)`: Concatenates a specific sweep across all VCP-* nodes along vcp_time dimension
- `get_repo_config()`: Icechunk repository configuration with manifest splitting
- `list_nexrad_files(...)`: Lists NEXRAD Level II files from AWS S3 by date/radar/time range
- `nexrad_donwload(s3filepath)`: Downloads and parses NEXRAD data from S3 (note: typo in function name is intentional — do not rename)
- `nexrad_download_with_size(filepath)`: Download with file size tracking, returns (datatree, size_bytes)
- `list_nexrad_files_with_sizes(...)`: List files with size and time metadata

## CI/CD

GitHub Actions workflow (`.github/workflows/render-notebooks.yml`):
- Triggers on push/PR to `main` when notebooks/, docs/, images/, or workflow files change
- Runs linting (ruff check, ruff format --check, black --check) before building
- Builds documentation with Sphinx (`sphinx-build -b html docs _build/html`)
- Deploys to GitHub Pages (main branch only)
- Uses uv with Python 3.12 and caches .venv
- 15-minute job timeout

There is no formal test suite — notebook execution via Sphinx serves as integration testing.

### Branch Protection

The `main` branch has protection rules enabled:
- **Pull requests required** — no direct pushes to main
- **1 approving review** required before merging
- **Stale reviews dismissed** — re-review needed after new commits
- **Enforce admins** — rules apply to org owners too
- **Force pushes and branch deletion blocked**

All changes must go through a feature branch and PR workflow.

## Reference Paper

Ladino-Rincón & Nesbitt (2025). Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives. arXiv:2510.24943

## License

Apache License 2.0
