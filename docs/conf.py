# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import datetime
import os
import sys
from importlib.metadata import distribution


year = datetime.datetime.now().year
sys.path.append(os.path.abspath('../src'))
rqmt = distribution('Products.LDAPUserFolder')

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Products.LDAPUserFolder'
copyright = f'2000-{year}, Jens Vagelpohl and Contributors'
author = 'Jens Vagelpohl'

# The short X.Y version.
version = '%s.%s' % tuple(map(int, rqmt.version.split('.')[:2]))
# The full version, including alpha/beta/rc tags.
release = rqmt.version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'repoze.sphinx.autointerface']
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'en'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
