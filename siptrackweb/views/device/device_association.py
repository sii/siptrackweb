from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

import siptracklib.errors

from siptrackweb.views import helpers
from siptrackweb.forms import *

@helpers.authcheck
def add_with_target(request, oid):
    pm = helpers.PageManager(request, '')
    target = request.session.get('tagged_oid')
    device1 = pm.object_store.getOID(target)
    device2 = pm.object_store.getOID(oid)

    try:
        device1.associate(device2)
    except siptracklib.errors.SiptrackError, e:
        request.session['error_msg'] = 'association failed: %s' % (str(e))
    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def delete(request, oid1, oid2, type):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    device = pm.setVar('device', pm.object_store.getOID(oid1))
    if type == 'association':
        url = '/device/association/delete/post/%s/%s/' % (oid1, oid2)
    else:
        url = '/device/reference/delete/post/%s/%s/' % (oid1, oid2)
    
    pm.addForm(DeleteForm(), url,
            'remove device association',
            message = 'Removing device association.')

    pm.path(device)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid1, oid2, type):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    device1 = pm.object_store.getOID(oid1)
    device2 = pm.object_store.getOID(oid2)
    if type == 'association':
        pm.render_var['device'] = device1
        url = '/device/association/delete/post/%s/%s/' % (oid1, oid2)
    else:
        pm.render_var['device'] = device2
        url = '/device/reference/delete/post/%s/%s/' % (oid1, oid2)
    pm.addForm(DeleteForm(request.POST), url,
            'remove device association',
            message = 'Removing device association.')
    if not pm.form.is_valid():
        return pm.render()

    if type == 'association':
        device1.disassociate(device2)
    else:
        device2.disassociate(device1)

    return pm.redirect('display.display', (oid1,))


