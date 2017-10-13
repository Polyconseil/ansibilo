import json
import os.path

from ansibilo.inventory import exporters
from ansibilo.inventory import utils


def get_host_group():
    inventory_file = os.path.join(
        os.path.dirname(__file__),
        'resources/hosts.ini',
    )
    return utils.get_host_groups(inventory_file)


def dot_lines(dot):
    return sorted([
        line.strip()
        for line in dot.strip().splitlines()[1:-1]
        if line.strip()
    ])


def test_export_to_dot():
    expected = """
        graph {
            graph [comment="-:ansible-inventory:-" layout=neato overlap=false]
            hostOne [color="#66c2a4" fillcolor="#66c2a4" fontcolor=black style=filled]
            OneHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            hostOne -- OneHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            ThreeHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            hostOne -- ThreeHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            "dc-One" [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
            "dc-One" -- hostOne [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
            hostTwo [color="#66c2a4" fillcolor="#66c2a4" fontcolor=black style=filled]
            ThreeHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            hostTwo -- ThreeHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            "dc-One" [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
            "dc-One" -- hostTwo [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
            hostThree [color="#66c2a4" fillcolor="#66c2a4" fontcolor=black style=filled]
            ThreeHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            hostThree -- ThreeHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            "dc-Two" [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
            "dc-Two" -- hostThree [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
        }
    """
    exported = exporters.export_to_dot(get_host_group(), data_center_prefix='dc-')
    assert dot_lines(str(exported)) == dot_lines(expected)


def test_export_to_json():
    expected = {
        "hostOne": ["OneHostGroup", "ThreeHostGroup", "dc-One"],
        "hostTwo": ["ThreeHostGroup", "dc-One"],
        "hostThree": ["ThreeHostGroup", "dc-Two"],
    }
    exported = exporters.export_to_json(get_host_group(), data_center_prefix='dc-')
    assert json.loads(exported) == expected


def test_export_to_ansible_json():
    expected = {
        "OneHostGroup": ["hostOne"],
        "ThreeHostGroup": ["hostOne", "hostThree", "hostTwo"],
        "dc-One": ["hostOne", "hostTwo"],
        "dc-Two": ["hostThree"],
    }
    exported_raw = exporters.export_to_ansible_json(get_host_group(), data_center_prefix='dc-')
    exported = {key: sorted(value) for key, value in json.loads(exported_raw).items()}
    assert exported == expected
