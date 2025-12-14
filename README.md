# Radar DataTree

[![DOI](https://zenodo.org/badge/658848435.svg)](https://zenodo.org/doi/10.5281/zenodo.10069535)

A FAIR and cloud-native framework for working with hierarchical weather radar data using [xarray.DataTree](https://docs.xarray.dev/en/stable/user-guide/hierarchical-data.html), enabling scalable access and analysis of radar archives stored in cloud-optimized formats.

## Cite This Work

This repository demonstrates the **Radar DataTree** framework described in:

> **Ladino-Rincón, A., & Nesbitt, S. W. (2025).** *Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives.* arXiv:2510.24943 [cs.DC]
>
> https://doi.org/10.48550/arXiv.2510.24943

## Motivation

Weather radar data are among the most scientifically valuable yet structurally underutilized Earth observation datasets. Despite widespread public availability, operational radar archives remain **fragmented, vendor-specific, and poorly aligned with FAIR principles** (Findable, Accessible, Interoperable, Reusable).

**Radar DataTree** addresses these limitations by transforming operational radar archives into FAIR-compliant, cloud-optimized datasets. This framework extends the WMO [FM-301/CfRadial 2.1](https://community.wmo.int/en/activity-areas/wis/wmo-cf-extensions) standard from individual radar volume scans to **time-resolved, analysis-ready archives**.

### Key Features

- **Dataset-level organization**: Entire radar archives as structured, time-indexed collections
- **Cloud-native access**: Zarr serialization optimized for parallel I/O and lazy evaluation
- **Metadata preservation**: Full FM-301/CF compliance with sweep-level detail
- **Concurrent-safe writes**: Icechunk transactions enable real-time ingestion without data corruption
- **Scalable performance**: Demonstrated 100x+ speedups over traditional file-based workflows

## Core Architecture

| Component | Role |
|-----------|------|
| **FM-301/CfRadial 2.1** | File-level standard for radar volumes and sweeps |
| **xarray.DataTree** | Hierarchical in-memory representation of scan collections |
| **Zarr** | Chunked, compressed, cloud-native storage format |
| **Icechunk** | ACID-compliant transactional engine for versioned datasets |

## Installation

### Using conda

```bash
conda env create -f environment.yml
conda activate radar-datatree
```

Or manually:

```bash
conda create -n radar-datatree python=3.11
conda activate radar-datatree
conda install -c conda-forge xarray zarr xarray-datatree matplotlib cartopy arm_pyart
```

### Using uv

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install xarray zarr xarray-datatree matplotlib cartopy
```

## Quick Start

```python
import xarray as xr

# Open a radar datatree from Zarr store
dt = xr.open_datatree("s3://bucket/path/to/radar.zarr", engine="zarr")

# Explore the structure
print(dt)

# Access a specific sweep
sweep_0 = dt["sweep_0"]

# Plot reflectivity
sweep_0["DBZ"].plot()
```

## Data Structure

The radar data is organized in a hierarchical tree structure following FM-301/CfRadial 2.1:

```
/
├── attrs: {radar metadata, instrument_name, latitude, longitude, ...}
├── sweep_0/
│   ├── attrs: {elevation, sweep_number, sweep_mode, ...}
│   ├── DBZ (azimuth, range)      # Reflectivity
│   ├── VEL (azimuth, range)      # Radial velocity
│   ├── ZDR (azimuth, range)      # Differential reflectivity
│   └── ...
├── sweep_1/
│   └── ...
└── sweep_N/
    └── ...
```

## Examples & Demo Notebooks

See the [`examples/`](examples/) directory for Jupyter notebooks demonstrating:

- Reading and exploring radar datatrees
- Visualizing radar data with matplotlib and cartopy
- Working with multiple sweeps
- Extracting time series and profiles

### Interactive Demos

Explore interactive examples at the **[Radar DataTree Demo Repository](https://github.com/earth-mover/radar-data-demo)**:

- QVP (Quasi-Vertical Profile) computation from cloud-hosted archives
- QPE (Quantitative Precipitation Estimation) accumulation workflows
- Time-series extraction and analysis

## Demonstrated Performance

Case studies on operational NEXRAD archives show:

- **100x+ speedup** for Quasi-Vertical Profile (QVP) generation
- **70-150x speedup** for Quantitative Precipitation Estimation (QPE)
- Sub-minute retrieval of multi-week time series from cloud storage

## Supported Formats

The Radar DataTree framework supports conversion from:

- NEXRAD Level II (including dynamic scans: SAILS, MRLE, AVSET)
- SIGMET/IRIS
- ODIM_H5

## Data Conversion

The radar data shown in these examples was converted from raw radar formats using the `raw2zarr` conversion tool.

**Note**: The `raw2zarr` package is currently under licensing review by the University of Illinois at Urbana-Champaign Office of Technology Management. If you are interested in converting your own radar data to this format, please contact us directly.

### Contact for Data Conversion

- **GitHub**: [@aladinor](https://github.com/aladinor)
- **Issues**: Feel free to open an issue in this repository

## Related Projects

- [xarray](https://xarray.pydata.org/) - N-D labeled arrays and datasets in Python
- [xarray.DataTree](https://docs.xarray.dev/en/stable/user-guide/hierarchical-data.html) - Hierarchical data structures for xarray
- [Zarr](https://zarr.readthedocs.io/) - Chunked, compressed, N-dimensional arrays
- [Icechunk](https://icechunk.io/) - Transactional storage engine for Zarr
- [Xradar](https://docs.openradarscience.org/projects/xradar/) - Xarray-based radar data I/O
- [Py-ART](https://arm-doe.github.io/pyart/) - Python ARM Radar Toolkit
- [wradlib](https://docs.wradlib.org/) - Open Source Library for Weather Radar Data Processing

## Authors

- [Alfonso Ladino-Rincón](https://github.com/aladinor)
- [Max Grover](https://github.com/mgrover1)

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@article{ladino2025radardatatree,
  title={Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives},
  author={Ladino-Rinc{\'o}n, Alfonso and Nesbitt, Stephen W.},
  journal={arXiv preprint arXiv:2510.24943},
  year={2025},
  doi={10.48550/arXiv.2510.24943}
}
```

## References

- Ladino-Rincón, A., & Nesbitt, S. W. (2025). Radar DataTree: A FAIR and Cloud-Native Framework for Scalable Weather Radar Archives. *arXiv preprint arXiv:2510.24943 [cs.DC]*. https://doi.org/10.48550/arXiv.2510.24943

- Abernathey, R. P., et al. (2021). Cloud-Native Repositories for Big Scientific Data. *Computing in Science & Engineering*, 23(2), 26-35. doi:10.1109/MCSE.2021.3059437
