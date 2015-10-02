import re

from django.http import HttpResponse
import siptracklib.errors
import json
import time

from siptrackweb.views import helpers
from siptrackweb.views import attribute
from siptrackweb.views import config
from siptrackweb.views.device.utils import make_device_association_list
import category
from siptrackweb.forms import *

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.addForm(DeviceConfigTemplateAddForm(), '/device/config/template/add/post/%s/' % (parent_oid))
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.addForm(DeviceConfigTemplateAddForm(request.POST), '/device/config/template/add/post/%s/' % (parent_oid))
    if not pm.form.is_valid():
        return pm.error()

    data = pm.form.cleaned_data['data']
    if type(data) == unicode:
        data = data.encode('utf-8')
    template = parent.add('device config template', data)

    if len(pm.form.cleaned_data['name']) > 0:
        template.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        template.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('device.display', (parent_oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.setVar('template', pm.object_store.getOID(oid))
    url = '/device/config/template/delete/post/%s/' % (template.oid)
    pm.addForm(DeleteForm(), url,
            'remove config template', message = 'Removing configuration template.')
    pm.path(template)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.setVar('template', pm.object_store.getOID(oid))
    pm.path(template)
    url = '/device/config/template/delete/post/%s/' % (template.oid)
    pm.addForm(DeleteForm(request.POST), url,
            'remove config template', message = 'Removing configuration template.')
    if not pm.form.is_valid():
        return pm.render()

    parent_oid = template.parent.oid
    template.delete()

    return pm.redirect('device.display', (parent_oid,))

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/display_config_template.html')
    template = pm.object_store.getOID(oid)
    pm.render_var['template'] = template
    pm.render_var['data'] = template.template
    pm.path(template)
    return pm.render()

@helpers.authcheck
def submit(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.setVar('template', pm.object_store.getOID(oid))
    url = '/device/config/template/submit/post/%s/' % (template.oid)
    pm.addForm(DeviceConfigTemplateSubmitForm(), url,
            'submit template', message = 'Submit configuration template.')
    pm.path(template)
    return pm.render()

@helpers.authcheck
def submit_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.setVar('template', pm.object_store.getOID(oid))
    pm.path(template)
    url = '/device/config/template/submit/post/%s/' % (template.oid)
    pm.addForm(DeviceConfigTemplateSubmitForm(request.POST), url,
            'submit template', message = 'Submit configuration template.')
    if not pm.form.is_valid():
        return pm.render()

    data = pm.form.cleaned_data['data']
    if type(data) == unicode:
        data = data.encode('utf-8')
    template.template = data

    return pm.redirect('device.config_template.display', (template.oid,))

def generate(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/generate_config_template.html')
    template = pm.object_store.getOID(oid)
    pm.render_var['template'] = template
    pm.render_var['data'] = template.template
    pm.render_var['generated'] = template.expand()
    pm.path(template)
    return pm.render()

@helpers.authcheck
def download(request, oid):
    pm = helpers.PageManager(request, '')
    template = pm.object_store.getOID(oid)
    data = template.expand()
    return pm.renderDownload(data, 'config.txt')

