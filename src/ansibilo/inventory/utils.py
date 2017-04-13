import ansible.cli
import ansible.inventory
import ansible.constants
import ansible.parsing.dataloader
import ansible.vars


def get_ansible_inventory():
    data_loader = ansible.parsing.dataloader.DataLoader()
    variable_manager = ansible.vars.VariableManager()

    if ansible.constants.DEFAULT_VAULT_PASSWORD_FILE:
        vault_pass = ansible.cli.CLI.read_vault_password_file(
            ansible.constants.DEFAULT_VAULT_PASSWORD_FILE,
            data_loader,
        )
        data_loader.set_vault_password(vault_pass)
    return ansible.inventory.Inventory(
        loader=data_loader,
        variable_manager=variable_manager,
    )


def get_host_groups():
    inventory = get_ansible_inventory()
    return {
        host.name: [
            group.name
            for group in host.get_groups()
            if group.name != 'all'
        ]
        for host in inventory.list_hosts()
    }
