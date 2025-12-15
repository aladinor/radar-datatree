# Examples

This directory contains Jupyter notebooks demonstrating how to work with radar data stored in the DataTree format.

## Notebooks

| Notebook | Description |
|----------|-------------|
| [01_getting_started.ipynb](01_getting_started.ipynb) | Introduction to opening and exploring radar datatrees |
| [02_visualization.ipynb](02_visualization.ipynb) | Visualizing radar data with matplotlib and cartopy |
| [03_multi_sweep_analysis.ipynb](03_multi_sweep_analysis.ipynb) | Working with multiple sweeps in a volume |

## Prerequisites

Make sure you have installed the required dependencies:

```bash
# Using conda
conda env create -f ../environment.yml
conda activate radar-datatree

# Or using uv
uv pip install -e "..[all]"
```

## Data Access

The example data used in these notebooks is available from cloud storage. Each notebook includes instructions for accessing the relevant data.

## Running the Notebooks

```bash
jupyter lab
```

Then navigate to the `examples/` directory and open the notebooks.
