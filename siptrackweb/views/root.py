from django.http import HttpResponse
from django.template import Context, loader
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response                                 

import siptracklib.errors

import view
import helpers
from siptrackweb.forms import ViewSearchForm, LoginForm

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
    pm = helpers.PageManager(request, 'stweb/views/search_results.html')
    if 'searchstring' in request.GET:
        searchstring = request.GET['searchstring']
    else:
        pm.setForm(ViewSearchForm(request.POST))
        if not pm.form.is_valid():
            return pm.render()
        searchstring = pm.form.cleaned_data['searchstring']
    searchstring = searchstring.strip()
    searchresults = helpers.search(pm.object_store, searchstring)

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

