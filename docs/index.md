# Radar DataTree

**A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives**

```{image} ../images/radar_datatree.png
:alt: Radar DataTree Architecture
:width: 800px
:align: center
```

## Overview

**Radar DataTree** transforms fragmented weather radar archives into **FAIR-compliant, cloud-optimized datasets**. It extends the WMO FM-301/CfRadial 2.1 standard from individual radar volume scans to **time-resolved, analysis-ready archives**.

### The Problem

Weather radar data is among the most scientifically valuable yet structurally underutilized Earth observation datasets:

- Archives contain **millions of standalone binary files** in proprietary formats
- **No temporal indexing** — each scan must be parsed independently
- **Hours to days** required for multi-week analyses
- Fundamentally **misaligned with FAIR data principles**

### The Solution

Radar DataTree provides a **dataset-level abstraction** that aggregates individual radar files into a **single hierarchical dataset** for seamless time-series analysis and scalable cloud storage.

## Performance

| Metric | Traditional Workflow | Radar DataTree | Speedup |
|--------|---------------------|----------------|---------|
| **Load 92 GB metadata** | Minutes | **~1.5 seconds** | ~100x |
| **QVP generation (1 week)** | Hours | **Seconds** | **100x+** |
| **QPE accumulation (5 days)** | 30-60 minutes | **~12 seconds** | **70-150x** |

## Technology Stack

| Component | Role |
|-----------|------|
| **FM-301/CfRadial 2.1** | WMO standard for radar volumes and sweeps |
| **xarray.DataTree** | Hierarchical in-memory data representation |
| **Zarr** | Chunked, compressed, cloud-native storage |
| **Icechunk** | ACID-compliant transactional storage with version control |

## Quick Start

```python
import xarray as xr
import icechunk as ic

# Connect to NEXRAD KLOT on Open Storage Network
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

# Open 92 GB archive in ~1.5 seconds (lazy loading)
dtree = xr.open_datatree(
    session.store,
    zarr_format=3,
    consolidated=False,
    chunks={},
    engine="zarr",
)

# Plot reflectivity
dtree["VCP-34/sweep_0"].DBZH.sel(
    vcp_time="2025-12-13 15:36", method="nearest"
).plot(x="x", y="y", cmap="ChaseSpectral", vmin=-10, vmax=70)
```

## Example Notebooks

Explore the full capabilities through these interactive tutorials:

```{toctree}
:maxdepth: 1

NEXRAD-KLOT-Demo
QVP-Workflow-Comparison
```

## Citation

If you use this framework, please cite:

> **Ladino-Rincón, A., & Nesbitt, S. W. (2025).** Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives. *arXiv preprint arXiv:2510.24943 [cs.DC]*. https://doi.org/10.48550/arXiv.2510.24943

## Links

- [GitHub Repository](https://github.com/aladinor/radar-datatree)
- [Paper: arXiv:2510.24943](https://doi.org/10.48550/arXiv.2510.24943)
- [xarray](https://xarray.dev) | [xradar](https://xradar.dev) | [Zarr](https://zarr.dev) | [Icechunk](https://icechunk.io)
