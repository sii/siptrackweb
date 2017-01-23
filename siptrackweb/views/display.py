import siptracklib
import helpers
import view
import counter
import device
import device.specification
import password
import network
import network.tree
import network.range
import user
import attribute
import template
import permission
import command
import command.queue
import event.trigger
import event.trigger_rule_python

display_functions = {
    'attribute': attribute.display,
    'versioned attribute': attribute.display,
    'counter': counter.display,
    'counter loop': counter.display,
    'device': device.display,
    'device category': device.display,
    'device tree': device.display,
    'device specification': device.specification.display,
    'password': password.display,
    'password key': password.key_display,
    'password category': password.category_display,
    'password tree': password.index,
    'view': view.display,
    'network tree': network.display,
    'ipv4 network': network.display,
    'ipv4 network range': network.range.display,
    'ipv6 network': network.display,
    'ipv6 network range': network.range.display,
    'user local': user.display,
    'user ldap': user.display,
    'user active directory': user.display,
    'user manager local': user.manager_display,
    'user manager ldap': user.manager_display,
    'user manager active directory': user.manager_display,
    'user group': user.group_display,
    'device template': template.display,
    'network template': template.display,
    'permission': permission.display,
    'view tree': view.index,
    'command': command.display,
    'command queue': command.queue.display,
    'event trigger': event.trigger.display,
    'event trigger rule python': event.trigger_rule_python.display,
}

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/index.html')
    try:
        obj = pm.object_store.getOID(oid)
    except siptracklib.errors.NonExistent:
        return pm.error('sorry, missing oid "%s"' % (oid))
    if obj.class_name in display_functions:
        return display_functions[obj.class_name](request, oid)
    else:
        return pm.error('sorry, unknown object class "%s" for generic display' % (obj.class_name))
