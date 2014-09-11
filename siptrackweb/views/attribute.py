import textile

import siptracklib.errors

from siptrackweb.views import helpers
from siptrackweb.forms import *

def parse_attributes(obj):
    attr_list = {'standard': [], 'wikitext': [], 'large': []}
    for attr in obj.attributes:
        if attr.attributes.get('wikitext'):
            converted = textile.textile(attr.value.encode('utf-8'),
                    encoding = 'utf-8', output = 'utf-8')
            d = {'attribute': attr, 'converted': converted}
            attr_list['wikitext'].append(d)
        elif attr.attributes.get('large'):
            attr_list['large'].append(attr)
        else:
            attr_list['standard'].append(attr)
    return attr_list

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/attributes/display_self.html')

    attr = pm.setVar('attribute', pm.object_store.getOID(oid))
    pm.render_var['parent'] = attr
    pm.render_var['attribute_list'] = parse_attributes(attr)
    pm.path(attr)
    return pm.render()

@helpers.authcheck
def add_select(request, target_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    target = pm.object_store.getOID(target_oid)
    pm.path(target)

    form = AttributeAddSelectTypeForm()
    path = '/attribute/add/set/%s/' % (target_oid)
    pm.addForm(form, path, 'add attribute')

    return pm.render()

@helpers.authcheck
def add_set(request, target_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    target = pm.object_store.getOID(target_oid)
    pm.path(target)

    form = AttributeAddSelectTypeForm(request.POST)
    path = '/attribute/add/set/%s/' % (target_oid)
    pm.addForm(form, path, 'add attribute')
    if not form.is_valid():
        return pm.render()

    if form.cleaned_data['ruletype'] == 'text':
        form = AttributeAddTextForm()
    elif form.cleaned_data['ruletype'] == 'bool':
        form = AttributeAddBoolForm()
    elif form.cleaned_data['ruletype'] == 'int':
        form = AttributeAddIntForm()
    else:
        return pm.error('bad, invalid ruletype')
    path = '/attribute/add/post/%s/' % (target_oid)
    pm.addForm(form, path, 'add attribute')

    return pm.render()

@helpers.authcheck
def add_post(request, target_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    target = pm.object_store.getOID(target_oid)
    pm.path(target)

    ruletype = request.POST.get('ruletype', '')
    path = '/attribute/add/post/%s/' % (target_oid)
    if ruletype == 'text':
        form = AttributeAddTextForm(request.POST)
    elif ruletype == 'bool':
        form = AttributeAddBoolForm(request.POST)
    elif ruletype == 'int':
        form = AttributeAddIntForm(request.POST)
    else:
        return pm.error('bad, invalid ruletype')
    pm.addForm(form, path, 'add attribute')
    if not form.is_valid():
        return pm.error('')

    attr_name = form.cleaned_data['name']
    if ruletype == 'text':
        attr_value = form.cleaned_data['value']
        if form.cleaned_data['versions'] == 1:
            attr = target.add('attribute', attr_name, 'text', attr_value)
        else:
            attr = target.add('versioned attribute', attr_name, 'text',
                    attr_value, form.cleaned_data['versions'])
    elif ruletype == 'bool':
        attr_value = form.cleaned_data['value']
        if attr_value == 'true':
            attr_value = True
        else:
            attr_value = False
        if form.cleaned_data['versions'] == 1:
            attr = target.add('attribute', attr_name, 'bool', attr_value)
        else:
            attr = target.add('versioned attribute', attr_name, 'bool',
                    attr_value, form.cleaned_data['versions'])
    if ruletype == 'int':
        attr_value = form.cleaned_data['value']
        if form.cleaned_data['versions'] == 1:
            attr = target.add('attribute', attr_name, 'int', attr_value)
        else:
            attr = target.add('versioned attribute', attr_name, 'int',
                    attr_value, form.cleaned_data['versions'])
    if form.cleaned_data.get('wikitext', False):
         attr.attributes['wikitext'] = True
    if form.cleaned_data.get('large', False):
         attr.attributes['large'] = True
    if form.cleaned_data.get('hidden', False):
         attr.attributes['hidden'] = True

    return pm.redirect('display.display', (target_oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    attribute = pm.object_store.getOID(oid)
    pm.path(attribute.getParentNode())

    msg = ''
    if attribute.atype == 'text':
        args = {'value': attribute.value}
        if attribute.attributes.get('large') or \
                attribute.attributes.get('wikitext'):
            form = AttributeUpdateLargeTextForm(attribute)
        else:
            form = AttributeUpdateTextForm(args)
        if attribute.attributes.get('wikitext'):
            msg = 'Uses Textile wiki <a href="http://textism.com/tools/textile/">syntax</a>.'
    elif attribute.atype == 'bool':
        args = {'value': attribute.value}
        form = AttributeUpdateBoolForm(args)
    elif attribute.atype == 'int':
        args = {'value': attribute.value}
        form = AttributeUpdateIntForm(args)
    path = '/attribute/update/post/%s/' % (attribute.oid)
    pm.addForm(form, path, 'update attribute', message = msg)

    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    attribute = pm.object_store.getOID(oid)
    pm.path(attribute.getParentNode())

    if attribute.atype == 'text':
        if attribute.attributes.get('large') or \
                attribute.attributes.get('wikitext'):
            form = AttributeUpdateLargeTextForm(attribute, request.POST)
        else:
            form = AttributeUpdateTextForm(request.POST)
    elif attribute.atype == 'bool':
        form = AttributeUpdateBoolForm(request.POST)
    elif attribute.atype == 'int':
        form = AttributeUpdateIntForm(request.POST)
    if not form.is_valid():
        return pm.error('')

    attribute.value = form.cleaned_data['value']

    return pm.redirect('display.display', (attribute.parent.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, '')
    attribute = pm.object_store.getOID(oid)
    parent = attribute.parent
    attribute.delete()

    return pm.redirect('display.display', (parent.oid,))

