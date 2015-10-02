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
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/display_config.html')
    config = pm.object_store.getOID(oid)
    pm.render_var['config'] = config
    config.stats = config.getStats()
    if config.stats['latest_timestamp']:
        config.stats['pretty_latest_timestamp'] = time.ctime(config.stats['latest_timestamp'])
    else:
        config.stats['pretty_latest_timestamp'] = 'Nothing received'
    res = config.getLatestConfig()
    if res:
        pm.render_var['data'], pm.render_var['timestamp'] = res
    else:
        pm.render_var['data'] = None
        pm.render_var['timestamp'] = None
    pm.path(config)
    return pm.render()

@helpers.authcheck
def display_all(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/display_config_all.html')
    config = pm.object_store.getOID(oid)
    pm.render_var['config'] = config
    config.stats = config.getStats()
    if config.stats['latest_timestamp']:
        config.stats['pretty_latest_timestamp'] = time.ctime(config.stats['latest_timestamp'])
    else:
        config.stats['pretty_latest_timestamp'] = 'Nothing received'
    versions = []
    for version in config.getAllConfigs():
        data, timestamp = version
        versions.append({'timestamp': timestamp, 'pretty_timestamp': time.ctime(timestamp), 'data': data})
    versions.reverse()
    pm.render_var['versions'] = versions
    pm.path(config)
    return pm.render()

@helpers.authcheck
def download(request, oid, timestamp):
    pm = helpers.PageManager(request, '')
    config = pm.object_store.getOID(oid)
    data = config.getTimestampConfig(int(timestamp))
    return pm.renderDownload(data, 'config.txt')

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.addForm(DeviceConfigAddForm(), '/device/config/add/post/%s/' % (parent_oid))
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.addForm(DeviceConfigAddForm(request.POST), '/device/config/add/post/%s/' % (parent_oid))
    if not pm.form.is_valid():
        return pm.error()

    config = parent.add('device config', pm.form.cleaned_data['name'], pm.form.cleaned_data['max_versions'])

    if len(pm.form.cleaned_data['description']) > 0:
        config.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('device.display', (parent_oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    config = pm.setVar('config', pm.object_store.getOID(oid))
    url = '/device/config/delete/post/%s/' % (config.oid)
    pm.addForm(DeleteForm(), url,
            'remove config', message = 'Removing configuration.')
    pm.path(config)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    config = pm.setVar('config', pm.object_store.getOID(oid))
    pm.path(config)
    url = '/device/config/delete/post/%s/' % (config.oid)
    pm.addForm(DeleteForm(request.POST), url,
            'remove config', message = 'Removing configuration.')
    if not pm.form.is_valid():
        return pm.render()

    parent_oid = config.parent.oid
    config.delete()

    return pm.redirect('device.display', (parent_oid,))

@helpers.authcheck
def submit(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    config = pm.setVar('config', pm.object_store.getOID(oid))
    url = '/device/config/submit/post/%s/' % (config.oid)
    pm.addForm(DeviceConfigSubmitForm(), url,
            'submit config', message = 'Submit configuration.')
    pm.path(config)
    return pm.render()

@helpers.authcheck
def submit_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    config = pm.setVar('config', pm.object_store.getOID(oid))
    pm.path(config)
    url = '/device/config/submit/post/%s/' % (config.oid)
    pm.addForm(DeviceConfigSubmitForm(request.POST), url,
            'submit config', message = 'Submit configuration.')
    if not pm.form.is_valid():
        return pm.render()

    config.addConfig(pm.form.cleaned_data['data'])

    return pm.redirect('device.config.display', (config.oid,))

