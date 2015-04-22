import siptracklib.errors

from siptrackweb.views import helpers
from siptrackweb.forms import *

@helpers.authcheck
def add(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    device = pm.setVar('device', pm.object_store.getOID(oid))
    pm.path(device)
    view = device.getParent('view')
    network_trees = view.listChildren(include = ['network tree'])

    url = '/device/network/add/post/%s/' % (oid)
    pm.addForm(DeviceNetworkAddForm(network_trees), url)
    return pm.render()

@helpers.authcheck
def add_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    device = pm.setVar('device', pm.object_store.getOID(oid))
    pm.path(device)
    view = device.getParent('view')
    network_trees = view.listChildren(include = ['network tree'])

    url = '/device/network/add/post/%s/' % (oid)
    pm.addForm(DeviceNetworkAddForm(network_trees, request.POST), url)
    if not pm.form.is_valid():
        return pm.error()

    nt = pm.object_store.getOID(pm.form.cleaned_data['networktree'])
    address_string = pm.form.cleaned_data['network_name']
    network = nt.getNetworkOrRange(address_string)

    if device.isAssociated(network):
        return pm.error('address already associated')

    if network.isHost() and len(device.listNetworks()) > 0:
        network.attributes['secondary'] = True
    device.associate(network)

    return pm.redirect('device.display', (device.oid,))

@helpers.authcheck
def autoassign(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/networks/autoassign.html')
    device = pm.setVar('device', pm.object_store.getOID(oid))
    pm.path(device)

    return pm.render()

@helpers.authcheck
def autoassign_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/networks/autoassign.html')
    device = pm.setVar('device', pm.object_store.getOID(oid))
    pm.path(device)

    network = device.autoassignNetwork()
    if len(device.listNetworks()) > 0:
        network.attributes['secondary'] = True
    request.session['assigned network'] = network.oid

    return pm.redirect('device.display', (device.oid,))

@helpers.authcheck
def delete(request, device_oid, network_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/networks/delete.html')
    device = pm.setVar('device', pm.object_store.getOID(device_oid))
    pm.path(device)
    network = pm.setVar('network', pm.object_store.getOID(network_oid))

    return pm.render()

@helpers.authcheck
def delete_post(request, device_oid, network_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/networks/delete.html')
    device = pm.object_store.getOID(device_oid)
    pm.path(device)
    network = pm.object_store.getOID(network_oid)

    device.disassociate(network)
    network.prune()

    return pm.redirect('device.display', (device.oid,))

