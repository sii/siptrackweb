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

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/commands/display_queue.html')

    node = pm.setVar('queue', pm.object_store.getOID(oid))
    pm.render_var['parent'] = node.parent
    pm.render_var['attribute_list'] = attribute.parse_attributes(node)
    pm.render_var['command_list'] = node.listChildren(include = ['command'])
    pm.path(node)
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    url = '/command/queue/add/post/%s/' % (parent.oid)
    pm.addForm(CommandQueueAddForm(), url, 'add command queue')
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/command/queue/add/post/%s/' % (parent.oid)
    pm.addForm(CommandQueueAddForm(request.POST), url, 'add command queue')
    if not pm.form.is_valid():
        return pm.error()

    node = parent.add('command queue')
    if len(pm.form.cleaned_data['name']) > 0:
        node.attributes['name'] = pm.form.cleaned_data['name']

    return pm.redirect('display.display', (node.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('queue', pm.object_store.getOID(oid))
    form_data = {'name': node.attributes.get('name', '')}
    url = '/command/queue/update/post/%s/' % (node.oid)
    pm.addForm(CommandQueueUpdateForm(form_data), url, 'update command queue')
    pm.render_var['parent'] = node.parent
    pm.path(node)
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    url = '/command/queue/update/post/%s/' % (node.oid)
    pm.addForm(CommandQueueUpdateForm(request.POST), url, 'update command queue')
    if not pm.form.is_valid():
        return pm.error()

    if pm.form.cleaned_data['name'] != node.attributes.get('name'):
        node.attributes['name'] = pm.form.cleaned_data['name']

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('queue', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/command/queue/delete/post/%s/' % (node.oid),
            'remove command queue', message = 'Removing command queue.')
    pm.path(node)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    parent_oid = node.parent.oid
    pm.addForm(DeleteForm(request.POST), '/command/queue/delete/post/%s/' % (node.oid),
            'remove command', message = 'Removing command.')
    if not pm.form.is_valid():
        return pm.render()
    node.delete()

    return pm.redirect('display.display', (parent_oid,))

