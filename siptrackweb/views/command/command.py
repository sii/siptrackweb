from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from siptracklib.utils import object_by_attribute
import siptracklib.errors
from siptrackweb.views import helpers
from siptrackweb.views import attribute
from siptrackweb.forms import *
from siptrackweb.views import attribute

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/commands/display_command.html')

    node = pm.setVar('command', pm.object_store.getOID(oid))
    pm.render_var['parent'] = node.parent
    pm.render_var['attribute_list'] = attribute.parse_attributes(node)
    pm.path(node)
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    url = '/command/add/post/%s/' % (parent.oid)
    pm.addForm(CommandAddForm(), url, 'add command')
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/command/add/post/%s/' % (parent.oid)
    pm.addForm(CommandAddForm(request.POST), url, 'add command')
    if not pm.form.is_valid():
        return pm.error()

    freetext = pm.form.cleaned_data['freetext']
    node = parent.add('command', freetext)

    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('command', pm.object_store.getOID(oid))
    form_data = {'freetext': node.freetext}
    url = '/command/update/post/%s/' % (node.oid)
    pm.addForm(CommandUpdateForm(form_data), url, 'update command')
    pm.render_var['parent'] = node.parent
    pm.path(node)
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    url = '/command/update/post/%s/' % (node.oid)
    pm.addForm(CommandUpdateForm(request.POST), url, 'update command')
    if not pm.form.is_valid():
        return pm.error()

    if pm.form.cleaned_data['freetext'] != node.freetext:
        node.freetext = pm.form.cleaned_data['freetext']

    return pm.redirect('display.display', (node.parent.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('command', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/command/delete/post/%s/' % (node.oid),
            'remove command', message = 'Removing command.')
    pm.path(node)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    parent_oid = node.parent.oid
    pm.addForm(DeleteForm(request.POST), '/command/delete/post/%s/' % (node.oid),
            'remove command', message = 'Removing command.')
    if not pm.form.is_valid():
        return pm.render()
    node.delete()

    return pm.redirect('display.display', (parent_oid,))

