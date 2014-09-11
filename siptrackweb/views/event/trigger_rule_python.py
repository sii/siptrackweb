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
    pm = helpers.PageManager(request, 'stweb/events/display_python_rule.html')

    node = pm.setVar('rule', pm.object_store.getOID(oid))
    pm.render_var['parent'] = node.parent
    pm.render_var['attribute_list'] = attribute.parse_attributes(node)
    pm.path(node)
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    url = '/event/trigger/rule/python/add/post/%s/' % (parent.oid)
    pm.addForm(EventTriggerRulePythonAddForm(), url, 'add python rule')
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/event/trigger/rule/python/add/post/%s/' % (parent.oid)
    pm.addForm(EventTriggerRulePythonAddForm(request.POST), url, 'add python rule')
    if not pm.form.is_valid():
        return pm.error()

    node = parent.add('event trigger rule python', pm.form.cleaned_data['code'].replace('\r', ''))
    if len(pm.form.cleaned_data['name']) > 0:
        node.attributes['name'] = pm.form.cleaned_data['name']

    return pm.redirect('display.display', (node.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('rule', pm.object_store.getOID(oid))
    form_data = {'name': node.attributes.get('name', ''),
                 'code': node.code}
    url = '/event/trigger/rule/python/update/post/%s/' % (node.oid)
    pm.addForm(EventTriggerRulePythonUpdateForm(form_data), url, 'update python rule')
    pm.render_var['parent'] = node.parent
    pm.path(node)
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    url = '/event/trigger/rule/python/update/post/%s/' % (node.oid)
    pm.addForm(EventTriggerRulePythonUpdateForm(request.POST), url, 'update python rule')
    if not pm.form.is_valid():
        return pm.error()

    if pm.form.cleaned_data['name'] != node.attributes.get('name'):
        node.attributes['name'] = pm.form.cleaned_data['name']

    if pm.form.cleaned_data['code'] != node.code:
        node.code = pm.form.cleaned_data['code'].replace('\r', '')

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    node = pm.setVar('rule', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/event/trigger/rule/python/delete/post/%s/' % (node.oid),
            'remove python rule', message = 'Removing python rule.')
    pm.path(node)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    node = pm.object_store.getOID(oid)
    parent_oid = node.parent.oid
    pm.addForm(DeleteForm(request.POST), '/event/trigger/rule/python/delete/post/%s/' % (node.oid),
            'remove python rule', message = 'Removing python rule.')
    if not pm.form.is_valid():
        return pm.render()
    node.delete()

    return pm.redirect('display.display', (parent_oid,))

