<h1 align="center">Radar DataTree</h1>

<p align="center">
  <strong>A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License"></a>
  <a href="https://doi.org/10.48550/arXiv.2510.24943"><img src="https://img.shields.io/badge/arXiv-2510.24943-b31b1b.svg" alt="arXiv"></a>
  <a href="https://aladinor.github.io/radar-datatree/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue" alt="Documentation"></a>
  <a href="https://github.com/aladinor/radar-datatree/actions"><img src="https://github.com/aladinor/radar-datatree/actions/workflows/render-notebooks.yml/badge.svg" alt="CI"></a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-documentation">Documentation</a> •
  <a href="#-performance">Performance</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-citation">Citation</a>
</p>

---

## Overview

**Radar DataTree** transforms fragmented weather radar archives into **FAIR-compliant, cloud-optimized datasets**. It extends the WMO FM-301/CfRadial 2.1 standard from individual radar volume scans to **time-resolved, analysis-ready archives** that can be accessed and analyzed at scale.

This repository provides **examples and tutorials** demonstrating how to access and analyze weather radar data stored in the Radar DataTree format.

### The Problem

Weather radar data is among the most scientifically valuable yet structurally underutilized Earth observation datasets:

- Archives contain **millions of standalone binary files** in proprietary formats
- **No temporal indexing** — each scan must be parsed independently
- **Hours to days** required for multi-week analyses
- Fundamentally **misaligned with FAIR data principles**

### The Solution

Radar DataTree provides a **dataset-level abstraction** that aggregates individual radar files into a **single hierarchical dataset** for seamless time-series analysis and scalable cloud storage—while preserving each VCP's unique structure.

<p align="center">
  <img src="images/radar_datatree.png" alt="Radar DataTree Architecture" width="800"/>
</p>

**Data Structure:**

```
/
├── VCP-34/           # Clear-air Volume Coverage Pattern
│   ├── sweep_0/      # Lowest elevation (0.5°)
│   │   ├── DBZH      # Reflectivity
│   │   ├── ZDR       # Differential reflectivity
│   │   ├── RHOHV     # Cross-correlation coefficient
│   │   └── PHIDP     # Differential phase
│   ├── sweep_1/
│   └── ...
├── VCP-212/          # Precipitation mode
│   └── ...
└── ...
```

---

## Performance

| Metric | Traditional Workflow | Radar DataTree | Speedup |
|--------|---------------------|----------------|---------|
| **Load 92 GB metadata** | Minutes | **~1.5 seconds** | ~100x |
| **QVP generation (1 week)** | Hours | **Seconds** | **100x+** |
| **QPE accumulation (5 days)** | 30-60 minutes | **~12 seconds** | **70-150x** |

All benchmarks performed on commodity hardware (laptop with 4 cores, 12 threads).

---

## Technology Stack

| Component | Role |
|-----------|------|
| **FM-301/CfRadial 2.1** | WMO standard for radar volumes and sweeps |
| **xarray.DataTree** | Hierarchical in-memory data representation |
| **Zarr** | Chunked, compressed, cloud-native storage |
| **Icechunk** | ACID-compliant transactional storage with version control |

---

## Quick Start

### Connect to NEXRAD KLOT Data

NEXRAD data for KLOT (Chicago, IL) is available on the **Open Storage Network (OSN)** with anonymous access:

```python
import xarray as xr
import icechunk as ic

# Connect to cloud storage
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

# Open the entire archive (lazy loading - only metadata)
dtree = xr.open_datatree(
    session.store,
    zarr_format=3,
    consolidated=False,
    chunks={},
    engine="zarr",
)

# Explore: 92 GB of data, loaded in ~1.5 seconds!
print(f"Dataset size: {dtree.nbytes / 1024**3:.2f} GB")

# Plot reflectivity from a specific time
dtree["VCP-34/sweep_0"].DBZH.sel(
    vcp_time="2025-12-13 15:36",
    method="nearest"
).plot(x="x", y="y", cmap="ChaseSpectral", vmin=-10, vmax=70)
```

---

## Documentation

### Interactive Notebooks

Explore the full capabilities through our Jupyter notebooks:

| Notebook | Description |
|----------|-------------|
| [**NEXRAD KLOT Demo**](https://aladinor.github.io/radar-datatree/NEXRAD-KLOT-Demo.html) | Complete tutorial: data access, visualization, QVP computation, and QPE |
| [**Workflow Comparison**](https://aladinor.github.io/radar-datatree/QVP-Workflow-Comparison.html) | Side-by-side comparison of ARCO vs traditional file-based workflows |

### Run Locally

```bash
cd notebooks
jupyter lab
```

---

## Installation

### Using uv (recommended)

```bash
git clone https://github.com/aladinor/radar-datatree.git
cd radar-datatree
uv sync
```

### Using conda

```bash
git clone https://github.com/aladinor/radar-datatree.git
cd radar-datatree
conda env create -f environment.yml
conda activate radar-datatree
```

### Using pip

```bash
git clone https://github.com/aladinor/radar-datatree.git
cd radar-datatree
pip install -e ".[dev]"
```

---

## Available Data

### NEXRAD KLOT (Chicago, IL)

| Property | Value |
|----------|-------|
| **Bucket** | `nexrad-arco` |
| **Prefix** | `KLOT-RT` |
| **Endpoint** | `https://umn1.osn.mghpcc.org` |
| **Access** | Anonymous (no credentials) |
| **Size** | ~92 GB |
| **Time Range** | December 2025 (continuously updated) |

---

## Use Cases

### Quasi-Vertical Profiles (QVP)

QVPs summarize vertical trends in radar variables by azimuthally averaging data from constant-elevation sweeps. Essential for:
- Storm microphysics analysis
- Melting layer detection
- Hydrometeor classification

### Quantitative Precipitation Estimation (QPE)

Compute precipitation accumulations over extended periods using reflectivity-derived rain rates:
- Multi-day accumulations in seconds
- Z-R relationship customization
- Real-time and retrospective analysis

### Time-Series Extraction

Extract radar data at fixed locations for:
- Sensor intercomparisons
- Validation studies
- Data assimilation workflows

---

## Citation

If you use this framework, please cite:

> **Ladino-Rincón, A., & Nesbitt, S. W. (2025).** Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives. *arXiv preprint arXiv:2510.24943 [cs.DC]*. https://doi.org/10.48550/arXiv.2510.24943

```bibtex
@article{ladino2025radardatatree,
  title={Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives},
  author={Ladino-Rinc{\'o}n, Alfonso and Nesbitt, Stephen W.},
  journal={arXiv preprint arXiv:2510.24943},
  year={2025},
  doi={10.48550/arXiv.2510.24943}
}
```

---

## Need to Convert Your Own Data?

The conversion tool (**Raw2Zarr**) transforms raw radar files (NEXRAD Level II, SIGMET/IRIS, ODIM_H5) into the ARCO format. Contact us for access:

**Alfonso Ladino-Rincón**
- GitHub: [@aladinor](https://github.com/aladinor)
- Email: alfonso8@illinois.edu

---

## Related Projects

| Project | Description |
|---------|-------------|
| [xarray](https://xarray.dev) | N-D labeled arrays and datasets |
| [xradar](https://xradar.dev) | Radar data I/O and analysis |
| [Zarr](https://zarr.dev) | Chunked, compressed N-dimensional arrays |
| [Icechunk](https://icechunk.io) | Transactional storage engine for Zarr |
| [Py-ART](https://arm-doe.github.io/pyart/) | Python ARM Radar Toolkit |

---

## Authors

- **[Alfonso Ladino-Rincón](https://github.com/aladinor)** — University of Illinois Urbana-Champaign
- **[Stephen Nesbitt](https://github.com/swnesbitt)** — University of Illinois Urbana-Champaign

---

## License

This project is licensed under the **Apache License 2.0** — see the [LICENSE](LICENSE) file for details.
