# Radar DataTree

A framework for working with hierarchical radar data using [xarray-datatree](https://xarray-datatree.readthedocs.io/), enabling efficient access and analysis of weather radar data stored in cloud-optimized formats.

## Overview

This repository provides examples and documentation for working with radar data stored in Zarr format using the DataTree structure. The hierarchical organization allows for efficient storage and retrieval of multi-sweep radar data while maintaining the relationships between different radar scans.

### Key Features

- **Hierarchical Data Structure**: Organize radar sweeps in a tree structure that mirrors the natural organization of radar volumes
- **Cloud-Optimized**: Data stored in Zarr format enables efficient partial reads and parallel access
- **Xarray Integration**: Full compatibility with the xarray ecosystem for analysis and visualization
- **Lazy Loading**: Only load the data you need, when you need it

## Installation

### Using conda

```bash
conda create -n radar-datatree python=3.11
conda activate radar-datatree
conda install -c conda-forge xarray zarr xarray-datatree matplotlib cartopy
```

### Using uv

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install xarray zarr datatree matplotlib cartopy
```

### Using pip

```bash
pip install xarray zarr datatree matplotlib cartopy
```

## Quick Start

```python
import xarray as xr
from datatree import open_datatree

# Open a radar datatree from Zarr store
dt = open_datatree("path/to/radar_data.zarr")

# Explore the structure
print(dt)

# Access a specific sweep
sweep_0 = dt["sweep_0"]

# Plot reflectivity
sweep_0["DBZ"].plot()
```

## Data Structure

The radar data is organized in a hierarchical tree structure:

```
/
├── attrs: {radar metadata}
├── sweep_0/
│   ├── attrs: {sweep metadata}
│   ├── DBZ (azimuth, range)
│   ├── VEL (azimuth, range)
│   └── ...
├── sweep_1/
│   └── ...
└── sweep_N/
    └── ...
```

## Examples

See the [`examples/`](examples/) directory for Jupyter notebooks demonstrating:

- Reading and exploring radar datatrees
- Visualizing radar data with matplotlib and cartopy
- Working with multiple sweeps
- Extracting cross-sections and profiles

## Scientific Background

For a detailed description of the data structure and methodology, please refer to our preprint:

> [Paper Title - arXiv preprint]
>
> *Link: https://arxiv.org/abs/XXXX.XXXXX*

<!-- TODO: Update with actual arXiv link -->

## Data Conversion

The radar data shown in these examples was converted from raw radar formats (NEXRAD Level II, ODIM H5, etc.) using the `raw2zarr` conversion tool.

**Note**: The `raw2zarr` package is currently under licensing review by the University of Illinois at Urbana-Champaign Office of Technology Management. If you are interested in converting your own radar data to this format, please contact us directly.

### Contact for Data Conversion

<!-- TODO: Update with contact information -->
- **Email**: [your.email@institution.edu]
- **GitHub Issues**: Feel free to open an issue in this repository

## Related Projects

- [xarray](https://xarray.pydata.org/) - N-D labeled arrays and datasets in Python
- [xarray-datatree](https://xarray-datatree.readthedocs.io/) - Hierarchical data structures for xarray
- [Zarr](https://zarr.readthedocs.io/) - Chunked, compressed, N-dimensional arrays
- [Py-ART](https://arm-doe.github.io/pyart/) - Python ARM Radar Toolkit
- [wradlib](https://docs.wradlib.org/) - Open Source Library for Weather Radar Data Processing

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this work in your research, please cite:

```bibtex
@article{radar_datatree_2024,
  title={Title of Paper},
  author={Author Names},
  journal={arXiv preprint arXiv:XXXX.XXXXX},
  year={2024}
}
```

<!-- TODO: Update citation with actual paper details -->

## Acknowledgments

This work was supported by [funding sources/institutions].
