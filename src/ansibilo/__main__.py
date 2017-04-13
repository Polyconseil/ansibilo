import click

from .inventory import exporters
from .inventory import utils


@click.group()
def main():
    pass


@main.command('export-inventory')
@click.option('--data-center-prefix', default='dc-')
@click.argument('output_format', type=click.Choice(exporters.FORMAT_EXPORTERS))
def export_inventory(output_format, data_center_prefix):
    print(
        exporters.FORMAT_EXPORTERS[output_format](
            utils.get_host_groups(),
            data_center_prefix
        )
    )


if __name__ == '__main__':
    main()
