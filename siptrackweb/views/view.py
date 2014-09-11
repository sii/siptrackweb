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
from siptrackweb.views import config
from siptrackweb.views import permission

@helpers.authcheck
def index(request, *args, **kwargs):
    pm = helpers.PageManager(request, 'stweb/views/index.html')
    pm.render_var['config_list'] = config.parse_config(pm.view_tree)
    pm.render_var['permission_list'] = pm.view_tree.listChildren(include = ['permission'])
    pm.render_var['command_queue_list'] = pm.view_tree.listChildren(include = ['command queue'])
    pm.render_var['event_trigger_list'] = pm.view_tree.listChildren(include = ['event trigger'])
    pm.path(pm.view_tree)
    pm.section('view')
    return pm.render()

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/display.html')
    view = pm.setVar('view', pm.object_store.getOID(oid))
    pm.render_var['attribute_list'] = attribute.parse_attributes(view)
    pm.render_var['config_list'] = config.parse_config(view)
    pm.render_var['permission_list'] = view.listChildren(include = ['permission'])
    pm.path(view)
    pm.section('view')
    return pm.render()

@helpers.authcheck
def add(request):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    pm.addForm(ViewAddForm(), '/view/add/post/', 'add view')
    pm.path(None)
    pm.section('view')
    return pm.render()

@helpers.authcheck
def add_post(request):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    pm.addForm(ViewAddForm(request.POST), '/view/add/post/', 'add view')
    if not pm.form.is_valid():
        return pm.render()

    view = pm.view_tree.add('view')
    view.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        view.attributes['description'] = pm.form.cleaned_data['description']

    pm.path(None)
    pm.section('view')
    return pm.redirect('display.display', (view.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    view = pm.setVar('view', pm.object_store.getOID(oid))
    name = view.attributes.get('name', '')
    description = view.attributes.get('description', '')
    args = {'name': name, 'description': description}
    url = '/view/update/post/%s/' % (view.oid)
    pm.addForm(ViewUpdateForm(args), url, 'update view')

    pm.path(view)
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    view = pm.setVar('view', pm.object_store.getOID(oid))

    url = '/view/update/post/%s/' % (view.oid)
    pm.addForm(ViewUpdateForm(request.POST), url, 'update view')
    if not pm.form.is_valid():
        return pm.render()

    view.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        view.attributes['description'] = pm.form.cleaned_data['description']

    pm.path(view)
    return pm.redirect('view.display', (view.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    view = pm.setVar('view', pm.object_store.getOID(oid))
    pm.render_var['network_tree_list'] = view.listChildren(include = ['network tree'])
    pm.addForm(DeleteForm(), '/view/delete/post/%s/' % (view.oid),
            'remove view', message = 'Removing view.')

    pm.path(view)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    view = pm.setVar('view', pm.object_store.getOID(oid))
    pm.render_var['network_tree_list'] = view.listChildren(include = ['network tree'])
    pm.addForm(DeleteForm(request.POST), '/view/delete/post/%s/' % (view.oid),
            'remove view', message = 'Removing view.')
    if not pm.form.is_valid():
        return pm.render()

    view.delete()

    return pm.redirect('view.index')

