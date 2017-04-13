# -*- coding: utf-8 -*-
import pkg_resources
import sphinx_rtd_theme


project = u'ansibilo'
copyright = u'2017, Polyconseil'

version = pkg_resources.get_distribution('ansibilo').version
release = version

templates_path = []
source_suffix = '.rst'
master_doc = 'index'

pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = []
