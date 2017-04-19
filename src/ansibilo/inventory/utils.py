import os.path

import ansible.cli
import ansible.inventory
import ansible.constants
import ansible.parsing.dataloader
import ansible.parsing.vault
import ansible.vars


class FakeVaultLib(ansible.parsing.vault.VaultLib):
    def decrypt(self, *args, **kwargs):
        return b''


class DataLoader(ansible.parsing.dataloader.DataLoader):
    def set_vault_password(self, b_vault_password):
        if b_vault_password:
            return super(DataLoader, self).set_vault_password(b_vault_password)

        self._b_vault_password = None
        self._vault = FakeVaultLib(b_password=None)


def get_ansible_inventory(inventory_file=None):
    data_loader = DataLoader()
    variable_manager = ansible.vars.VariableManager()

    if (
        ansible.constants.DEFAULT_VAULT_PASSWORD_FILE
        and os.path.exists(ansible.constants.DEFAULT_VAULT_PASSWORD_FILE)
    ):
        vault_pass = ansible.cli.CLI.read_vault_password_file(
            ansible.constants.DEFAULT_VAULT_PASSWORD_FILE,
            data_loader,
        )
        data_loader.set_vault_password(vault_pass)
    return ansible.inventory.Inventory(
        loader=data_loader,
        variable_manager=variable_manager,
        host_list=inventory_file or ansible.constants.DEFAULT_HOST_LIST,
    )


def get_host_groups(inventory_file=None):
    inventory = get_ansible_inventory(inventory_file)
    return {
        host.name: [
            group.name
            for group in host.get_groups()
            if group.name != 'all'
        ]
        for host in inventory.list_hosts()
    }
