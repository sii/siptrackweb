from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from siptracklib.utils import object_by_attribute
import siptracklib.errors
from siptrackweb.views import helpers
from siptrackweb.forms import *

@helpers.authcheck
def index(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/index.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)
    pm.section('network')

    pm.render_var['network_tree_list'] = list(parent.listChildren(include = ['network tree']))
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/add.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)
    pm.section('network')

    pm.render_var['network_tree_list'] = parent.listChildren(include = ['network tree'])
    pm.setForm(NetworkTreeAddForm())
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/add.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)
    pm.section('network')

    pm.render_var['network_tree_list'] = parent.listChildren(include = ['network tree'])
    pm.setForm(NetworkTreeAddForm(request.POST))
    if not pm.form.is_valid():
        return pm.error()

    nt = parent.add('network tree', pm.form.cleaned_data['protocol'])
    nt.attributes['name'] = pm.form.cleaned_data['name']

    return pm.redirect('network.display', (nt.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/delete.html')
    pm.section('network')

    nt = pm.setVar('network_tree', pm.object_store.getOID(oid))
    pm.path(nt)
    pm.render_var['parent'] = nt.parent
    pm.render_var['network_tree_list'] = nt.parent.listChildren(include = ['network tree'])
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/networktrees/delete.html')
    pm.section('network')
    nt = pm.object_store.getOID(oid)
    parent_oid = nt.parent.oid
    nt.delete()

    return pm.redirect('network.tree.index', (parent_oid,))

