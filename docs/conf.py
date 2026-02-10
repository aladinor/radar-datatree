# Sphinx configuration for Radar DataTree documentation
import os
import sys

# Add notebooks directory to path
sys.path.insert(0, os.path.abspath("../notebooks"))

project = "Radar DataTree"
author = "Alfonso Ladino-Rincón"
copyright = "2025, Alfonso Ladino-Rincón"

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_design",
    "sphinx_copybutton",
]

# MyST-NB settings
nb_execution_mode = (
    "cache"  # Execute and cache results; re-execute only when code changes
)
nb_execution_timeout = 40  # seconds per cell
myst_enable_extensions = [
    "attrs_block",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

# Theme
html_theme = "sphinx_book_theme"
html_theme_options = {
    "repository_url": "https://github.com/AtmoScale/radar-datatree",
    "use_repository_button": True,
    "use_download_button": True,
    "show_toc_level": 2,
}

# Source settings
source_suffix = {
    ".rst": "restructuredtext",
    ".ipynb": "myst-nb",
    ".md": "myst-nb",
}

# Exclude patterns
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "QVP-Workflow-Benchmark.ipynb",  # Benchmark notebook for paper, not rendered in docs
]

# Suppress warnings for notebooks with no outputs
suppress_warnings = ["myst.header"]
