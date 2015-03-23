import json

import siptracklib.errors
from siptrackweb.views import helpers
from siptrackweb.views import attribute
from siptrackweb.views import config
from siptrackweb.forms import *

@helpers.authcheck
def display(request, pm, device):
    pm.render_path = 'stweb/views/devices/categories/display.html'
    pm.render_var['device'] = device
    # We do a manual fetch to avoid fetching associations/references that
    # are never used when displaying categories. Certain categories tend
    # to contain children that have large numbers of associations.
    # Without this, the first call to listChildren would trigger a fetch
    # of all children and all their associations/references.
    # Simon - 090219.
    device.fetch(max_depth = 1, include_associations = False,
            include_references = False)
    device.fetched_children = True
    pm.setVar('device_tree', device.getDeviceTree())
    pm.render_var['device_list'] = device.listChildren(include = ['device'])
    sort_method = device.attributes.get('web-device-sort-method')
    if sort_method == 'reverse':
        pm.render_var['device_list'].reverse()
    elif sort_method == 'letter-number':
        pm.render_var['device_list'].sort(cmp = helpers.device_letter_number_sorter)
    else:
        pass
    if device.attributes.get('reverse-device-sort-order', False):
        pm.render_var['device_list'].reverse()
    pm.render_var['category_list'] = device.listChildren(include = ['device category'])
    pm.render_var['attribute_list'] = attribute.parse_attributes(device)
    pm.render_var['config_list'] = config.parse_config(device)
    pm.render_var['template_list'] = device.listChildren(include = ['device template', 'network template'])
    pm.render_var['permission_list'] = device.listChildren(include = ['permission'])
    networks = device.listNetworks()
    hosts = [n for n in networks if n.isHost()]
    subnets = [n for n in networks if not n.isHost()]
    pm.render_var['network_host_list'] = hosts
    pm.render_var['network_subnet_list'] = subnets
    pm.render_var['template_add_type'] = 'device'

    if pm.tagged_oid and pm.tagged_oid.oid != device.oid and \
            pm.tagged_oid.class_name in ['device', 'device category']:
        pm.render_var['valid_tag_target'] = True

    pm.path(device)
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/categories/add.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.setForm(DeviceCategoryAddForm())
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/categories/add.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.setForm(ViewAddForm(request.POST))
    if not pm.form.is_valid():
        return pm.error()

    category = parent.add('device category')

    category.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        category.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('device.display', (parent_oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    category = pm.setVar('category', pm.object_store.getOID(oid))
    url = '/device/category/delete/post/%s/' % (category.oid)
    pm.addForm(DeleteForm(), url,
            'remove category', message = 'Removing device category.')
    pm.path(category)

    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    category = pm.setVar('category', pm.object_store.getOID(oid))
    pm.path(category)
    url = '/device/category/delete/post/%s/' % (category.oid)
    pm.addForm(DeleteForm(request.POST), url,
            'remove category', message = 'Removing device category.')
    if not pm.form.is_valid():
        return pm.render()

    parent_oid = category.parent.oid
    category.delete()

    return pm.redirect('display.display', (parent_oid,))

@helpers.authcheck
def export(request, oid):
    pm = helpers.PageManager(request, '')
    node = pm.object_store.getOID(oid)
    data = {'type': node.class_name, 'oid': node.oid, 'attributes': [], 'subdevices': [], 'devicelinks': [], 'class': node.attributes.get('class')}
    for attr in node.attributes:
        if attr.atype in ['binary']:
            continue
        data['attributes'].append({'name': attr.name, 'value': attr.value, 'type': attr.atype})
    for subdevice in node.listChildren(include = ['device']):
        data['subdevices'].append({'oid': subdevice.oid, 'name': subdevice.attributes.get('name', ''), 'class': subdevice.attributes.get('class', ''), 'disabled': subdevice.attributes.get('disabled', False)})
    for link in node.listLinks(include = ['device']):
        data['devicelinks'].append({'oid': link.oid, 'name': link.attributes.get('name', ''), 'class': link.attributes.get('class', '')})
    data = json.dumps(data, sort_keys=True, indent=2)
    filename = '%s.json' % (node.attributes.get('name', node.oid))
    filename = filename.replace(' ', '_').replace(',', '_')
    return pm.renderDownload(data, '%s.json' % (node.attributes.get('name', node.oid)))

