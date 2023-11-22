# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ZJB-Docs"
copyright = "2023, ZJB Group"
author = "ZJB Group"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_design",
    "myst_nb",
]

# https://myst-nb.readthedocs.io/en/latest/configuration.html
myst_enable_extensions = ["dollarmath", "colon_fence"]
myst_heading_anchors = 5
nb_execution_mode = "off"

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "zh_CN"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_book_theme"
html_static_path = ["_static"]
html_js_files = ["auto_logo.js"]

# https://sphinx-book-theme.readthedocs.io/en/stable/index.html
html_theme_options = {
    "repository_url": "https://github.com/ZJBGroup/ZJB-Docs",
    "use_source_button": True,
    "use_issues_button": True,
    "use_edit_page_button": True,
    "show_toc_level": 2,
    "logo": {
        "image_light": "logo_black.png",
        "image_dark": "logo_white.png",
    },
}
