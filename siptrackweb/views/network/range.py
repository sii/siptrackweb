from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from siptracklib.utils import object_by_attribute
import siptracklib.errors
from siptrackweb.views import helpers
from siptrackweb.forms import *
from siptrackweb.views import attribute
from siptrackweb.views import config

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/display_range.html')
    range = pm.object_store.getOID(oid)
    network_tree = range.getNetworkTree()
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])

    pm.render_var['browsable_path'] = []
    pm.render_var['network_tree'] = network_tree
    pm.render_var['network_range'] = range
    pm.render_var['network'] = range
    pm.render_var['template_list'] = range.listChildren(include = ['device template', 'network template'])
    pm.render_var['attribute_list'] = attribute.parse_attributes(range)
    pm.render_var['config_list'] = config.parse_config(range)
    pm.render_var['device_list'] = range.listReferences(include = ['device', 'device category'])
    pm.path(range)
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/add_range.html')
    parent = pm.object_store.getOID(parent_oid)
    network_tree = parent.getNetworkTree()
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])

    pm.render_var['network_tree'] = network_tree
    pm.render_var['parent'] = parent
    pm.setForm(NetworkRangeAddForm())
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/add_range.html')
    parent = pm.object_store.getOID(parent_oid)
    pm.path(parent)
    network_tree = parent.getNetworkTree()
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])
    pm.render_var['network_tree'] = network_tree

    pm.setForm(NetworkRangeAddForm(request.POST))
    if not pm.form.is_valid():
        return pm.error()

    range = network_tree.addNetworkRange(pm.form.cleaned_data['range'])

    if len(pm.form.cleaned_data['description']) > 0:
        range.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('network.range.display', (range.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/delete_range.html')
    range = pm.object_store.getOID(oid)
    network_tree = range.getNetworkTree()
    pm.render_var['network_tree'] = network_tree
    pm.render_var['network_tree_list'] = network_tree.parent.listChildren(include = ['network tree'])
    pm.render_var['network_range'] = range

    pm.path(range)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/networks/delete_range.html')
    range = pm.object_store.getOID(oid)

    parent_oid = range.parent.oid
    range.delete()

    return pm.redirect('network.display', (parent_oid,))
