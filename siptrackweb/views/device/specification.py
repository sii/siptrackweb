import siptracklib.errors

from siptrackweb.views import helpers
from siptrackweb.forms import *

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/display.html')
    spec = pm.setVar('device_spec', pm.object_store.getOID(oid))
    pm.path(spec)

    pm.render_var['device_spec_combined_rule_list'] = spec.combinedRules()
    pm.render_var['device_spec_rule_list'] = spec.listChildren(include = ['device specification rule'])
    return pm.render()

@helpers.authcheck
def add(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/add.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.setForm(DeviceSpecAddForm(parent.findSpecifications()))
    return pm.render()

@helpers.authcheck
def add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/add.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    pm.setForm(DeviceSpecAddForm(parent.findSpecifications(), request.POST))
    if not pm.form.is_valid():
        return pm.error()

    inherits = None
    if pm.form.cleaned_data['inherits'] != '-1':
        inherits = pm.object_store.getOID(pm.form.cleaned_data['inherits'])

    spec = parent.add('device specification', inherits)

    spec.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        spec.attributes['description'] = pm.form.cleaned_data['description']
    spec.attributes['template_only'] = pm.form.cleaned_data['template']

    return pm.redirect('device.specification.display', (spec.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/delete.html')
    spec = pm.setVar('device_spec', pm.object_store.getOID(oid))
    pm.path(spec)

    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/delete.html')
    spec = pm.setVar('device_spec', pm.object_store.getOID(oid))
    pm.path(spec)

    parent = spec.parent
    spec.delete()

    return pm.redirect('device.display', (parent.oid,))

@helpers.authcheck
def rule_add_select_type(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/add_rule_select_type.html')
    spec = pm.setVar('device_spec', pm.object_store.getOID(parent_oid))
    pm.path(spec)

    pm.setForm(DeviceSpecRuleAddSelectTypeForm())
    return pm.render()

@helpers.authcheck
def rule_add_set_values(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/add_rule_set_values.html')
    spec = pm.setVar('device_spec', pm.object_store.getOID(parent_oid))
    pm.path(spec)
    view = spec.getParent('view')
    network_tree_list = view.listChildren(include = ['network tree'])

    form = DeviceSpecRuleAddSelectTypeForm(request.POST)
    if not form.is_valid():
        pm.setForm(form)
        return pm.error('', path = 'stweb/views/devices/specifications/add_rule_select_type.html')
    if form.cleaned_data['ruletype'] == 'text':
        pm.setForm(DeviceSpecRuleAddTextForm())
    elif form.cleaned_data['ruletype'] == 'fixed':
        pm.setForm(DeviceSpecRuleAddFixedForm())
    elif form.cleaned_data['ruletype'] == 'regmatch':
        pm.setForm(DeviceSpecRuleAddRegmatchForm())
    elif form.cleaned_data['ruletype'] == 'bool':
        pm.setForm(DeviceSpecRuleAddBoolForm())
    elif form.cleaned_data['ruletype'] == 'wikitext':
        pm.setForm(DeviceSpecRuleAddWikitextForm())
    elif form.cleaned_data['ruletype'] == 'networkrange':
        pm.setForm(DeviceSpecRuleAddNetworkrangeForm(network_tree_list))
    else:
        pm.error('bad, invalid ruletype')

    return pm.render()

@helpers.authcheck
def rule_add_post(request, parent_oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/add_rule_set_values.html')
    spec = pm.setVar('device_spec', pm.object_store.getOID(parent_oid))
    pm.path(spec)
    view = spec.getParent('view')
    network_tree_list = view.listChildren(include = ['network tree'])

    ruletype = request.POST.get('ruletype', '')
    if ruletype == 'text':
        pm.setForm(DeviceSpecRuleAddTextForm(request.POST))
    elif ruletype == 'fixed':
        pm.setForm(DeviceSpecRuleAddFixedForm(request.POST))
    elif ruletype == 'regmatch':
        pm.setForm(DeviceSpecRuleAddRegmatchForm(request.POST))
    elif ruletype == 'bool':
        pm.setForm(DeviceSpecRuleAddBoolForm(request.POST))
    elif ruletype == 'wikitext':
        pm.setForm(DeviceSpecRuleAddWikitextForm(request.POST))
    elif ruletype == 'networkrange':
        pm.setForm(DeviceSpecRuleAddNetworkrangeForm(network_tree_list,
                request.POST))
    else:
        return pm.error('bad, invalid ruletype')

    if not pm.form.is_valid():
        return pm.error('')

    if ruletype in ['text', 'bool', 'wikitext']:
        ruledata = ''
    elif ruletype in ['fixed', 'regmatch']:
        ruledata = pm.form.cleaned_data['value']
    elif ruletype in ['networkrange']:
        nt = pm.object_store.getOID(pm.form.cleaned_data['networktree'])
        range_start = pm.form.cleaned_data['rangestart']
        range_end = pm.form.cleaned_data['rangeend']
        ruledata = [nt, range_start, range_end]

    if ruletype == 'wikitext':
        ruletype = 'text'
        wikitext = True
    else:
        wikitext = False

    rule = spec.add('device specification rule',
            pm.form.cleaned_data['name'],
            ruletype, ruledata)
    if pm.form.cleaned_data['hidden'] == 'yes':
        rule.attributes['hidden'] = True
    if pm.form.cleaned_data.get('expansion', False) is False:
        rule.attributes['expansion'] = False
    else:
        rule.attributes['expansion'] = True
    if pm.form.cleaned_data.get('default', None) is not None:
        if pm.form.cleaned_data['default'] == 'true':
            rule.attributes['default'] = True
        else:
            rule.attributes['default'] = False
    if wikitext:
        rule.attributes['wikitext'] = True
    if len(pm.form.cleaned_data['description']) > 0:
        rule.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('device.specification.display', (spec.oid,))

@helpers.authcheck
def rule_delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/delete_rule.html')
    rule = pm.setVar('device_spec_rule', pm.object_store.getOID(oid))
    pm.path(rule.parent)

    return pm.render()

@helpers.authcheck
def rule_delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/views/devices/specifications/delete_rule.html')
    rule = pm.setVar('device_spec_rule', pm.object_store.getOID(oid))
    parent = rule.parent
    pm.path(parent)
    rule.delete()

    return pm.redirect('device.specification.display',(parent.oid,))


