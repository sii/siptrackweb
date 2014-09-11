from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from siptracklib.utils import object_by_attribute
import siptracklib.errors
from siptrackweb.views import helpers
from siptrackweb.views import attribute
from siptrackweb.views import config
from siptrackweb.forms import *

def make_device_association_list(network):
    ret = []
    if network.class_name not in ['ipv4 network', 'ipv6 network']:
        return ret
    for device in network.listAssociations(include = ['device']):
        path = helpers.make_browsable_path(device, ['device category', 'device tree'],
                include_root = False)
        ent = {'obj': device, 'path': path, 'type': 'association'}
        ret.append(ent)
    for device in network.listReferences(include = ['device']):
        path = helpers.make_browsable_path(device, ['device category', 'device tree'],
                include_root = False)
        ent = {'obj': device, 'path': path, 'type': 'reference'}
        ret.append(ent)
    return ret

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/display.html')
    network = pm.object_store.getOID(oid)
    network_tree = network.getNetworkTree()
#    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])

    pm.render_var['browsable_path'] = []
    pm.render_var['network_tree'] = network_tree
    pm.render_var['network'] = network
    pm.render_var['template_list'] = network.listChildren(include = ['device template', 'network template'])
    pm.render_var['permission_list'] = network.listChildren(include = ['permission'])
    if request.GET.get('display_missing', '') == 'true':
        pm.render_var['network_list'] = list(network.listNetworks(include_missing = True))
    else:
        pm.render_var['network_list'] = list(network.listNetworks())
    for n in pm.render_var['network_list']:
        n.device_association_list = make_device_association_list(n)
    pm.render_var['network_range_list'] = network.listNetworkRanges()
    pm.render_var['attribute_list'] = attribute.parse_attributes(network)
    pm.render_var['config_list'] = config.parse_config(network)
    pm.render_var['device_list'] = network.listReferences(include = ['device', 'device category'])
    pm.render_var['template_add_type'] = 'network'
    assoc_list = make_device_association_list(network)
    pm.render_var['device_association_list'] = assoc_list
    pm.path(network)

    if pm.tagged_oid and pm.tagged_oid.class_name in ['ipv4 network', 'ipv6 network']:
        if network == network_tree:
            tagged_network_tree = pm.tagged_oid.getNetworkTree()
            if tagged_network_tree != network_tree:
                if tagged_network_tree.protocol == network_tree.protocol:
                    pm.render_var['valid_tag_target'] = True

    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/add.html')
    network = pm.object_store.getOID(parent_oid)
    network_tree = network.getNetworkTree()
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])

    pm.render_var['network_tree'] = network_tree
    pm.render_var['network'] = network
    pm.setForm(NetworkAddForm())
    pm.path(network)
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/add.html')
    parent = pm.object_store.getOID(parent_oid)
    pm.path(parent)
    network_tree = parent.getNetworkTree()
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])
    pm.render_var['network_tree'] = network_tree

    pm.setForm(NetworkAddForm(request.POST))
    if not pm.form.is_valid():
        return pm.error()

    network = network_tree.addNetwork(pm.form.cleaned_data['name'].strip())

    if len(pm.form.cleaned_data['description']) > 0:
        network.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('network.display', (network.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/delete.html')
    network = pm.object_store.getOID(oid)
    network_tree = network.getNetworkTree()
    pm.render_var['network_tree'] = network_tree
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])
    pm.render_var['network'] = network

    pm.setForm(NetworkDeleteForm())

    pm.path(network)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/delete.html')
    network = pm.object_store.getOID(oid)
    pm.path(network)
    network_tree = network.getNetworkTree()
    pm.render_var['network_tree'] = network_tree
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])
    pm.render_var['network'] = network

    pm.setForm(NetworkDeleteForm(request.POST))
    if not pm.form.is_valid():
        return pm.error('invalid value for recursive')

    parent_oid = network.parent.oid

    network.delete(pm.form.cleaned_data['recursive'])

    return pm.redirect('network.display', (parent_oid,))

