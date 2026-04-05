import os
import sys

cwd = os.getcwd()
project_root = os.path.dirname(cwd)

sys.path.insert(0, project_root)

import gxformat2 as project_module  # noqa: E402

# -- General configuration ---------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "_ext"))
extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinxarg.ext",
    "sphinx_design",
    "sphinxcontrib.mermaid",
    "examples_catalog",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}

templates_path = ["_templates"]
source_suffix = [".rst", ".md"]
master_doc = "index"

project = "Galaxy Workflow Format 2"
copyright = "2015-2026, Galaxy Project and Community"

version = project_module.__version__
release = project_module.__version__

exclude_patterns = ["_build"]

pygments_style = "default"

# -- Options for HTML output -------------------------------------------

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "logo": {
        "text": "gxformat2",
    },
    "header_links_before_dropdown": 6,
    "pygment_light_style": "default",
    "navbar_align": "left",
    "show_prev_next": True,
    "footer_start": ["copyright"],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/galaxyproject/gxformat2",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "Galaxy Project",
            "url": "https://galaxyproject.org",
            "icon": "fa-solid fa-globe",
        },
    ],
    "secondary_sidebar_items": ["page-toc", "sourcelink"],
    "navigation_with_keys": True,
}

html_static_path = ["_static"]
html_css_files = ["css/galaxy.css"]
html_title = "gxformat2"
html_short_title = "gxformat2"

htmlhelp_basename = "gxformat2doc"

# -- Options for LaTeX output ------------------------------------------

latex_elements = {}

latex_documents = [
    ("index", "gxformat2.tex", "Galaxy Workflow Format 2 Documentation", "Galaxy Project and Community", "manual"),
]

# -- Options for manual page output ------------------------------------

man_pages = [("index", "gxformat2", "Galaxy Workflow Format 2 Documentation", ["Galaxy Project and Community"], 1)]

# -- Options for Texinfo output ----------------------------------------

texinfo_documents = [
    (
        "index",
        "gxformat2",
        "Galaxy Workflow Format 2 Documentation",
        "Galaxy Project and Community",
        "gxformat2",
        "Galaxy Workflow Format 2 descriptions.",
        "Miscellaneous",
    ),
]
