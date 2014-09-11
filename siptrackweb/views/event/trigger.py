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
    pm = helpers.PageManager(request, 'stweb/events/display_trigger.html')

    node = pm.setVar('trigger', pm.object_store.getOID(oid))
    pm.render_var['parent'] = node.parent
    pm.render_var['attribute_list'] = attribute.parse_attributes(node)
    pm.render_var['python_rule_list'] = node.listChildren(include = ['event trigger rule python'])
    pm.path(node)
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    url = '/event/trigger/add/post/%s/' % (parent.oid)
    pm.addForm(EventTriggerAddForm(), url, 'add event trigger')
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/event/trigger/add/post/%s/' % (parent.oid)
    pm.addForm(EventTriggerAddForm(request.POST), url, 'add event trigger')
    if not pm.form.is_valid():
        return pm.error()

    node = parent.add('event trigger')
    if len(pm.form.cleaned_data['name']) > 0:
        node.attributes['name'] = pm.form.cleaned_data['name']

    return pm.redirect('display.display', (node.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('trigger', pm.object_store.getOID(oid))
    form_data = {'name': node.attributes.get('name', '')}
    url = '/event/trigger/update/post/%s/' % (node.oid)
    pm.addForm(EventTriggerUpdateForm(form_data), url, 'update event trigger')
    pm.render_var['parent'] = node.parent
    pm.path(node)
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    url = '/event/trigger/update/post/%s/' % (node.oid)
    pm.addForm(EventTriggerUpdateForm(request.POST), url, 'update event trigger')
    if not pm.form.is_valid():
        return pm.error()

    if pm.form.cleaned_data['name'] != node.attributes.get('name'):
        node.attributes['name'] = pm.form.cleaned_data['name']

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('trigger', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/event/trigger/delete/post/%s/' % (node.oid),
            'remove event trigger', message = 'Removing event trigger.')
    pm.path(node)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    parent_oid = node.parent.oid
    pm.addForm(DeleteForm(request.POST), '/event/trigger/delete/post/%s/' % (node.oid),
            'remove event trigger', message = 'Removing event trigger.')
    if not pm.form.is_valid():
        return pm.render()
    node.delete()

    return pm.redirect('display.display', (parent_oid,))

