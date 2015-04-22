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

def parse_config(obj):
    include = ['permission']
    return obj.listChildren(include = include)

def get_add_users(object_store):
    users = []
    for user in object_store.view_tree.user_manager.listUsers():
        users.append((user.oid, user.username))
    return users

def get_add_groups(object_store):
    groups = []
    for group in object_store.view_tree.user_manager.listGroups():
        groups.append((group.oid, group.attributes.get('name', '[NONE]')))
    return groups

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/permissions/display.html')

    permission = pm.setVar('permission', pm.object_store.getOID(oid))
    pm.render_var['parent'] = permission.parent
    pm.render_var['attribute_list'] = attribute.parse_attributes(permission)
    pm.render_var['permission'] = permission
    pm.path(permission)
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    users = get_add_users(pm.object_store)
    groups = get_add_groups(pm.object_store)
    form = PermissionAddForm(users, groups)
    url = '/permission/add/post/%s/' % (parent.oid)
    pm.addForm(form, url, 'add permission')
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    users = get_add_users(pm.object_store)
    groups = get_add_groups(pm.object_store)
    form = PermissionAddForm(users, groups, request.POST)
    url = '/permission/add/post/%s/' % (parent.oid)
    pm.addForm(form, url, 'add permission')
    if not pm.form.is_valid():
        return pm.error()

    form_users = [pm.object_store.getOID(oid) for oid in pm.form.cleaned_data['users']]
    form_groups = [pm.object_store.getOID(oid) for oid in pm.form.cleaned_data['groups']]

    permission = parent.add('permission', pm.form.cleaned_data['read_access'],
            pm.form.cleaned_data['write_access'],
            form_users,
            form_groups,
            pm.form.cleaned_data['all_users'],
            pm.form.cleaned_data['recursive'],
            )

    return pm.redirect('display.display', (parent_oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    permission = pm.setVar('permission', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/permission/delete/post/%s/' % (permission.oid),
            'remove permission', message = 'Removing permission.')
    pm.path(permission)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    permission = pm.object_store.getOID(oid)
    parent_oid = permission.parent.oid
    pm.addForm(DeleteForm(request.POST), '/permission/delete/post/%s/' % (permission.oid),
            'remove permission', message = 'Removing permission.')
    if not pm.form.is_valid():
        return pm.render()
    permission.delete()

    return pm.redirect('display.display', (parent_oid,))

