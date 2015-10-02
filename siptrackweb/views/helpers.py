import random
import subprocess
import json
import re

from django.shortcuts import render_to_response                                 
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseRedirect)
from django.conf import settings

import siptracklib
import siptracklib.errors
from siptrackweb import forms

def get_siptrack_server():
    if not getattr(settings, 'SIPTRACK_SERVER', None):
        raise Exception('SIPTRACK_SERVER missing from settings.py')
    if getattr(settings, 'SIPTRACK_USE_SSL', None) is None:
        use_ssl = True
    else:
        use_ssl = getattr(settings, 'SIPTRACK_USE_SSL')
    if getattr(settings, 'SIPTRACK_PORT', None) is None:
        if use_ssl:
            port = siptracklib.default_ssl_port
        else:
            port = siptracklib.default_port
    else:
        port = getattr(settings, 'SIPTRACK_PORT')
    return (settings.SIPTRACK_SERVER, port, use_ssl)

def valid_login(request, username, password):
    server, port, use_ssl = get_siptrack_server()
    try:
        st = siptracklib.connect(server, username, password, port = port,
                use_ssl = use_ssl)
    except siptracklib.errors.InvalidLoginError:
        return False
    request.session['st_session_id'] = st.transport.session_id
    request.session['username'] = username
    session_user = st.getSessionUser()
    request.session['administrator'] = session_user.administrator
    return True

def authcheck(func):
    def authwrapper(request, *args, **kwargs):
        server, port, use_ssl = get_siptrack_server()
        if 'st_session_id' in request.session:
            object_store = siptracklib.connect(server, port = port,
                    use_ssl = use_ssl,
                    session_id = request.session['st_session_id'])
            if object_store.transport.cmd.hello() == 1:
                request.object_store = object_store
                try:
                    return func(request, *args, **kwargs)
                except siptracklib.errors.PermissionDenied:
                    pm = PageManager(request, 'stweb/views/perm.html')
                    pm.render_var['request'] = request
                    pm.render_var['pm'] = pm
                    pm.render_var['referer'] = request.META.get('HTTP_REFERER', None)
                    return pm.render()
        function = 'siptrackweb.views.root.login'
        request.session['login_prev_url'] = request.get_full_path().encode('utf-8')
        if 'searchstring' in request.POST:
            request.session['login_prev_url'] = '%s?searchstring=%s' % (
                    request.session['login_prev_url'],
                    request.POST['searchstring'].encode('utf-8'))
        return HttpResponseRedirect(reverse(function, args = None))
    return authwrapper

class PageManager(object):
    def __init__(self, request, render_path, section = None):
        self.request = request
        server, port, use_ssl = get_siptrack_server()
        self.object_store = object_store = siptracklib.connect(server,
                port = port, use_ssl = use_ssl,
                session_id = request.session['st_session_id'])
        self.render_path = render_path
        self.render_var = {}
        self.forms = {}
        self.view_tree = self.object_store.view_tree
        self.render_var['view_list'] = \
            self.view_tree.listChildren(include = ['view'])
        self.render_var['searchform'] = forms.ViewSearchForm()
        self.render_var['username'] = request.session['username']
        self.render_var['administrator'] = request.session['administrator']
        self.render_var['write_access'] = True
        self.render_var['section'] = section
        
        if request.session.get('verbose', False) is True:
            self.render_var['verbose'] = True

        self.tagged_oid = None
        if request.session.get('tagged_oid') is not None:
            self._taggedOIDSetup(request.session.get('tagged_oid'))

    def _taggedOIDSetup(self, oid):
        try:
            target = self.object_store.getOID(oid)
        except siptracklib.errors.NonExistent:
            del self.request.session['tagged_oid']
            return
        self.render_var['tagged_oid'] = target
        self.render_var['tagged_oid_path'] = \
                make_browsable_path(target, 'view tree',
                        include_root = False)
#                make_browsable_path(target, 'device category',
        self.tagged_oid = target

    def error(self, message = '', path = None):
        if message in self.render_var:
            self.render_var['message'] = '%s %s' % (self.render_var['message'],
                    message)
        else:
            self.render_var['message'] = message
        return self.render(path)

    def setForm(self, form, form_name = 'form', validate = True):
        self.form = form
        self.render_var[form_name] = form

    def addForm(self, form_obj, action, title = 'form', submit = 'continue',
            method = 'POST', name = 'form', message = None, default = True,
            extraelements = '', display_hidden = False):
        form = {}
        form['form'] = form_obj
        form['action'] = action
        form['title'] = title
        form['submit'] = submit
        form['method'] = method
        form['name'] = name
        form['message'] = message
        form['extraelements'] = extraelements
        form['display_hidden'] = display_hidden
        if default:
            self.form = form_obj
        self.forms[name] = form
        self.render_var[name] = form

    def setVar(self, name, value):
        self.render_var[name] = value
        return value

    def section(self, section):
        self.render_var['section'] = section

    def render(self, path = None):
        if not path:
            path = self.render_path
        if self.request.session.get('error_msg') is not None:
            self.render_var['message'] = self.request.session['error_msg']
            del self.request.session['error_msg']
        return render_to_response(path, self.render_var)

    def renderJSON(self, data, http_headers = None):
        data = json.dumps(data, sort_keys=True, indent=2)
        try:
            http_response = HttpResponse(data, content_type='application/json')
        except TypeError:
            http_response = HttpResponse(data, mimetype='application/json')
        http_response['Cache-Control'] = 'max-age=0,no-cache,no-store'
        if http_headers:
            for key in http_headers:
                http_response[key] = http_headers[key]
        return http_response

    def renderDownload(self, data, filename):
        try:
            http_response = HttpResponse(data, content_type='application/octet-stream')
        except TypeError:
            http_response = HttpResponse(data, mimetype='application/octet-stream')
        http_response['Cache-Control'] = 'max-age=0,no-cache,no-store'
        http_response['Content-Disposition'] = 'attachment; filename=%s' % (filename)
        return http_response

    def redirect(self, function, args = None):
        function = 'siptrackweb.views.%s' % (function)
        return HttpResponseRedirect(reverse(function, args = args))

    def path(self, node):
        if node and node.class_name == 'view':
            self.render_var['current_view'] = node
        elif node:
            self.render_var['current_view'] = node.getParent('view')
        self.render_var['browsable_path'] = make_browsable_path(node)
        self.render_var['target'] = node
        # Check the targets class to see if we can automatically determine
        # what section we're currently in. Used for menu hilighting.
        if node and self.render_var['section'] is None:
            if node.class_name in ['view']:
                self.render_var['section'] = 'view'
            if node.class_name in ['device', 'device category', 'device tree']:
                self.render_var['section'] = 'device'
            elif node.class_name in ['counter', 'counter loop']:
                self.render_var['section'] = 'counter'
            elif node.class_name in ['network tree', 'ipv4 network',
                    'ipv4 network range', 'ipv6 network', 'ipv6 network range']:
                self.render_var['section'] = 'network'
            elif node.class_name in ['counter', 'counter loop']:
                self.render_var['section'] = 'counter'
            elif node.class_name in ['password key']:
                self.render_var['section'] = 'password'


def search(object_store, pattern):
    searchresults = {'devices': [], 'networks': [], 'device_categories': [],
            'resultcount': 0, 'singleresult': None}
    include = ['device', 'device category', 'ipv4 network', 'ipv6 network']
#    for result in object_store.view_tree.search(pattern, include = include):
    attr_limit = []
    for result in object_store.quicksearch(pattern, attr_limit = attr_limit, include = include, max_results=100):
        if result.class_name == 'device':
            searchresults['devices'].append(result)
        if result.class_name == 'device category':
            searchresults['device_categories'].append(result)
        if result.class_name in ['ipv4 network', 'ipv6 network']:
            searchresults['networks'].append(result)
        searchresults['resultcount'] += 1
        searchresults['singleresult'] = result
    return searchresults

def generate_password(pwgen_call = None):
    if not pwgen_call:
        pwgen_call = ['pwgen', '-s', '10', '1']
    try:
        pwd = subprocess.Popen(pwgen_call, stdout=subprocess.PIPE).communicate()[0]
    except:
        raise
        pwd = ''
    pwd = pwd.strip()
    return pwd

def make_browsable_path(node, end_parent = 'view tree', include_root = True):
    if type(end_parent) is not list:
        end_parent = [end_parent]
    ret = []
    # The object store has parent = None.
    while node and node.class_name not in end_parent:
        ent = {'path': None}
        if node.class_name == 'view':
            ent['path'] = '/view/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'counter':
            ent['path'] = '/counter/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'password key':
            ent['path'] = '/password/key/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'password category':
            ent['path'] = '/password/category/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'password tree':
            ent['path'] = '/password/%s/' % (node.oid)
            ent['name'] = '[passwords]'
        if node.class_name == 'device':
            ent['path'] = '/device/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
            ent['disabled'] = node.attributes.get('disabled', False)
        if node.class_name == 'device specification':
            ent['path'] = '/device/specification/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'device category':
            ent['path'] = '/device/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'device tree':
            ent['path'] = '/device/display/%s/' % (node.oid)
            ent['name'] = '[devices]'
        if node.class_name == 'device template':
            ent['path'] = '/template/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'network template':
            ent['path'] = '/template/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', node.class_name)
        if node.class_name == 'network tree':
            ent['path'] = '/network/display/%s/' % (node.oid)
            ent['name'] = '%s' % node.attributes.get('name', node.class_name)
        if node.class_name == 'ipv4 network':
            ent['path'] = '/network/display/%s/' % (node.oid)
            ent['name'] = '%s' % (node)
        if node.class_name == 'ipv4 network range':
            ent['path'] = '/network/range/display/%s/' % (node.oid)
            ent['name'] = '%s' % (node)
        if node.class_name == 'ipv6 network':
            ent['path'] = '/network/display/%s/' % (node.oid)
            ent['name'] = '%s' % (node)
        if node.class_name == 'ipv6 network range':
            ent['path'] = '/network/range/display/%s/' % (node.oid)
            ent['name'] = '%s' % (node)
        if node.class_name in ['user local', 'user ldap']:
            ent['path'] = '/user/display/%s/' % (node.oid)
            ent['name'] = node.username
        if node.class_name in ['user group']:
            ent['path'] = '/user/group/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', 'group')
        if node.class_name in ['user manager local', 'user manager ldap', 'user manager active directory']:
            ent['path'] = '/user/manager/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name', 'user manager')
            ret.insert(0, ent)
            ent = {'path': None}
            ent['path'] = '/user/'
            ent['name'] = 'users'
        if node.class_name in ['attribute', 'versioned attribute']:
            ent['path'] = '/display/%s/' % (node.oid)
            ent['name'] = node.name
        if node.class_name == 'command queue':
            ent['path'] = '/command/queue/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name')
        if node.class_name == 'command':
            ent['path'] = '/command/display/%s/' % (node.oid)
            ent['name'] = 'command'
        if node.class_name == 'event trigger':
            ent['path'] = '/event/trigger/display/%s/' % (node.oid)
            ent['name'] = node.attributes.get('name')
        if node.class_name == 'event trigger rule python':
            ent['path'] = '/event/trigger/rule/python/display/%s/' % (node.oid)
            ent['name'] = 'python rule'
        if node.class_name == 'device config':
            ent['path'] = '/device/config/%s/' % (node.oid)
            ent['name'] = node.name
        if ent['path'] != None:
            ret.insert(0, ent)
        node = node.parent
    if include_root:
        ent = {}
        ent['path'] = '/'
        ent['name'] = 'root'
        ret.insert(0, ent)
    return ret

def _letter_number_split(name):
    letter = name
    number = 0
    res = re.match('^(\D+)(\d+)', name)
    if res:
        letter, number = res.groups()
        try:
            number = int(number)
        except:
            number = 0
    return letter, number

def device_letter_number_sorter(x, y):
    x_letter, x_number = _letter_number_split(x.attributes.get('name', ''))
    y_letter, y_number = _letter_number_split(y.attributes.get('name', ''))
    ret = cmp(x_letter, y_letter)
    if ret == 0:
        ret = cmp(x_number, y_number)
    return ret

