from . import utils


def get_missing_modules(internal_package, ansible_package):
    return [
        plugin[1]  # FIXME: plugin.name in Python 3+
        for plugin in utils.sub_module_iterator(internal_package)
        if not utils.try_import('{}.{}'.format(ansible_package, plugin[1]))
    ]


@utils.skip_if_editable
def test_callback_plugin_imports():
    missing_modules = get_missing_modules('ansibilo.plugins.callbacks', 'ansible.plugins.callback.ansibilo')
    assert not missing_modules, 'Can not import some callback plugins'


@utils.skip_if_editable
def test_filter_plugin_imports():
    missing_modules = get_missing_modules('ansibilo.plugins.filters', 'ansible.plugins.filter.ansibilo')
    assert not missing_modules, 'Can not import some filter plugins'


@utils.skip_if_editable
def test_module_imports():
    missing_modules = get_missing_modules('ansibilo.modules', 'ansible.modules.ansibilo')
    assert not missing_modules, 'Can not import some ansible module'
