import ansible.inventory.manager
import ansible.constants
import ansible.parsing.dataloader


def get_ansible_inventory(inventory_file=None):
    data_loader = ansible.parsing.dataloader.DataLoader()
    return ansible.inventory.manager.InventoryManager(
        loader=data_loader,
        sources=inventory_file or ansible.constants.DEFAULT_HOST_LIST
    )


def get_host_groups(inventory_file=None):
    inventory = get_ansible_inventory(inventory_file)
    return {
        host.name: sorted(
            group.name
            for group in host.get_groups()
            if group.name != 'all'
        )
        for host in inventory.list_hosts()
    }
