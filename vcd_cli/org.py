# vCloud CLI 0.1
#
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the
# Apache License, Version 2.0 (the "License").
# You may not use this product except in compliance with the License.
#
# This product may include a number of subcomponents with
# separate copyright notices and license terms. Your use of the source
# code for the these subcomponents is subject to the terms and
# conditions of the subcomponent's license, as noted in the LICENSE file.
#

import click
from lxml import etree
from pyvcloud.vcd.client import QueryResultFormat
from pyvcloud.vcd.client import get_links
from pyvcloud.vcd.client import EntityType
from pyvcloud.vcd.utils import org_to_object
import sys
import traceback
from vcd_cli.vcd import as_metavar
from vcd_cli.vcd import cli
from vcd_cli.utils import as_metavar
from vcd_cli.utils import restore_session
from vcd_cli.utils import stderr
from vcd_cli.utils import stdout


@cli.group(short_help='work with organizations')
@click.pass_context
def org(ctx):
    """Work with organizations in vCloud Director.

\b
    Examples
        vcd org list
            Get list of organizations.
\b
        vcd org info my-org
            Get details of the organization 'my-org'.
\b
        vcd org use my-org
            Set organization 'my-org' as default.
    """  # NOQA
    if ctx.invoked_subcommand is not None:
        try:
            restore_session(ctx)
        except Exception as e:
            stderr(e, ctx)


@org.command(short_help='show org details')
@click.pass_context
@click.argument('name',
                metavar='<name>',
                required=True)
def info(ctx, name):
    try:
        client = ctx.obj['client']
        logged_in_org_name = ctx.obj['profiles'].get('org')
        in_use_org_name = ctx.obj['profiles'].get('org_in_use')
        orgs = client.get_org_list()
        result = {}
        for org in orgs.findall('{http://www.vmware.com/vcloud/v1.5}Org'):
            if name == org.get('name'):
                resource = client.get_resource(org.get('href'))
                result = org_to_object(resource)
                result['logged_in'] = logged_in_org_name == \
                                      org.get('name')
                result['in_use'] = in_use_org_name == \
                                      org.get('name')
                stdout(result, ctx)
                return
        raise Exception('not found')
    except Exception as e:
        stderr(e, ctx)


@org.command(short_help='list organizations')
@click.pass_context
def list(ctx):
    try:
        client = ctx.obj['client']
        logged_in_org_name = ctx.obj['profiles'].get('org')
        in_use_org_name = ctx.obj['profiles'].get('org_in_use')
        orgs = client.get_org_list()
        result = []
        for org in orgs.findall('{http://www.vmware.com/vcloud/v1.5}Org'):
            result.append({'name': org.get('name'),
                           'logged_in': logged_in_org_name == \
                                        org.get('name'),
                            'in_use': in_use_org_name == org.get('name')})
        stdout(result, ctx)
    except Exception as e:
        stderr(e, ctx)


@org.command(short_help='set active organization')
@click.pass_context
@click.argument('name',
                metavar='<name>',
                required=True)
def use(ctx, name):
    try:
        client = ctx.obj['client']
        orgs = client.get_org_list()
        result = {}
        for org in orgs.findall('{http://www.vmware.com/vcloud/v1.5}Org'):
            if name == org.get('name'):
                resource = client.get_resource(org.get('href'))
                in_use_vdc = ''
                for v in get_links(resource, media_type=EntityType.VDC.value):
                    in_use_vdc = v.name
                    break
                ctx.obj['profiles'].set('org_in_use', str(name))
                ctx.obj['profiles'].set('vdc_in_use', in_use_vdc)
                stdout('now using org: \'%s\', vdc: \'%s\'.' % (name, in_use_vdc), ctx)
                return
        raise Exception('not found')
    except Exception as e:
        stderr(e, ctx)
