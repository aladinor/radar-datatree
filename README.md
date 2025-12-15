<img src="images/radar_datatree.png" alt="Radar DataTree" width="550"/>

# Radar DataTree

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![DOI](https://zenodo.org/badge/658848435.svg)](https://zenodo.org/doi/10.5281/zenodo.10069535)

**Examples and tutorials for accessing Analysis-Ready Cloud-Optimized (ARCO) weather radar data.**

This repository demonstrates how to read and analyze weather radar data stored in the Radar DataTree format - a FAIR-compliant, cloud-native framework for scalable radar archives.

## Cite This Work

This repository showcases the **Radar DataTree** framework described in:

> **Ladino-Rincón & Nesbitt (2025)**
> *Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives*
> arXiv:2510.24943 [cs.DC] — https://doi.org/10.48550/arXiv.2510.24943

```bibtex
@article{ladino2025radardatatree,
  title={Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives},
  author={Ladino-Rinc{\'o}n, Alfonso and Nesbitt, Stephen W.},
  journal={arXiv preprint arXiv:2510.24943},
  year={2025},
  doi={10.48550/arXiv.2510.24943}
}
```

## What is Radar DataTree?

Radar DataTree transforms operational radar archives into FAIR-compliant, cloud-optimized datasets. It extends the WMO FM-301/CfRadial 2.1 standard from individual radar volume scans to **time-resolved, analysis-ready archives**.

### Key Benefits

| Traditional Approach                   | Radar DataTree                         |
|----------------------------------------|----------------------------------------|
| Download thousands of individual files | Stream directly from cloud storage     |
| Decompress and parse each file         | Data immediately accessible            |
| No temporal indexing                   | Time-indexed collections               |
| Sequential file-by-file processing     | Parallel I/O with lazy evaluation      |
| Hours/Days for multi-week analysis     | **Minutes** for multi-week analysis    |

### Performance Highlights

- **Sub-second metadata access**: Load metadata for ~92 GB of radar data in ~1.5 seconds
- **100x+ speedup** for Quasi-Vertical Profile (QVP) generation
- **70-150x speedup** for Quantitative Precipitation Estimation (QPE)

### Technology Stack

| Component               | Role                                                    |
|-------------------------|---------------------------------------------------------|
| **FM-301/CfRadial 2.1** | WMO standard for radar volumes and sweeps               |
| **xarray.DataTree**     | Hierarchical in-memory data representation              |
| **Zarr**                | Chunked, compressed, cloud-native storage               |
| **Icechunk**            | ACID-compliant transactional storage with version control |

## Available Data

### NEXRAD KLOT (Chicago, IL)

NEXRAD data for KLOT is available on the **Open Storage Network (OSN)**:

- **Bucket**: `nexrad-arco`
- **Prefix**: `KLOT-RT`
- **Endpoint**: `https://umn1.osn.mghpcc.org`
- **Access**: Anonymous (no credentials required)

```python
import icechunk as ic

storage = ic.s3_storage(
    bucket='nexrad-arco',
    prefix='KLOT-RT',
    endpoint_url='https://umn1.osn.mghpcc.org',
    anonymous=True,
    force_path_style=True,
    region='us-east-1',
)
repo = ic.Repository.open(storage)
```

## Installation

### Using conda (recommended)

```bash
git clone https://github.com/aladinor/radar-datatree.git
cd radar-datatree
conda env create -f environment.yml
conda activate radar-datatree
```

### Using uv

```bash
git clone https://github.com/aladinor/radar-datatree.git
cd radar-datatree
uv sync
```

## Quick Start

```python
import xarray as xr
import icechunk as ic

# Connect to KLOT data on OSN
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

# Open the DataTree (lazy loading - only metadata)
dtree = xr.open_datatree(
    session.store,
    zarr_format=3,
    consolidated=False,
    chunks={},
    engine="zarr",
)

# Explore the structure
print(f"Dataset size: {dtree.nbytes / 1024**3:.2f} GB")
dtree.prune()

# Plot reflectivity from the latest scan
dtree["VCP-34/sweep_0"].DBZH.isel(vcp_time=-1).plot(
    x="x", y="y", cmap="ChaseSpectral", vmin=-10, vmax=70
)
```

## Examples

### Notebooks

| Notebook | Description |
|----------|-------------|
| [NEXRAD-KLOT-Demo.ipynb](notebooks/NEXRAD-KLOT-Demo.ipynb) | Complete tutorial on accessing KLOT data, visualizing radar scans, and computing Quasi-Vertical Profiles |

### Running the Examples

```bash
cd notebooks
jupyter lab
```

Open `NEXRAD-KLOT-Demo.ipynb` to get started.

## Data Structure

Radar DataTree organizes data hierarchically by **Volume Coverage Pattern (VCP)** and **sweep**:

```
/
├── VCP-34/           # Clear-air mode
│   ├── sweep_0/      # Lowest elevation
│   ├── sweep_1/
│   └── ...
├── VCP-212/          # Precipitation mode
│   ├── sweep_0/
│   └── ...
...
```

Each sweep contains polarimetric variables:
- **DBZH**: Horizontal reflectivity (dBZ)
- **ZDR**: Differential reflectivity (dB)
- **RHOHV**: Cross-correlation coefficient
- **PHIDP**: Differential phase (degrees)
- **VELOCITY**: Radial velocity (m/s)

## Need to Convert Your Own Data?

If you need to convert radar data (NEXRAD, SIGMET/IRIS, ODIM_H5, RAW) to this ARCO format, please contact:

**Alfonso Ladino-Rincón**
- GitHub: [@aladinor](https://github.com/aladinor)
- Email: alfonso8@illinois.edu

## References

- **Ladino-Rincón, A., & Nesbitt, S. W. (2025).** Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives. *arXiv preprint arXiv:2510.24943 [cs.DC]*. https://doi.org/10.48550/arXiv.2510.24943

- Abernathey, R. P., et al. (2021). Cloud-Native Repositories for Big Scientific Data. *Computing in Science & Engineering*, 23(2), 26-35. doi:10.1109/MCSE.2021.3059437

## Related Projects

- [xarray](https://xarray.dev) - N-D labeled arrays and datasets
- [xradar](https://xradar.dev) - Radar data I/O and analysis
- [Zarr](https://zarr.dev) - Chunked, compressed N-dimensional arrays
- [Icechunk](https://icechunk.io) - Transactional storage engine for Zarr

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Authors

- [Alfonso Ladino-Rincón](https://github.com/aladinor) - University of Illinois Urbana-Champaign
- [Stephen Nesbitt](https://github.com/swnesbitt) - University of Illinois Urbana-Champaign
