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
            dc_One [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
            dc_Two [color="#238b45" fillcolor="#238b45" fontcolor=white style=filled]
            OneHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            ThreeHostGroup [color="#b2e2e2" fillcolor="#b2e2e2" fontcolor=black style=filled]
            hostOne [color="#66c2a4" fillcolor="#66c2a4" fontcolor=black style=filled]
            hostOne -- OneHostGroup [color="#b2e2e2"]
            hostOne -- ThreeHostGroup [color="#b2e2e2"]
            hostOne -- dc_One [color="#238b45"]
            hostTwo [color="#66c2a4" fillcolor="#66c2a4" fontcolor=black style=filled]
            hostTwo -- ThreeHostGroup [color="#b2e2e2"]
            hostTwo -- dc_One [color="#238b45"]
            hostThree [color="#66c2a4" fillcolor="#66c2a4" fontcolor=black style=filled]
            hostThree -- ThreeHostGroup [color="#b2e2e2"]
            hostThree -- dc_Two [color="#238b45"]
        }
    """
    exported = exporters.export_to_dot(get_host_group())
    assert dot_lines(str(exported)) == dot_lines(expected)


def test_export_to_json():
    expected = {
        "hostOne": ["OneHostGroup", "ThreeHostGroup", "dc_One"],
        "hostTwo": ["ThreeHostGroup", "dc_One"],
        "hostThree": ["ThreeHostGroup", "dc_Two"],
    }
    exported = exporters.export_to_json(get_host_group())
    assert json.loads(exported) == expected


def test_export_to_ansible_json():
    expected = {
        "OneHostGroup": ["hostOne"],
        "ThreeHostGroup": ["hostOne", "hostThree", "hostTwo"],
        "dc_One": ["hostOne", "hostTwo"],
        "dc_Two": ["hostThree"],
    }
    exported_raw = exporters.export_to_ansible_json(get_host_group())
    exported = {key: sorted(value) for key, value in json.loads(exported_raw).items()}
    assert exported == expected
