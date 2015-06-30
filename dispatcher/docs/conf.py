import os
import sys

sys.path.insert(0, os.path.abspath('../../'))

# Activate desired extensions.
extensions = [
    'sphinxcontrib.programoutput',
    'sphinxcontrib.ansi',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo', 
    'sphinx.ext.viewcode', 
    'sphinx.ext.graphviz',
    'sphinx.ext.autosummary',
	]

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'Orchestrator REST API'
copyright = '2013, CRS4'
author = 'Carlo Impagliazzo'
version = '0.2'
release = '0.2.2'
html_title = '%s (%s)' % (project, release)
html_short_title = 'Orchestrator API'

# Choose a slightly better theme than default.
#html_theme = 'sphinxdoc'
#html_theme = 'default'
html_theme = 'haiku'
templates_path = ['_templates']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

html_logo = "logo/CRS4-colori-small.png"
html_favicon = "favicon.ico"

# Don't show links to the reST source.
html_show_sourcelink = False

# Disable index on the html page.
html_use_index = False

# Capture ansi colour in programoutput.
# See http://packages.python.org/sphinxcontrib-programoutput
programoutput_use_ansi = True

# Enable ansi plugin.
# See http://packages.python.org/sphinxcontrib-ansi
html_ansi_stylesheet = 'black-on-white.css'


autosummary_generate = True


