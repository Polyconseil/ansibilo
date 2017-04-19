import collections
import json

import graphviz


ANSIBLE_INVENTORY_TAG = '-:ansible-inventory:-'


def _colors(foreground, background):
    return {
        'color': background,
        'fontcolor': foreground,
        'fillcolor': background,
        'style': 'filled',
    }


def export_to_dot(host_groups, data_center_prefix='dc-'):
    dc_colors = _colors('white', '#238b45')
    host_colors = _colors('black', '#66c2a4')
    role_colors = _colors('black', '#b2e2e2')

    graph = graphviz.Graph()
    graph.attr('graph', overlap='false', layout='neato', comment=ANSIBLE_INVENTORY_TAG)
    for fqdn, labels in host_groups.items():
        host = fqdn.split('.')[0]
        graph.node(host, **host_colors)
        for label in labels:
            if label.startswith(data_center_prefix):
                graph.node(label, **dc_colors)
                graph.edge(label, host, **dc_colors)
            else:
                graph.node(label, **role_colors)
                graph.edge(host, label, **role_colors)

    return graph


def export_to_json(host_groups, data_center_prefix=None):
    return json.dumps(host_groups, indent=True)


def export_to_ansible_json(host_groups, data_center_prefix=None):
    groups = collections.defaultdict(list)
    for host, group_list in host_groups.items():
        for group in group_list:
            groups[group].append(host)
    return json.dumps(groups, indent=True)


def export_to_svg(*args, **kwargs):
    graph = export_to_dot(*args, **kwargs)
    graph.format = 'svg'
    return graph.pipe().decode('utf-8')


FORMAT_EXPORTERS = {
    'ansible-json': export_to_ansible_json,
    'dot': export_to_dot,
    'json': export_to_json,
    'svg': export_to_svg,
}
