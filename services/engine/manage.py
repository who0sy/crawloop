# -*- coding: utf-8 -*-

import click
from flask.cli import FlaskGroup
from webs import create_app

app = create_app()
cli = FlaskGroup(create_app=create_app)


@cli.command('add_spider_server')
@click.argument('address')
def _add_spider_server(address):
    from webs.api.utils.helper import add_spider_server
    add_spider_server(address)


if __name__ == '__main__':
    cli()
