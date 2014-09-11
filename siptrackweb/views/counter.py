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

@helpers.authcheck
def index(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/counters/index.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.section('counter')

    include = ['counter', 'counter loop']
    pm.render_var['counter_list'] = parent.listChildren(include = include)
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/counters/display.html')

    counter = pm.setVar('counter', pm.object_store.getOID(oid))
    pm.render_var['parent'] = counter.parent
    pm.render_var['attribute_list'] = attribute.parse_attributes(counter)
    pm.path(counter)
    return pm.render()

@helpers.authcheck
def add_basic(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    url = '/counter/basic/add/post/%s/' % (parent.oid)
    pm.addForm(CounterAddBasicForm(), url, 'add counter')
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_basic_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/counter/basic/add/post/%s/' % (parent.oid)
    pm.addForm(CounterAddBasicForm(request.POST), url, 'add counter')
    if not pm.form.is_valid():
        return pm.error()

    counter = parent.add('counter')
    counter.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        counter.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('counter.display', (counter.oid,))

@helpers.authcheck
def add_looping(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    url = '/counter/looping/add/post/%s/' % (parent.oid)
    pm.addForm(CounterAddLoopingForm(), url, 'add counter')
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_looping_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/counter/looping/add/post/%s/' % (parent.oid)
    pm.addForm(CounterAddLoopingForm(request.POST), url, 'add counter')
    if not pm.form.is_valid():
        return pm.error()

    values = pm.form.cleaned_data['values']
    values = values.replace('\r', '\n').split('\n')
    values = [value for value in values if len(value) > 0]
    if len(values) == 0:
        return pm.error('invalid values')
    pm.form.cleaned_data['description']
    counter = parent.add('counter loop', values)
    counter.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        counter.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('counter.display', (counter.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    counter = pm.setVar('counter', pm.object_store.getOID(oid))
    form_data = {'name': counter.attributes.get('name', ''),
        'description': counter.attributes.get('description', ''),
        'value': counter.value}
    url = '/counter/update/post/%s/' % (counter.oid)
    if counter.class_name == 'counter':
        pm.addForm(CounterUpdateBasicForm(form_data), url, 'update counter')
    elif counter.class_name == 'counter loop':
        form_data['values'] = '\n'.join(counter.values)
        pm.addForm(CounterUpdateLoopingForm(form_data), url, 'update counter')
    pm.render_var['parent'] = counter.parent
    pm.path(counter)
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    counter = pm.object_store.getOID(oid)
    url = '/counter/update/post/%s/' % (counter.oid)
    if counter.class_name == 'counter':
        pm.addForm(CounterUpdateBasicForm(request.POST), url, 'update counter')
    elif counter.class_name == 'counter loop':
        pm.addForm(CounterUpdateLoopingForm(request.POST), url, 'update counter')
    if not pm.form.is_valid():
        return pm.error()

    if counter.class_name == 'counter loop':
        values = pm.form.cleaned_data['values']
        values = values.replace('\r', '\n').split('\n')
        values = [value for value in values if len(value) > 0]
        if len(values) == 0:
            return pm.error('invalid values')
        if counter.values != values:
            counter.values = values

    if pm.form.cleaned_data['name'] != counter.attributes.get('name', None):
        counter.attributes['name'] = pm.form.cleaned_data['name']
    if pm.form.cleaned_data['description'] != counter.attributes.get('description', None):
        counter.attributes['description'] = pm.form.cleaned_data['description']
    if pm.form.cleaned_data['value'] != counter.value:
        if counter.class_name == 'counter':
            counter.value = int(pm.form.cleaned_data['value'])
        elif counter.class_name == 'counter loop':
            counter.value = pm.form.cleaned_data['value']

    return pm.redirect('counter.display', (oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    counter = pm.setVar('counter', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/counter/delete/post/%s/' % (counter.oid),
            'remove counter', message = 'Removing counter.')
    pm.path(counter)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    counter = pm.object_store.getOID(oid)
    parent_oid = counter.parent.oid
    pm.addForm(DeleteForm(request.POST), '/counter/delete/post/%s/' % (counter.oid),
            'remove counter', message = 'Removing counter.')
    if not pm.form.is_valid():
        return pm.render()
    counter.delete()

    return pm.redirect('counter.index', (parent_oid,))

