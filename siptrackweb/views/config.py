from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from siptracklib.utils import object_by_attribute
import siptracklib.errors
import helpers
from siptrackweb.forms import *
from siptrackweb.views import attribute

def parse_config(obj):
    include = ['config network autoassign',
            'config value']
    return obj.listChildren(include = include)

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/counters/display.html')

    counter = pm.setVar('counter', pm.object_store.getOID(oid))
    pm.render_var['parent'] = counter.parent
    pm.render_var['attribute_list'] = attribute.parse_attributes(counter)
    pm.path(counter)
    return pm.render()

@helpers.authcheck
def add_select(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    form = ConfigAddSelectTypeForm(parent)
    url = '/config/add/set/%s/' % (parent.oid)
    pm.addForm(form, url, 'add config item')
    return pm.render()

@helpers.authcheck
def add_set(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    form = ConfigAddSelectTypeForm(parent, request.POST)
    url = '/config/add/set/%s/' % (parent.oid)
    pm.addForm(form, url, 'add config item')
    if not form.is_valid():
        return pm.render()

    if form.cleaned_data['config_type'] == 'netautoassign':
        view = parent.getParent('view', include_self = True)
        network_trees = view.listChildren(include = ['network tree'])
        form = ConfigAddNetworkAutoassignForm(network_trees)
    elif form.cleaned_data['config_type'] == 'value':
        form = ConfigAddValueForm()
    else:
        return pm.error('bad, invalid ruletype')
    url = '/config/add/post/%s/' % (parent_oid)
    pm.addForm(form, url, 'add config item')

    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    config_type = request.POST.get('config_type', '')
    url = '/config/add/post/%s/' % (parent_oid)
    if config_type == 'netautoassign':
        view = parent.getParent('view', include_self = True)
        network_trees = view.listChildren(include = ['network tree'])
        form = ConfigAddNetworkAutoassignForm(network_trees, request.POST)
    elif config_type == 'value':
        form = ConfigAddValueForm(request.POST)
    else:
        return pm.error('bad, invalid config type')
    pm.addForm(form, url, '')
    if not form.is_valid():
        return pm.error('')

    if config_type == 'netautoassign':
        nt = pm.object_store.getOID(pm.form.cleaned_data['networktree'])
        parent.add('config network autoassign', nt,
                pm.form.cleaned_data['range_start'],
                pm.form.cleaned_data['range_end'])
    elif config_type == 'value':
        parent.add('config value',
                pm.form.cleaned_data['name'],
                pm.form.cleaned_data['value'])

    return pm.redirect('display.display', (parent_oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    config = pm.setVar('config', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/config/delete/post/%s/' % (config.oid),
            'remove config', message = 'Removing config.')
    pm.path(config)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    config = pm.object_store.getOID(oid)
    parent_oid = config.parent.oid
    pm.addForm(DeleteForm(request.POST), '/config/delete/post/%s/' % (config.oid),
            'remove config', message = 'Removing config.')
    if not pm.form.is_valid():
        return pm.render()
    config.delete()

    return pm.redirect('display.display', (parent_oid,))

