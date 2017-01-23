import json
from django.http import HttpResponse, HttpResponseServerError
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
def index(request, view_oid):
    pm = helpers.PageManager(request, 'stweb/passwords/index.html', 'password')
    view = pm.object_store.getOID(view_oid)
    if view.class_name == 'password tree':
        password_tree = view
        view = view.parent
    else:
        password_tree = view.getChildByName('default', include = ['password tree'])
        if not password_tree:
            password_tree = view.add('password tree')
            password_tree.attributes['name'] = 'default'
    pm.path(password_tree)
    pm.render_var['view'] = view
    pm.render_var['parent'] = pm.render_var['password_tree'] = password_tree
    pm.render_var['password_key_list'] = view.listChildren(include = ['password key'])
    pm.render_var['password_category_list'] = password_tree.listChildren(include = ['password category'])
    pm.render_var['password_list'] = password_tree.listChildren(include = ['password'])
    return pm.render()

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(
        request,
        'stweb/passwords/display.html',
        'password'
    )
    pm.section('password')

    password = pm.setVar('password', pm.object_store.getOID(oid))
    pm.path(password)

    pm.render_var['attribute_list'] = attribute.parse_attributes(password)
    return pm.render()

@helpers.authcheck
def key_display(request, oid):
    pm = helpers.PageManager(request, 'stweb/passwords/display_passwordkey.html', 'password')
    pm.section('password')

    pk = pm.setVar('password_key', pm.object_store.getOID(oid))
    pm.path(pk)

    view = pk.getParent('view')
    view_tree = view.parent
    user_manager = view_tree.user_manager
    user_list = []
    
    if request.session['administrator']:
        for users in user_manager.listChildren():
            try:
                username = users.username
                for subkey in users.listChildren(include=['sub key']):
                    if subkey.password_key is pk:
                        user_list.append(users)
            except:
                continue

    pm.render_var['user_list'] = user_list
    pm.render_var['parent'] = pk.parent
    pm.render_var['password_key_list'] = pk.parent.listChildren(include = ['password key'])
    pm.render_var['attribute_list'] = attribute.parse_attributes(pk)
    return pm.render()

@helpers.authcheck
def key_add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.render_var['password_key_list'] = parent.listChildren(include = ['password key'])
    url = '/password/key/add/post/%s/' % (parent.oid)
    pm.addForm(PasswordKeyAddForm(), url, 'add password key')
    return pm.render()

@helpers.authcheck
def key_add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.render_var['password_key_list'] = parent.listChildren(include = ['password key'])
    url = '/password/key/add/post/%s/' % (parent.oid)
    pm.addForm(PasswordKeyAddForm(request.POST), url, 'add password key')
    if not pm.form.is_valid():
        return pm.error()
    if not pm.form.cleaned_data['key'] == pm.form.cleaned_data['validate']:
        return pm.error('keys don\'t match')

    pk = parent.add('password key', pm.form.cleaned_data['key'])
    pk.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        pk.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('password.key_display', (pk.oid,))

@helpers.authcheck
def key_delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')

    pk = pm.setVar('password_key', pm.object_store.getOID(oid))
    pm.path(pk)
    pm.render_var['parent'] = pk.parent
    pm.render_var['password_key_list'] = pk.parent.listChildren(include = ['password key'])
    url = '/password/key/delete/post/%s/' % (oid)
    pm.addForm(DeleteForm(), url,
            'remove password key', message = 'Removing password key.')
    return pm.render()

@helpers.authcheck
def key_delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    pk = pm.object_store.getOID(oid)
    pm.path(pk)
    parent_oid = pk.parent.oid
    url = '/password/key/delete/post/%s/' % (oid)
    pm.addForm(DeleteForm(request.POST), url,
            'remove password key', message = 'Removing password key.')
    if not pm.form.is_valid():
        return pm.render()
    try:
        pk.delete()
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))

    return pm.redirect('password.index', (parent_oid,))


@helpers.authcheck
def ajax_key_is_valid(request):
    if request.method != 'POST':
        return HttpResponseServerError(
            json.dumps({
                'error': 'Incorrect method'
            }),
            content_type='application/json'
        )

    pm = helpers.PageManager(request, '')

    try:
        pk = pm.object_store.getOID(request.POST.get('passwordKeyOid'))
    except siptracklib.errors.NonExistent as e:
        return HttpResponse(
            json.dumps({
                'error': 'Password key not found'
            }),
            status=404,
            content_type='application/json'
        )
    except Exception as e:
        return HttpResponseServerError(
            json.dumps({
                'error': str(e)
            }),
            content_type='application/json'
        )

    try:
        test_password = request.POST.get('passwordKeyPassword')
        pk.isValidPassword(test_password)
    except Exception as e:
        return HttpResponseServerError(
            json.dumps({
                'status': False,
                'error': str(e)
            }),
            content_type='application/json'
        )

    return HttpResponse(
        json.dumps({
            'status': True
        }),
        content_type='application/json'
    )


@helpers.authcheck
def category_display(request, oid):
    pm = helpers.PageManager(request, 'stweb/passwords/display_category.html', 'password')

    pc = pm.setVar('password_category', pm.object_store.getOID(oid))
    pm.path(pc)
    pm.render_var['parent'] = pc
    pm.render_var['attribute_list'] = attribute.parse_attributes(pc)
    pm.render_var['password_category_list'] = pc.listChildren(include = ['password category'])
    pm.render_var['password_list'] = pc.listChildren(include = ['password'])
    return pm.render()

@helpers.authcheck
def category_add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/password/category/add/post/%s/' % (parent.oid)
    pm.addForm(PasswordCategoryAddForm(), url, 'add password category')
    return pm.render()

@helpers.authcheck
def category_add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/password/category/add/post/%s/' % (parent.oid)
    pm.addForm(PasswordCategoryAddForm(request.POST), url, 'add password category')
    if not pm.form.is_valid():
        return pm.error()

    pc = parent.add('password category')
    pc.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        pc.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('password.category_display', (pc.oid,))

@helpers.authcheck
def category_delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')

    category = pm.setVar('category', pm.object_store.getOID(oid))
    pm.path(category)
    pm.render_var['parent'] = category.parent
    url = '/password/category/delete/post/%s/' % (oid)
    pm.addForm(DeleteForm(), url,
            'remove password category', message = 'Removing password category.')
    return pm.render()

@helpers.authcheck
def category_delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    category = pm.object_store.getOID(oid)
    pm.path(category)
    parent_oid = category.parent.oid
    url = '/password/category/delete/post/%s/' % (oid)
    pm.addForm(DeleteForm(request.POST), url,
            'remove password category', message = 'Removing password category.')
    if not pm.form.is_valid():
        return pm.render()
    try:
        category.delete()
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))

    return pm.redirect('display.display', (parent_oid,))

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)
    view = parent.getParent('view')

    password_keys = view.listChildren(include = ['password key'])
    url = '/password/add/post/%s/' % (parent.oid)
    pm.addForm(PasswordAddForm(password_keys), url,
            'add password', message = 'Adding password.',
            extraelements = 'autocomplete="off"')
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)
    view = parent.getParent('view')

    password_keys = view.listChildren(include = ['password key'])
    url = '/password/add/post/%s/' % (parent.oid)
    pm.addForm(PasswordAddForm(password_keys, request.POST), url,
            'add password', message = 'Adding password.',
            extraelements = 'autocomplete="off"')

    if not pm.form.is_valid():
        return pm.error()
    if not pm.form.cleaned_data['pw_password'] == pm.form.cleaned_data['validate']:
        return pm.error('passwords don\'t match')

    password_key = None
    if pm.form.cleaned_data['passwordkey'] != '__no-password-key__':
        password_key = pm.object_store.getOID(pm.form.cleaned_data['passwordkey'])

    password_string = pm.form.cleaned_data['pw_password']
    if len(password_string) == 0:
        password_string = helpers.generate_password()

    try:
        password = parent.add('password', password_string, password_key)
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))

    password.attributes['username'] = pm.form.cleaned_data['pw_username']
    if len(pm.form.cleaned_data['description']) > 0:
        password.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')

    password = pm.object_store.getOID(oid)
    pm.addForm(DeleteForm(), '/password/delete/post/%s/' % (password.oid),
            'remove password', message = 'Removing password.')
    pm.path(password)

    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')

    password = pm.object_store.getOID(oid)
    parent = password.parent
    pm.path(password)
    pm.addForm(DeleteForm(request.POST), '/password/delete/post/%s/' % (password.oid),
            'remove password', message = 'Removing password.')

    if not pm.form.is_valid():
        return pm.render()
    password.delete()

    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    password = pm.setVar('password', pm.object_store.getOID(oid))
    pm.path(password)
    view = password.getParent('view')

    password_keys = view.listChildren(include = ['password key'])
    url = '/password/update/post/%s/' % (oid)
    pk = ''
    if password.key:
        pk = password.key.oid
    form_data = {'pw_username': password.attributes.get('username', ''),
                 'description': password.attributes.get('description', ''),
                 'pw_password': '',
                 'validate': '',
                 'passwordkey': pk}
    pm.addForm(PasswordUpdateForm(password_keys, form_data), url,
            'update password', message = 'Updating password.',
            extraelements = 'autocomplete="off"')
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html', 'password')
    password = pm.setVar('password', pm.object_store.getOID(oid))
    pm.path(password)
    view = password.getParent('view')

    password_keys = view.listChildren(include = ['password key'])
    url = '/password/update/post/%s/' % (oid)
    pm.addForm(PasswordUpdateForm(password_keys, request.POST), url,
            'update password', message = 'Updating password.',
            extraelements = 'autocomplete="off"')

    if not pm.form.is_valid():
        return pm.error()
    if not pm.form.cleaned_data['pw_password'] == pm.form.cleaned_data['validate']:
        return pm.error('passwords don\'t match')

    if pm.form.cleaned_data['pw_password']:
        password.setPassword(pm.form.cleaned_data['pw_password'])

    if pm.form.cleaned_data['pw_username'] != password.attributes.get('username'):
        password.attributes['username'] = pm.form.cleaned_data['pw_username']
    if pm.form.cleaned_data['description'] != password.attributes.get('description'):
        password.attributes['description'] = pm.form.cleaned_data['description']


    password_key = None
    if pm.form.cleaned_data['passwordkey'] != '__no-password-key__':
        password_key = pm.object_store.getOID(pm.form.cleaned_data['passwordkey'])
    if password_key != password.key:
        password.setPasswordKey(password_key)

    return pm.redirect('display.display', (password.parent.oid,))
