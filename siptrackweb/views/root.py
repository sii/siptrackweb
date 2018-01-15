from django.http import HttpResponse
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

import siptracklib.errors

import view
import helpers
from siptrackweb.forms import ViewSearchForm, LoginForm, ViewAdvancedSearchForm


def login(request):
    render_var = {'form': None, 'errormsg': ''}
    if 'username' in request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        if helpers.valid_login(request, username, password):
            if 'login_prev_url' in request.session:
                url = request.session['login_prev_url']
                del request.session['login_prev_url']
                return HttpResponseRedirect(url)
            else:
                return view.index(request)
        else:
            render_var['errormsg'] = 'Invalid username/password.'
    render_var['form'] = LoginForm()
    return render_to_response('stweb/login.html', render_var)

@helpers.authcheck
def logout(request):
    pm = helpers.PageManager(request, '')
    pm.object_store.logout()
    return pm.redirect('root.login')

@helpers.authcheck
def index(request):
    return view.index(request)

def style(request):
    t = loader.get_template('stweb/style.css')
    c = Context({})
    try:
        return HttpResponse(t.render(c), content_type='text/css')
    except TypeError:
        return HttpResponse(t.render(c), mimetype='text/css')

def prototypejs(request):
    t = loader.get_template('stweb/prototype.js')
    c = Context({})
    try:
        return HttpResponse(t.render(c), content_type='application/x-javascript')
    except TypeError:
        return HttpResponse(t.render(c), mimetype='application/x-javascript')

@helpers.authcheck
def search(request):
    searchstring = None
    search_attribute = 'name'
    search_value = str()
    search_attributes = None
    search_attributes_list = []
    advanced_search = False
    display_types = []
    default_display_types = [
        'devices',
        'device categories',
        'passwords',
        'password categories',
        'networks'
    ]

    pm = helpers.PageManager(request, 'stweb/views/search_results.html')

    # Determine if we're using the advanced search form or not.
    if 'searchAttribute' in request.GET:
        pm.setForm(ViewAdvancedSearchForm(request.GET))
        advanced_search = True
    else:
        pm.setForm(ViewSearchForm(request.POST))

    if not pm.form.is_valid():
        return pm.render()

    if advanced_search:
        search_attribute = pm.form.cleaned_data['searchAttribute'].replace(' ', '_').lower()
        search_value = pm.form.cleaned_data['searchValue']
        search_attributes = pm.form.cleaned_data['attributesList']
        display_types = pm.form.cleaned_data['displayTypes']
    else:
        searchstring = pm.form.cleaned_data['searchstring']
        display_types = default_display_types

    if search_value:
        search_value = search_value.strip().lower()

    # Restrict number of attribute names we can show in the html table.
    if search_attributes:
        for attribute_name in search_attributes.split(',')[:5]:
            search_attributes_list.append(
                attribute_name.strip()
            )

    if searchstring:
        searchstring = searchstring.strip().lower()
        searchresults = helpers.search(pm.object_store, searchstring)
    else:
        searchstring = search_value.strip().lower()
        searchresults = helpers.search(
            pm.object_store,
            searchstring,
            [search_attribute]
        )

    # Go directly to the result for a single match.
    if searchresults['resultcount'] == 1:
        if searchresults['singleresult'].class_name == 'device':
            return pm.redirect('device.display',
                    (searchresults['singleresult'].oid,))
        if searchresults['singleresult'].class_name == 'device category':
            return pm.redirect('device.display',
                    (searchresults['singleresult'].oid,))
        if searchresults['singleresult'].class_name == 'ipv4 network':
            return pm.redirect('network.display',
                    (searchresults['singleresult'].oid,))

    pm.render_var['searchresults'] = searchresults
    pm.render_var['searchstring'] = searchstring
    pm.render_var['search_attribute'] = search_attribute
    pm.render_var['attributes_list'] = search_attributes_list
    pm.render_var['display_types'] = display_types

    pm.render_var['browsable_path'] = [{
        'name': 'Search results',
        'path': '/search/'
    }]

    return pm.render()

@helpers.authcheck
def toggle_verbose(request, oid):
    if 'verbose' in request.session:
        request.session['verbose'] = not request.session['verbose']
    else:
        request.session['verbose'] = True

    function = 'siptrackweb.views.display.display'
    return HttpResponseRedirect(reverse(function, args = (oid,)))

@helpers.authcheck
def tag_oid(request, oid):
    request.session['tagged_oid'] = oid
    function = 'siptrackweb.views.display.display'
    return HttpResponseRedirect(reverse(function, args = (oid,)))

@helpers.authcheck
def untag_oid(request, oid):
    if 'tagged_oid' in request.session:
        del request.session['tagged_oid']
    function = 'siptrackweb.views.display.display'
    return HttpResponseRedirect(reverse(function, args = (oid,)))

@helpers.authcheck
def relocate_tagged_oid(request, oid):
    pm = helpers.PageManager(request, '')
    target = request.session.get('tagged_oid')
    device1 = pm.object_store.getOID(target)
    device2 = pm.object_store.getOID(oid)

    try:
        device1.relocate(device2)
    except siptracklib.errors.SiptrackError, e:
        request.session['error_msg'] = 'relocation failed: %s' % (str(e))
    return pm.redirect('display.display', (oid,))

@helpers.authcheck
def dinfo(request):
    pm = helpers.PageManager(request, 'stweb/dinfo.html')
    pm.render_var['request'] = request
    pm.render_var['pm'] = pm
    return pm.render()

@helpers.authcheck
def p404(request):
    return render_to_response('404.html')

