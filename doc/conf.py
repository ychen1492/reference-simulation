import os
import sys

sys.path.insert(0, os.path.abspath('..'))
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Geothermal Reference Simulation'
copyright = '2023, Yuan Chen'
author = 'Yuan Chen'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser', 
    'sphinxcontrib.apidoc',
    'sphinx.ext.autodoc', 
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon' 
    ]

apidoc_module_dir = '../src'
apidoc_output_dir = '_api/'
autodoc_mock_imports = ["darts",
                        "numpy",
                        "pandas",
                        "matplotlib",
                        "scipy",
                        "pykrige",
                        "gstools",
                        "skimage"]
source_suffix = ['.rst', '.md']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_title = 'Geothermal Reference Simulation'
html_static_path = ['_static']


