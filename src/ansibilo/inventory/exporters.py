import collections
import itertools
import json

import graphviz


ANSIBLE_INVENTORY_TAG = '-:ansible-inventory:-'
DEFAULT_DATA_CENTER_PREFIX = 'dc_'


def _colors(foreground, background):
    return {
        'color': background,
        'fontcolor': foreground,
        'fillcolor': background,
        'style': 'filled',
    }


def export_to_dot(host_groups, data_center_prefix=DEFAULT_DATA_CENTER_PREFIX):
    data_center_colors = _colors('white', '#238b45')
    host_colors = _colors('black', '#66c2a4')
    role_colors = _colors('black', '#b2e2e2')

    labels = set(itertools.chain(*host_groups.values()))
    data_centers = {label for label in labels if label.startswith(data_center_prefix)}
    roles = labels - data_centers

    graph = graphviz.Graph()
    graph.attr('graph', overlap='false', layout='neato', comment=ANSIBLE_INVENTORY_TAG)

    for data_center in sorted(data_centers):
        graph.node(data_center, **data_center_colors)

    for role in sorted(roles):
        graph.node(role, **role_colors)

    for fqdn, labels in host_groups.items():
        host = fqdn.split('.')[0]
        graph.node(host, **host_colors)
        for label in labels:
            color = data_center_colors if label in data_centers else role_colors
            graph.edge(host, label, color=color['color'])

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
