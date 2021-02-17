import functools
import xml.dom
import xml.dom.minidom as dom

import sphinx.ext.graphviz as sphinx_graphviz


from .inventory import exporters
from .inventory import utils


class AnsibleInventoryGraphDirective(sphinx_graphviz.Graphviz):
    def run(self):
        self.content = exporters.export_to_dot(utils.get_host_groups())
        return super(AnsibleInventoryGraphDirective, self).run()


def render_dot_decorator(fct):
    @functools.wraps(fct)
    def inner(self, code, options, output_format, prefix, filename=None):
        # sphinx version 3.5.1 added a new parameter filename
        # this condition try to make this patched function retrocompatible
        if filename is not None:
            rel_filename, out_filename = fct(self, code, options, output_format, prefix, filename)
        else:
            rel_filename, out_filename = fct(self, code, options, output_format, prefix)

        if output_format == 'svg' and exporters.ANSIBLE_INVENTORY_TAG in code:
            # Drop svg width and height so the svg will fit in the content block
            tree = dom.parse(out_filename)
            root = tree.getElementsByTagName('svg')[0]
            for attribute in ('width', 'height'):
                try:
                    root.removeAttribute(attribute)
                except xml.dom.NotFoundErr:
                    pass
            with open(out_filename, 'w') as fp:
                fp.write(tree.toxml())
        return rel_filename, out_filename
    return inner


def setup(app):
    app.add_directive('ansible-inventory-graph', AnsibleInventoryGraphDirective)
    sphinx_graphviz.render_dot = render_dot_decorator(sphinx_graphviz.render_dot)
