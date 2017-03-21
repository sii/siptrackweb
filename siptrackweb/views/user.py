import json
from django.http import HttpResponse, HttpResponseRedirect
from django.http import HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.core.urlresolvers import reverse
from siptracklib.utils import object_by_attribute
import siptracklib.errors
import helpers
from siptrackweb.forms import *
from siptrackweb.views import attribute

def make_user_manager_list(view_tree):
    user_managers = []
    for um in view_tree.listChildren(include = ['user manager local',
        'user manager ldap', 'user manager active directory']):
        data = {}
        data['obj'] = um
        if um is view_tree.user_manager:
            data['active'] = True
        else:
            data['active'] = False
        if um.class_name == 'user manager local':
            data['type'] = 'local'
        elif um.class_name == 'user manager ldap':
            data['type'] = 'ldap'
        elif um.class_name == 'user manager active directory':
            data['type'] = 'ad'
        user_managers.append(data)
    return user_managers

@helpers.authcheck
def index(request):
    pm = helpers.PageManager(request, 'stweb/users/index.html')
    pm.section('user')

    if request.session['administrator']:
        um_list = make_user_manager_list(pm.view_tree)
        pm.render_var['user_manager_list'] = um_list
        pm.render_var['session_list'] = pm.object_store.listServerSessions()
        pm.path(None)
        return pm.render()
    else:
        user = pm.object_store.getSessionUser()
        return pm.redirect('display.display', (user.oid,))

@helpers.authcheck
def manager_display(request, oid):
    pm = helpers.PageManager(request, 'stweb/users/display_user_manager.html')
    pm.section('user')
    if not request.session['administrator']:
        user = pm.object_store.getSessionUser()
        return pm.redirect('display.display', (user.oid,))

    um = pm.object_store.getOID(oid)
    pm.render_var['user_manager'] = um
    pm.render_var['user_list'] = um.listChildren(include = ['user local',
        'user ldap', 'user active directory'])
    pm.render_var['group_list'] = um.listChildren(include = ['user group', 'user group ldap', 'user group active directory'])
    pm.render_var['attribute_list'] = attribute.parse_attributes(um)
    pm.path(um)
    return pm.render()

@helpers.authcheck
def manager_ldap_syncusers(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    um = pm.object_store.getOID(oid)
    pm.addForm(EmptyForm(),
            '/user/manager/syncusers/ldap/post/%s/' % (oid),
            'sync users', message = 'Sync user list from ldap server.')
    pm.path(um)
    return pm.render()

@helpers.authcheck
def manager_ldap_syncusers_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    um = pm.object_store.getOID(oid)
    pm.path(um)
    pm.addForm(EmptyForm(request.POST),
            '/user/manager/syncusers/ldap/post/%s/' % (oid),
            'sync users', message = 'Sync user list from ldap server.')
    if not pm.form.is_valid():
        return pm.render()
    um.syncUsers(purge_missing_users = True)

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def manager_ad_syncusers(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    um = pm.object_store.getOID(oid)
    pm.addForm(UsermanagerADSyncUsersForm(),
            '/user/manager/syncusers/ad/post/%s/' % (oid),
            'sync users', message = 'Sync user list from AD server.')
    pm.path(um)
    return pm.render()

@helpers.authcheck
def manager_ad_syncusers_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    um = pm.object_store.getOID(oid)
    pm.path(um)
    pm.addForm(UsermanagerADSyncUsersForm(request.POST),
            '/user/manager/syncusers/ad/post/%s/' % (oid),
            'sync users', message = 'Sync user list from AD server.')
    if not pm.form.is_valid():
        return pm.render()
    um.syncUsers(pm.form.cleaned_data['username'], pm.form.cleaned_data['password'],
                 purge_missing_users = True)

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def manager_activate(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    um = pm.object_store.getOID(oid)
    pm.addForm(EmptyForm(),
            '/user/manager/activate/post/%s/' % (oid),
            'activate user manager', message = 'Activate user manager.')
    pm.path(um)
    return pm.render()

@helpers.authcheck
def manager_activate_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    um = pm.object_store.getOID(oid)
    pm.path(um)
    pm.addForm(EmptyForm(request.POST),
            '/user/manager/activate/post/%s/' % (oid),
            'activate user manager', message = 'Activate user manager.')
    if not pm.form.is_valid():
        return pm.render()
    pm.view_tree.user_manager = um

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def add(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    url = '/user/add/post/%s/' % (oid)
    pm.addForm(UserAddForm(), url, 'add user')
    pm.path(None)
    return pm.render()

@helpers.authcheck
def add_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    pm.path(None)

    url = '/user/add/post/%s/' % (oid)
    pm.addForm(UserAddForm(request.POST), url, 'add user')
    if not pm.form.is_valid():
        return pm.error()
    if pm.form.cleaned_data['password'] != pm.form.cleaned_data['validate']:
        return pm.error('passwords don\'t match')

    um = pm.object_store.getOID(oid)
    user_type = None
    if um.class_name == 'user manager local':
        user_type = 'user local'
    elif um.class_name == 'user manager ldap':
        user_type = 'user ldap'
    elif um.class_name == 'user manager active directory':
        user_type = 'user active directory'
    try:
        user = um.add(user_type,
                pm.form.cleaned_data['user_name'],
                pm.form.cleaned_data['password'],
                pm.form.cleaned_data['administrator'])
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))
    user.attributes['real_name'] = pm.form.cleaned_data['real_name']
    user.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/users/display_user.html')

    user = pm.setVar('user', pm.object_store.getOID(oid))

    # Set a render variable to indicate if the user has logged in before based
    # on whether or not they have a public key.
    user_pk = user.listChildren(include=['public key'])
    if not len(user_pk):
        has_public_key = False
    else:
        has_public_key = True
    has_logged_in = pm.setVar('has_logged_in', has_public_key)

    pm.render_var['attribute_list'] = attribute.parse_attributes(user)
    subkey_list = []
    for subkey in user.listChildren(include=['sub key']):
        pw_key = subkey.password_key

        try:
            name = subkey.password_key.attributes.get('name')
            description = subkey.password_key.attributes.get('description')
        except Exception as e:
            pm.render_var['message'] = (
                'Failed to get name/description of subkey: {error}'
            ).format(
                error=str(e)
            )
            name = 'Unknown'
            description = ''
            pass

        subkey_list.append({
            'oid': subkey.oid,
            'exists': True,
            'subkey': subkey,
            'name': name,
            'description': description
        })

    # Sort the list of subkeys to easier find them
    sorted_subkey_list = sorted(
        subkey_list,
        key=lambda k: k['name']
    )

    pm.render_var['subkey_list'] = sorted_subkey_list
    pm.path(user)
    return pm.render()

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    user = pm.setVar('user', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/user/delete/post/%s/' % (user.oid),
            'remove user', message = 'Removing user.')
    pm.path(user)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    user = pm.object_store.getOID(oid)
    pm.addForm(DeleteForm(request.POST), '/user/delete/post/%s/' % (user.oid),
            'remove user', message = 'Removing user.')
    if not pm.form.is_valid():
        return pm.render()
    parent = user.parent
    user.delete()

    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    user = pm.setVar('user', pm.object_store.getOID(oid))
    form_data = {'user_name': user.username,
            'real_name': user.attributes.get('real_name', ''),
            'description': user.attributes.get('description', ''),
            'validate': '',
            'administrator': user.administrator}
    url = '/user/update/post/%s/' % (user.oid)
    if request.session['administrator']:
        pm.addForm(UserUpdateAdminForm(form_data), url, 'update user')
    else:
        pm.addForm(UserUpdateForm(form_data), url, 'update user')
    pm.path(user)
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    user = pm.object_store.getOID(oid)
    url = '/user/update/post/%s/' % (user.oid)
    if request.session['administrator']:
        pm.addForm(UserUpdateAdminForm(request.POST), url, 'update user')
    else:
        pm.addForm(UserUpdateForm(request.POST), url, 'update user')
    if not pm.form.is_valid():
        return pm.error()

    if pm.form.cleaned_data['user_name'] != user.username:
        user.setUsername(pm.form.cleaned_data['user_name'])
    if pm.form.cleaned_data['real_name'] != user.attributes.get('real_name', None):
        user.attributes['real_name'] = pm.form.cleaned_data['real_name']
    if pm.form.cleaned_data['description'] != user.attributes.get('description', None):
        user.attributes['description'] = pm.form.cleaned_data['description']
    if request.session['administrator']:
        if pm.form.cleaned_data['administrator'] != user.administrator:
            user.setAdministrator(pm.form.cleaned_data['administrator'])

    return pm.redirect('user.display', (oid,))

@helpers.authcheck
def reset_password(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    user = pm.setVar('user', pm.object_store.getOID(oid))
    url = '/user/password/reset/post/%s/' % (user.oid)
    pm.addForm(UserResetPasswordForm(), url, 'reset password')
    pm.path(user)
    return pm.render()

@helpers.authcheck
def reset_password_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    user = pm.object_store.getOID(oid)
    url = '/user/password/reset/post/%s/' % (user.oid)
    pm.addForm(UserResetPasswordForm(request.POST), url, 'reset password')
    if not pm.form.is_valid():
        return pm.error()
    new_password = pm.form.cleaned_data['password']
    new_password_verify = pm.form.cleaned_data['validate']
    if len(new_password) == 0:
        return pm.error('password to short')
    if new_password != new_password_verify:
        return pm.error('passwords don\'t match')
    user.resetPassword(new_password)
    return pm.redirect('user.display', (oid,))

@helpers.authcheck
def update_password(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    user = pm.setVar('user', pm.object_store.getOID(oid))
    url = '/user/password/update/post/%s/' % (user.oid)
    pm.addForm(UserUpdatePasswordForm(), url, 'reset password')
    pm.path(user)

    # The use of this form needs to be clearer
    ldap_warning = ('If using LDAP/AD user manager you must use this form '
                    'BEFORE you change your password in LDAP/AD. This form '
                    'will not update the LDAP/AD password but it will '
                    'reconnect all your subkeys to your new password to '
                    'prepare them for the password change that will happen '
                    'in the directory server.')
    pm.render_var['form']['message'] = ldap_warning

    return pm.render()

@helpers.authcheck
def update_password_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    user = pm.object_store.getOID(oid)
    url = '/user/password/update/post/%s/' % (user.oid)
    pm.addForm(UserUpdatePasswordForm(request.POST), url, 'update password')
    if not pm.form.is_valid():
        return pm.error()
    new_password = pm.form.cleaned_data['password']
    new_password_verify = pm.form.cleaned_data['validate']
    if len(new_password) == 0:
        return pm.error('password too short')
    if new_password != new_password_verify:
        return pm.error('passwords don\'t match')
    old_password = pm.form.cleaned_data['old_password']
    if not old_password:
        old_password = False
    try:
        user.setPassword(new_password, old_password)
    except siptracklib.errors.SiptrackError as e:
        pm.setVar('message', str(e))
        return pm.render()
    return pm.redirect('user.display', (oid,))

def _get_password_keys(view_tree):
    password_keys = []
    for view in view_tree.listChildren(include = ['view']):
        for password_key in view.listChildren(include = ['password key']):
            password_keys.append(password_key)
    return password_keys

@helpers.authcheck
def connectkey_selectkey(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    user = pm.object_store.getOID(oid)

    url = '/user/connectkey/post/%s/' % (oid)
    password_keys = _get_password_keys(pm.view_tree)
    require_user_password = True
    if pm.render_var['username'] == user.username:
        require_user_password = False
    form = UserConnectKeyForm(password_keys, require_user_password)
    pm.addForm(form, url, 'connect password key')
    pm.path(user)
    return pm.render()

@helpers.authcheck
def connectkey_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    user = pm.object_store.getOID(oid)

    url = '/user/connectkey/post/%s/' % (oid)
    password_keys = _get_password_keys(pm.view_tree)
    require_user_password = True
    if pm.render_var['username'] == user.username:
        require_user_password = False
    form = UserConnectKeyForm(password_keys, require_user_password, request.POST)
    pm.addForm(form, url, 'connect password key')
    pm.path(user)
    if not pm.form.is_valid():
        return pm.error()

    password_key = pm.object_store.getOID(pm.form.cleaned_data['passwordkey'])
    user_password = None
    if 'user_password' in pm.form.cleaned_data and \
            len(pm.form.cleaned_data['user_password']) > 0:
        user_password = pm.form.cleaned_data['user_password']
    password_key_key = None
    if len(pm.form.cleaned_data['password_key_key']) > 0:
        password_key_key = pm.form.cleaned_data['password_key_key']
    try:
        user.connectPasswordKey(password_key, user_password, password_key_key)
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))
    except Exception as e:
        raise

    return pm.redirect('user.display', (oid,))


@helpers.authcheck
def ajax_connectkey(request):
    if request.method != 'POST':
        return HttpResponseServerError(
            json.dumps({
                'error': 'Unsupported method'
            }),
            content_type='application/json'
        )

    pm = helpers.PageManager(request, '')
    password_key = pm.object_store.getOID(request.POST.get('passwordKeyOid'))
    user = pm.object_store.getOID(request.POST.get('userOid'))

    password_key_key = request.POST.get('passwordKeyPassword')
    user_password = request.POST.get('userPassword')

    try:
        user.connectPasswordKey(password_key, user_password, password_key_key)
    except siptracklib.errors.SiptrackError as e:
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
        })
    )


@helpers.authcheck
def subkey_delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    subkey = pm.setVar('subkey', pm.object_store.getOID(oid))
    user = subkey.parent
    pm.addForm(DeleteForm(), '/user/subkey/delete/post/%s/' % (oid),
            'remove subkey', message = 'Removing subkey.')
    pm.path(user)
    return pm.render()


@helpers.authcheck
def subkey_delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    subkey = pm.object_store.getOID(oid)
    user = subkey.parent
    pm.addForm(DeleteForm(request.POST), '/user/subkey/delete/post/%s/' % (oid),
            'remove subkey', message = 'Removing subkey.')
    if not pm.form.is_valid():
        return pm.render()
    subkey.delete()

    return pm.redirect('user.display', (user.oid,))


@helpers.authcheck
def ajax_subkey_delete(request):
    if request.method != 'POST':
        return HttpResponse(
            json.dumps({
                'error': 'Unsupported method'
            }),
            status=500,
            content_type='application/json'
        )

    pm = helpers.PageManager(request, '')
    oid = request.POST.get('subkeyOid')

    try:
        subkey = pm.object_store.getOID(oid)
    except siptracklib.errors.NonExistent as e:
        return HttpResponse(
            json.dumps({
                'error': 'Subkey not found'
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
        subkey.delete()
    except Exception as e:
        return HttpResponseServerError(
            json.dumps({
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
def session_kill(request, session_id):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    pm.addForm(DeleteForm(), '/user/session/kill/post/%s/' % (session_id),
            'kill session', message = 'Kill session.')
    pm.path(None)
    return pm.render()

@helpers.authcheck
def session_kill_post(request, session_id):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    pm.addForm(DeleteForm(request.POST), '/user/session/kill/post/%s/' % (session_id),
            'kill session', message = 'Kill session.')
    if not pm.form.is_valid():
        return pm.render()
    pm.object_store.killServerSession(session_id)

    return pm.redirect('user.index', ())

@helpers.authcheck
def manager_add(request, um_type):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    url = '/user/manager/add/post/%s/' % (um_type)
    if um_type == 'local':
        form = UserManagerLocalAddForm()
    elif um_type == 'ldap':
        form = UserManagerLDAPAddForm()
    elif um_type == 'ad':
        form = UserManagerActiveDirectoryAddForm()
    else:
        raise Exception('no')
    pm.addForm(form, url, 'add user manager')
    pm.path(None)
    return pm.render()

@helpers.authcheck
def manager_add_post(request, um_type):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    pm.path(None)

    url = '/user/manager/add/post/%s/' % (um_type)
    if um_type == 'local':
        form = UserManagerLocalAddForm(request.POST)
    elif um_type == 'ldap':
        form = UserManagerLDAPAddForm(request.POST)
    elif um_type == 'ad':
        form = UserManagerActiveDirectoryAddForm(request.POST)
    else:
        raise Exception('no')
    pm.addForm(form, url, 'add user manager')
    if not pm.form.is_valid():
        return pm.error()

    try:
        if um_type == 'local':
            um = pm.view_tree.add('user manager local')
        elif um_type == 'ldap':
            valid_groups = []
            if len(pm.form.cleaned_data.get('valid_groups', '')) > 0:
                valid_groups = [g.strip() for g in pm.form.cleaned_data['valid_groups'].split(':')]
            um = pm.view_tree.add('user manager ldap',
                pm.form.cleaned_data['connection_type'],
                pm.form.cleaned_data['server'],
                pm.form.cleaned_data['port'],
                pm.form.cleaned_data['base_dn'],
                valid_groups)
        elif um_type == 'ad':
            valid_groups = []
            if len(pm.form.cleaned_data.get('valid_groups', '')) > 0:
                valid_groups = [g.strip() for g in pm.form.cleaned_data['valid_groups'].split(':')]
            um = pm.view_tree.add('user manager active directory',
                pm.form.cleaned_data['server'],
                pm.form.cleaned_data['base_dn'],
                valid_groups,
                pm.form.cleaned_data['user_domain'])
        else:
            raise Exception('no')
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))
    um.attributes['name'] = pm.form.cleaned_data['name']
    um.attributes['description'] = pm.form.cleaned_data.get('description', '')

    return pm.redirect('display.display', (um.oid,))

@helpers.authcheck
def manager_update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    um = pm.object_store.getOID(oid)
    url = '/user/manager/update/post/%s/' % (oid)
    if um.class_name == 'user manager local':
        form_data = {'name': um.attributes.get('name', ''),
                'description': um.attributes.get('description', '')}
        pm.addForm(UserManagerLocalAddForm(form_data), url, 'update user manager')
    elif um.class_name == 'user manager ldap':
        valid_groups = ''
        if len(um.valid_groups) > 0:
            valid_groups = ':'.join(um.valid_groups[0])
        form_data = {'name': um.attributes.get('name', ''),
                'description': um.attributes.get('description', ''),
                'connection_type': um.connection_type,
                'server': um.server,
                'port': um.port,
                'base_dn': um.base_dn,
                'valid_groups': valid_groups,
                }
        pm.addForm(UserManagerLDAPAddForm(form_data), url, 'update user manager')
    elif um.class_name == 'user manager active directory':
        valid_groups = ''
        if len(um.valid_groups) > 0:
            valid_groups = ':'.join(um.valid_groups)
        form_data = {'name': um.attributes.get('name', ''),
                'description': um.attributes.get('description', ''),
                'server': um.server,
                'base_dn': um.base_dn,
                'valid_groups': valid_groups,
                'user_domain': um.user_domain,
                }
        pm.addForm(UserManagerActiveDirectoryAddForm(form_data), url, 'update user manager')
    else:
        raise Exception('no')
    pm.path(um)
    return pm.render()

@helpers.authcheck
def manager_update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    um = pm.object_store.getOID(oid)
    url = '/user/manager/update/post/%s/' % (oid)
    if um.class_name == 'user manager local':
        pm.addForm(UserManagerLocalAddForm(request.POST), url, 'update user manager')
    elif um.class_name == 'user manager ldap':
        pm.addForm(UserManagerLDAPAddForm(request.POST), url, 'update user manager')
    elif um.class_name == 'user manager active directory':
        pm.addForm(UserManagerActiveDirectoryAddForm(request.POST), url, 'update user manager')
    else:
        raise Exception('no')
    if not pm.form.is_valid():
        return pm.error()
    if um.class_name == 'user manager ldap':
        valid_groups = []
        if len(pm.form.cleaned_data.get('valid_groups', '')) > 0:
            valid_groups = [g.strip() for g in pm.form.cleaned_data['valid_groups'].split(':')]
        um.setValidGroups(valid_groups)
        if pm.form.cleaned_data['connection_type'] != um.connection_type:
            um.setConnectionType(pm.form.cleaned_data['connection_type'])
        if pm.form.cleaned_data['server'] != um.server:
            um.setServer(pm.form.cleaned_data['server'])
        if pm.form.cleaned_data['port'] != um.port:
            um.setPort(pm.form.cleaned_data['port'])
        if pm.form.cleaned_data['base_dn'] != um.base_dn:
            um.setBaseDN(pm.form.cleaned_data['base_dn'])
    if um.class_name == 'user manager active directory':
        valid_groups = []
        if len(pm.form.cleaned_data.get('valid_groups', '')) > 0:
            valid_groups = [g.strip() for g in pm.form.cleaned_data['valid_groups'].split(':')]
        um.setValidGroups(valid_groups)
        if pm.form.cleaned_data['server'] != um.server:
            um.setServer(pm.form.cleaned_data['server'])
        if pm.form.cleaned_data['base_dn'] != um.base_dn:
            um.setBaseDN(pm.form.cleaned_data['base_dn'])
        if pm.form.cleaned_data['user_domain'] != um.user_domain:
            um.setUserDomain(pm.form.cleaned_data['user_domain'])

    if pm.form.cleaned_data['name'] != um.attributes.get('name', None):
        um.attributes['name'] = pm.form.cleaned_data['name']
    if pm.form.cleaned_data['description'] != um.attributes.get('description', None):
        um.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def manager_delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    um = pm.object_store.getOID(oid)
    pm.addForm(DeleteForm(), '/user/manager/delete/post/%s/' % (oid),
            'remove user manager', message = 'Removing user manager.')
    pm.path(um)
    return pm.render()

@helpers.authcheck
def manager_delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    um = pm.object_store.getOID(oid)
    pm.addForm(DeleteForm(request.POST),
            '/user/manager/delete/post/%s/' % (oid),
            'remove user manager', message = 'Removing user manager.')
    if not pm.form.is_valid():
        return pm.render()
    try:
        um.delete()
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))

    return pm.redirect('user.index', ())

@helpers.authcheck
def group_display(request, oid):
    pm = helpers.PageManager(request, 'stweb/users/display_group.html')
    pm.section('user')

    group = pm.object_store.getOID(oid)
    pm.render_var['group'] = group
    pm.render_var['attribute_list'] = attribute.parse_attributes(group)
    pm.path(group)
    return pm.render()

@helpers.authcheck
def group_add(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    um = pm.object_store.getOID(oid)
    users = [(u.oid, u.username) for u in um.listUsers()]

    url = '/user/group/add/post/%s/' % (oid)
    pm.addForm(UserGroupAddForm(users), url, 'add user group')
    pm.path(um)
    return pm.render()

@helpers.authcheck
def group_add_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    um = pm.object_store.getOID(oid)
    pm.path(um)

    users = [(u.oid, u.username) for u in um.listUsers()]

    url = '/user/group/add/post/%s/' % (oid)
    pm.addForm(UserGroupAddForm(users, request.POST), url, 'add user group')
    if not pm.form.is_valid():
        return pm.error()

    form_users = [pm.object_store.getOID(u_oid) for u_oid in pm.form.cleaned_data['users']]

    group = um.add('user group', form_users)
    group.attributes['name'] = pm.form.cleaned_data['name']
    if 'description' in pm.form.cleaned_data and len(pm.form.cleaned_data['description']) > 0:
        group.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def group_delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    group = pm.setVar('group', pm.object_store.getOID(oid))
    pm.addForm(DeleteForm(), '/user/group/delete/post/%s/' % (group.oid),
            'remove group', message = 'Removing group.')
    pm.path(group)
    return pm.render()

@helpers.authcheck
def group_delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    group = pm.object_store.getOID(oid)
    pm.addForm(DeleteForm(request.POST), '/user/group/delete/post/%s/' % (group.oid),
            'remove group', message = 'Removing group.')
    if not pm.form.is_valid():
        return pm.render()
    parent = group.parent
    group.delete()

    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def group_update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    group = pm.setVar('user', pm.object_store.getOID(oid))
    um = group.parent
    all_users = [(u.oid, u.username) for u in um.listUsers()]
    group_users = [u.oid for u in group.users]
    form_data = {'name': group.attributes.get('name', ''),
            'description': group.attributes.get('description', ''),
            'users': group_users}
    url = '/user/group/update/post/%s/' % (group.oid)
    pm.addForm(UserGroupUpdateForm(all_users, form_data), url, 'update group')
    pm.path(group)
    return pm.render()

@helpers.authcheck
def group_update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    group = pm.object_store.getOID(oid)
    um = group.parent
    all_users = [(u.oid, u.username) for u in um.listUsers()]
    url = '/user/group/update/post/%s/' % (group.oid)
    pm.addForm(UserGroupUpdateForm(all_users, request.POST), url, 'update group')
    if not pm.form.is_valid():
        return pm.error()

    if pm.form.cleaned_data['name'] != group.attributes.get('name'):
        group.attributes['name'] = pm.form.cleaned_data['name']
    if pm.form.cleaned_data['description'] != group.attributes.get('description'):
        group.attributes['description'] = pm.form.cleaned_data['description']
    form_users = [pm.object_store.getOID(u_oid) for u_oid in pm.form.cleaned_data['users']]
    group.setUsers(form_users)

    return pm.redirect('display.display', (oid,))

