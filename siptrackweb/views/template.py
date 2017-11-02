from django.http import JsonResponse

import siptracklib.errors
from siptracklib import device

from siptrackweb.views import helpers
from siptrackweb.forms import *
from siptrackweb.views import attribute
import siptracklib.template

def sort_rules(template):
    ret = {}
    for rule in template.combinedRules():
        if rule.class_id not in ret:
            ret[rule.class_id] = []
        if rule.parent != template:
            rule.inherited = True
        ret[rule.class_id].append(rule)
    return ret

@helpers.authcheck
def display(request, oid):
    pm = helpers.PageManager(request, 'stweb/templates/display.html')

    template = pm.setVar('template', pm.object_store.getOID(oid))
    pm.render_var['rules'] = sort_rules(template)
    pm.render_var['attribute_list'] = attribute.parse_attributes(template)
    if template.class_name == 'device template':
        if pm.tagged_oid and pm.tagged_oid.class_name in ['device category', 'device tree']:
            pm.render_var['valid_copy_target'] = True
    if template.class_name == 'network template':
        if pm.tagged_oid and pm.tagged_oid.class_name in ['network tree', 'ipv4 network', 'ipv6 network']:
            pm.render_var['valid_copy_target'] = True
    pm.path(template)
    return pm.render()


@helpers.authcheck
def export(request, oid):
    pm = helpers.PageManager(request, 'stweb/templates/display.html')

    template = pm.object_store.getOID(oid)
    sorted_rules = sort_rules(template)
    export_data = {}

    for (class_id, rules) in sorted_rules.items():
        if not len(rules):
            continue

        for rule in rules:
            export_data[rule.class_name] = []

            if rule.class_name == 'template rule text':
                export_data[rule.class_name].append({
                    'args': [
                        rule.attr_name,
                        rule.versions
                    ]
                })
        
            if rule.class_name == 'template rule fixed':
                export_data[rule.class_name].append({
                    'args': [
                        rule.attr_name,
                        rule.value,
                        rule.variable_expansion,
                        rule.versions
                    ]
                })
        
            if rule.class_name == 'template rule regmatch':
                export_data[rule.class_name].append({
                    'args': [
                        rule.attr_name,
                        rule.regexp,
                        rule.versions
                    ]
                })
        
            if rule.class_name == 'template rule bool':
                export_data[rule.class_name].append({
                    'args': [
                        rule.attr_name,
                        rule.default_value,
                        rule.versions
                    ]
                })
        
            if rule.class_name == 'template rule int':
                export_data[rule.class_name].append({
                    'args': [
                        rule.attr_name,
                        rule.default_value,
                        rule.versions
                    ]
                })
            
    response = JsonResponse(
        export_data,
        content_type='application/force-download'
    )
    response['Content-Disposition'] = 'attachment; filename={filename}'.format(
        filename='Template_{oid}.json'.format(
            oid=oid
        )
    )
    return response


@helpers.authcheck
def add(request, template_type, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    url = '/template/%s/add/post/%s/' % (template_type, parent.oid)
    if template_type == 'device':
        templates = siptracklib.template.suggest_templates(parent,
                'device template')
        form = DeviceTemplateAddForm(templates)
    elif template_type == 'network':
        templates = siptracklib.template.suggest_templates(parent,
                'network template')
        form = NetworkTemplateAddForm(templates)
    pm.addForm(form, url, 'add template')
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def add_post(request, template_type, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.path(parent)

    url = '/template/%s/add/post/%s/' % (template_type, parent.oid)
    if template_type == 'device':
        templates = siptracklib.template.suggest_templates(parent,
                'device template')
        form = DeviceTemplateAddForm(templates, request.POST)
    elif template_type == 'network':
        templates = siptracklib.template.suggest_templates(parent,
                'network template')
        form = NetworkTemplateAddForm(templates, request.POST)
    pm.addForm(form, url, 'add template')
    if not pm.form.is_valid():
        return pm.error()

    inherited_templates = [pm.object_store.getOID(oid) for oid in \
            pm.form.cleaned_data['inherited_templates']]
    if template_type == 'device':
        template = parent.add('device template',
                pm.form.cleaned_data['inheritance_only'],
                inherited_templates)
        template.attributes['device_creation'] = \
                pm.form.cleaned_data['device_creation']
    elif template_type == 'network':
        template = parent.add('network template',
                pm.form.cleaned_data['inheritance_only'],
                inherited_templates)
    template.attributes['name'] = pm.form.cleaned_data['name']
    if len(pm.form.cleaned_data['description']) > 0:
        template.attributes['description'] = pm.form.cleaned_data['description']

    return pm.redirect('display.display', (template.oid,))

@helpers.authcheck
def update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.object_store.getOID(oid)
    pm.path(template)

    form_data = {'name': template.attributes.get('name', ''),
        'description': template.attributes.get('description', ''),
        'inheritance_only': template.inheritance_only}
    url = '/template/update/post/%s/' % (oid)
    if template.class_name == 'device template':
        templates = siptracklib.template.suggest_templates(template.parent,
                'device template')
        form_data['device_creation'] = template.attributes.get('device_creation', False)
        form_data['inherited_templates'] = [t.oid for t in template.inherited_templates]
        form = DeviceTemplateUpdateForm(templates, form_data)
    elif template.class_name == 'network template':
        templates = siptracklib.template.suggest_templates(template.parent,
                'network template')
        form_data['inherited_templates'] = [t.oid for t in template.inherited_templates]
        form = NetworkTemplateUpdateForm(templates, form_data)
    pm.addForm(form, url, 'update template')
    return pm.render()

@helpers.authcheck
def update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.object_store.getOID(oid)
    pm.path(template)

    url = '/template/update/post/%s/' % (oid)
    if template.class_name == 'device template':
        templates = siptracklib.template.suggest_templates(template.parent,
                'device template')
        form = DeviceTemplateAddForm(templates, request.POST)
    elif template.class_name == 'network template':
        templates = siptracklib.template.suggest_templates(template.parent,
                'network template')
        form = NetworkTemplateAddForm(templates, request.POST)
    pm.addForm(form, url, 'update template')
    if not pm.form.is_valid():
        return pm.error()

    if pm.form.cleaned_data['name'] != template.attributes.get('name'):
        template.attributes['name'] = pm.form.cleaned_data['name']
    if pm.form.cleaned_data['description'] != template.attributes.get('description'):
        template.attributes['description'] = pm.form.cleaned_data['description']
    inherited_templates = [pm.object_store.getOID(oid) for oid in \
            pm.form.cleaned_data['inherited_templates']]
    it1 = set(template.inherited_templates)
    it2 = set(inherited_templates)
    if it1 != it2:
        template.setInheritedTemplates(inherited_templates)
    if pm.form.cleaned_data['inheritance_only'] != template.inheritance_only:
        template.setInheritanceOnly(pm.form.cleaned_data['inheritance_only'])
    if template.class_name == 'device template':
        if pm.form.cleaned_data['device_creation'] != template.attributes.get('device_creation'):
            template.attributes['device_creation'] = pm.form.cleaned_data['device_creation']

    return pm.redirect('display.display', (template.oid,))

@helpers.authcheck
def delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    template = pm.object_store.getOID(oid)
    pm.addForm(DeleteForm(), '/template/delete/post/%s/' % (template.oid),
            'remove template', message = 'Removing template.')
    pm.path(template)
    return pm.render()

@helpers.authcheck
def delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.object_store.getOID(oid)
    parent_oid = template.parent.oid
    pm.addForm(DeleteForm(request.POST), '/template/delete/post/%s/' % (template.oid),
            'remove template', message = 'Removing template.')
    if not pm.form.is_valid():
        return pm.render()
    template.delete()

    return pm.redirect('display.display', (parent_oid,))

@helpers.authcheck
def rule_add(request, rule_type, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))

    post_url = '/template/rule/%s/add/post/%s/' % (rule_type, parent_oid)
    if rule_type == 'password':
        view = parent.getParent('view')
        password_keys = view.listChildren(include = ['password key'])
        pm.addForm(TemplateRulePasswordAddForm(password_keys), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'subdevice':
        templates = [template for template in \
                siptracklib.template.suggest_templates(parent,
                    parent.class_name) \
                if template.attributes.get('device_creation', False) and \
                not template.inheritance_only]
        pm.addForm(TemplateRuleSubdeviceAddForm(templates), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'network':
        pm.addForm(TemplateRuleAssignNetworkAddForm(), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'text':
        pm.addForm(TemplateRuleTextAddForm(), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'fixed':
        pm.addForm(TemplateRuleFixedAddForm(), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'regmatch':
        pm.addForm(TemplateRuleRegmatchAddForm(), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'bool':
        pm.addForm(TemplateRuleBoolAddForm(), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'int':
        pm.addForm(TemplateRuleIntAddForm(), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'delattr':
        pm.addForm(TemplateRuleDeleteAttributeAddForm(), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'flushnodes':
        inc = [c.class_name for c in pm.object_store.object_registry.iterChildrenByName('device')]
        pm.addForm(TemplateRuleFlushNodesAddForm(inc), post_url,
                'add template rule', message = 'Adding template rule.')
    elif rule_type == 'flushassoc':
        inc = pm.object_store.object_registry.iterRegisteredClassNames()
        pm.addForm(TemplateRuleFlushAssociationsAddForm(inc), post_url,
                'add template rule', message = 'Adding template rule.')
    else:
        raise Exception('invalid rule type')
    pm.render_var['rule_type'] = rule_type
    pm.path(parent)
    return pm.render()

@helpers.authcheck
def rule_add_post(request, rule_type, parent_oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    parent = pm.setVar('parent', pm.object_store.getOID(parent_oid))
    pm.render_var['rule_type'] = rule_type
    pm.path(parent)

    post_url = '/template/rule/%s/add/post/%s/' % (rule_type, parent_oid)
    if rule_type == 'password':
        view = parent.getParent('view')
        password_keys = view.listChildren(include = ['password key'])
        pm.addForm(TemplateRulePasswordAddForm(password_keys, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        key = None
        if pm.form.cleaned_data['passwordkey'] != '__no-password-key__':
            key = pm.object_store.getOID(pm.form.cleaned_data['passwordkey'])
        rule = parent.add('template rule password',
                pm.form.cleaned_data['username'],
                pm.form.cleaned_data['passwd_description'],
                key)
    elif rule_type == 'subdevice':
        templates = [template for template in \
                siptracklib.template.suggest_templates(parent, parent.class_name)
                if template.attributes.get('device_creation', False)]
        pm.addForm(TemplateRuleSubdeviceAddForm(templates, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        template = None
        if pm.form.cleaned_data['template'] != 'none':
            template = pm.object_store.getOID(pm.form.cleaned_data['template'])
        rule = parent.add('template rule subdevice',
                pm.form.cleaned_data['num_devices'],
                template,
                pm.form.cleaned_data['sequence_offset'])
    elif rule_type == 'network':
        pm.addForm(TemplateRuleAssignNetworkAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule = parent.add('template rule assign network')
    elif rule_type == 'text':
        pm.addForm(TemplateRuleTextAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule = parent.add('template rule text',
                pm.form.cleaned_data['attr_name'],
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['wikitext'] is True:
            rule.attributes['wikitext'] = True
        if pm.form.cleaned_data['large'] is True:
            rule.attributes['large'] = True
        if pm.form.cleaned_data['hidden'] is True:
            rule.attributes['hidden'] = True
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule_type == 'fixed':
        pm.addForm(TemplateRuleFixedAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule = parent.add('template rule fixed',
                pm.form.cleaned_data['attr_name'],
                pm.form.cleaned_data['string_value'],
                pm.form.cleaned_data['variable_expansion'],
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule_type == 'regmatch':
        pm.addForm(TemplateRuleRegmatchAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule = parent.add('template rule regmatch',
                pm.form.cleaned_data['attr_name'],
                pm.form.cleaned_data['regexp'],
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule_type == 'bool':
        pm.addForm(TemplateRuleBoolAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        default = False
        if pm.form.cleaned_data['default'] == 'true':
            default = True
        rule = parent.add('template rule bool',
                pm.form.cleaned_data['attr_name'], default,
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule_type == 'int':
        pm.addForm(TemplateRuleIntAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        default = pm.form.cleaned_data['default']
        rule = parent.add('template rule int',
                pm.form.cleaned_data['attr_name'], default,
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule_type == 'delattr':
        pm.addForm(TemplateRuleDeleteAttributeAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule = parent.add('template rule delete attribute',
                pm.form.cleaned_data['attr_name'])
    elif rule_type == 'flushnodes':
        inc = [c.class_name for c in pm.object_store.object_registry.iterChildrenByName('device')]
        pm.addForm(TemplateRuleFlushNodesAddForm(inc, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule = parent.add('template rule flush nodes',
                pm.form.cleaned_data['include'],
                pm.form.cleaned_data['exclude'])
    elif rule_type == 'flushassoc':
        inc = pm.object_store.object_registry.iterRegisteredClassNames()
        pm.addForm(TemplateRuleFlushAssociationsAddForm(inc, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule = parent.add('template rule flush associations',
                pm.form.cleaned_data['include'],
                pm.form.cleaned_data['exclude'])
    else:
        raise Exception('invalid rule type')

    if 'description' in pm.form.cleaned_data and \
            pm.form.cleaned_data['description'] is not None and \
            len(pm.form.cleaned_data['description']) > 0:
        rule.attributes['description'] = pm.form.cleaned_data['description']
        # Rule attributes that have an exclude attribute will not be applied
        # anywhere.
        attr = rule.attributes.getObject('description')
        attr.attributes['exclude'] = True
    if 'priority' in pm.form.cleaned_data and pm.form.cleaned_data['priority'] is not None:
        rule.attributes['priority'] = pm.form.cleaned_data['priority']
    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def rule_update(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    rule = pm.object_store.getOID(oid)
    parent = pm.object_store.getOID(rule.parent.oid)

    post_url = '/template/rule/update/post/%s/' % (oid)
    initial = {'description': rule.attributes.get('description', ''),
               'priority': rule.attributes.get('priority', 10)}
    if rule.class_name == 'template rule password':
        view = rule.getParent('view')
        password_keys = view.listChildren(include = ['password key'])
        initial.update({'username': rule.username, 'passwd_description': rule.description})
        pm.addForm(TemplateRulePasswordAddForm(password_keys, initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule subdevice':
        templates = [template for template in \
                     siptracklib.template.suggest_templates(parent,
                                                            parent.class_name) \
                     if template.attributes.get('device_creation', False) and \
                     not template.inheritance_only]
        initial.update({
                   'num_devices': rule.num_devices,
                   'sequence_offset': rule.sequence_offset,
                   'template': rule.device_template})
        pm.addForm(TemplateRuleSubdeviceAddForm(templates, initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule assign network':
        pm.addForm(TemplateRuleAssignNetworkAddForm(initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule text':
        initial.update({
            'attr_name': rule.attr_name,
            'version': rule.versions,
            'hidden': rule.attributes.get('hidden', False),
            'important': rule.attributes.get('important', False),
            'large': rule.attributes.get('large', False),
            'wikitext': rule.attributes.get('wikitext', False),
        })
        pm.addForm(TemplateRuleTextAddForm(initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule fixed':
        initial.update({
            'attr_name': rule.attr_name,
            'string_value': rule.value,
            'variable_expansion': rule.variable_expansion,
            'important': rule.attributes.get('important', False),
            'versions': rule.versions,
        })
        pm.addForm(TemplateRuleFixedAddForm(initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule regmatch':
        initial.update({
            'attr_name': rule.attr_name,
            'regexp': rule.regexp,
            'versions': rule.versions,
        })
        pm.addForm(TemplateRuleRegmatchAddForm(initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule bool':
        initial.update({
            'attr_name': rule.attr_name,
            'default': rule.default_value,
            'versions': rule.versions,
            'important': rule.attributes.get('important', False),
        })
        pm.addForm(TemplateRuleBoolAddForm(initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule int':
        initial.update({
            'attr_name': rule.attr_name,
            'default': rule.default_value,
            'versions': rule.versions,
            'important': rule.attributes.get('important', False),
        })
        pm.addForm(TemplateRuleIntAddForm(initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule delete attribute':
        initial.update({
            'attr_name': rule.attr_name,
        })
        pm.addForm(TemplateRuleDeleteAttributeAddForm(initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule flush nodes':
        initial.update({
            'include': rule.include,
            'exclude': rule.exclude,
        })
        inc = [c.class_name for c in pm.object_store.object_registry.iterChildrenByName('device')]
        pm.addForm(TemplateRuleFlushNodesAddForm(inc, initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    elif rule.class_name == 'template rule flush associations':
        initial.update({
            'include': rule.include,
            'exclude': rule.exclude,
        })
        inc = pm.object_store.object_registry.iterRegisteredClassNames()
        pm.addForm(TemplateRuleFlushAssociationsAddForm(inc, initial=initial), post_url,
                   'update template rule', message = 'Update template rule.')
    else:
        raise Exception('invalid rule type')
    pm.path(rule)
    return pm.render()

@helpers.authcheck
def rule_update_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    rule = pm.object_store.getOID(oid)
    parent = rule.parent
    pm.path(rule)

    post_url = '/template/rule/update/post/%s/' % (oid)
    if rule.class_name == 'template rule password':
        view = parent.getParent('view')
        password_keys = view.listChildren(include = ['password key'])
        pm.addForm(TemplateRulePasswordAddForm(password_keys, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        key = None
        if pm.form.cleaned_data['passwordkey'] != '__no-password-key__':
            key = pm.object_store.getOID(pm.form.cleaned_data['passwordkey'])
        rule.delete()
        rule = parent.add('template rule password',
                pm.form.cleaned_data['username'],
                pm.form.cleaned_data['passwd_description'],
                key)
    elif rule.class_name == 'template rule subdevice':
        templates = [template for template in \
                siptracklib.template.suggest_templates(parent, parent.class_name)
                if template.attributes.get('device_creation', False)]
        pm.addForm(TemplateRuleSubdeviceAddForm(templates, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        template = None
        if pm.form.cleaned_data['template'] != 'none':
            template = pm.object_store.getOID(pm.form.cleaned_data['template'])
        rule.delete()
        rule = parent.add('template rule subdevice',
                pm.form.cleaned_data['num_devices'],
                template,
                pm.form.cleaned_data['sequence_offset'])
    elif rule.class_name == 'template rule assign network':
        pm.addForm(TemplateRuleAssignNetworkAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule.delete()
        rule = parent.add('template rule assign network')
    elif rule.class_name == 'template rule text':
        pm.addForm(TemplateRuleTextAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule.delete()
        rule = parent.add('template rule text',
                pm.form.cleaned_data['attr_name'],
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['wikitext'] is True:
            rule.attributes['wikitext'] = True
        if pm.form.cleaned_data['large'] is True:
            rule.attributes['large'] = True
        if pm.form.cleaned_data['hidden'] is True:
            rule.attributes['hidden'] = True
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule.class_name == 'template rule fixed':
        pm.addForm(TemplateRuleFixedAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule.delete()
        rule = parent.add('template rule fixed',
                pm.form.cleaned_data['attr_name'],
                pm.form.cleaned_data['string_value'],
                pm.form.cleaned_data['variable_expansion'],
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule.class_name == 'template rule regmatch':
        pm.addForm(TemplateRuleRegmatchAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule.delete()
        rule = parent.add('template rule regmatch',
                pm.form.cleaned_data['attr_name'],
                pm.form.cleaned_data['regexp'],
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule.class_name == 'template rule bool':
        pm.addForm(TemplateRuleBoolAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        default = False
        if pm.form.cleaned_data['default'] == 'true':
            default = True
        rule.delete()
        rule = parent.add('template rule bool',
                pm.form.cleaned_data['attr_name'], default,
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule.class_name == 'template rule int':
        pm.addForm(TemplateRuleIntAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        default = pm.form.cleaned_data['default']
        rule.delete()
        rule = parent.add('template rule int',
                pm.form.cleaned_data['attr_name'], default,
                pm.form.cleaned_data['versions'])
        if pm.form.cleaned_data['important'] is True:
            rule.attributes['important'] = True
    elif rule.class_name == 'template rule delete attribute':
        pm.addForm(TemplateRuleDeleteAttributeAddForm(request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule.delete()
        rule = parent.add('template rule delete attribute',
                pm.form.cleaned_data['attr_name'])
    elif rule.class_name == 'template rule flush nodes':
        inc = [c.class_name for c in pm.object_store.object_registry.iterChildrenByName('device')]
        pm.addForm(TemplateRuleFlushNodesAddForm(inc, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule.delete()
        rule = parent.add('template rule flush nodes',
                pm.form.cleaned_data['include'],
                pm.form.cleaned_data['exclude'])
    elif rule.class_name == 'template rule flush associations':
        inc = pm.object_store.object_registry.iterRegisteredClassNames()
        pm.addForm(TemplateRuleFlushAssociationsAddForm(inc, request.POST),
                post_url,
                'add template rule', message = 'Adding template rule.')
        if not pm.form.is_valid():
            return pm.error()
        rule.delete()
        rule = parent.add('template rule flush associations',
                pm.form.cleaned_data['include'],
                pm.form.cleaned_data['exclude'])
    else:
        raise Exception('invalid rule type')

    if 'description' in pm.form.cleaned_data and \
            pm.form.cleaned_data['description'] is not None and \
            len(pm.form.cleaned_data['description']) > 0:
        rule.attributes['description'] = pm.form.cleaned_data['description']
        # Rule attributes that have an exclude attribute will not be applied
        # anywhere.
        attr = rule.attributes.getObject('description')
        attr.attributes['exclude'] = True
    if 'priority' in pm.form.cleaned_data and pm.form.cleaned_data['priority'] is not None:
        rule.attributes['priority'] = pm.form.cleaned_data['priority']
    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def rule_delete(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')

    rule = pm.object_store.getOID(oid)
    pm.addForm(DeleteForm(), '/template/rule/delete/post/%s/' % (oid),
            'remove template rule', message = 'Removing template rule.')
    pm.path(rule.parent)
    return pm.render()

@helpers.authcheck
def rule_delete_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    rule = pm.object_store.getOID(oid)
    parent = rule.parent
    pm.addForm(DeleteForm(request.POST), '/template/rule/delete/post/%s/' % (oid),
            'remove template rule', message = 'Removing template rule.')
    if not pm.form.is_valid():
        return pm.render()
    rule.delete()

    return pm.redirect('display.display', (parent.oid,))

@helpers.authcheck
def apply_select(request, target_oid, template_type):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    target = pm.object_store.getOID(target_oid)
    pm.path(target)

    if target.class_name in ['device']:
        templates = [template for template in \
                siptracklib.template.suggest_templates(target, 'device template')
                if not template.attributes.get('device_creation', False) and not template.inheritance_only]
    elif target.class_name in ['ipv4 network', 'ipv6 network']:
        templates = siptracklib.template.suggest_templates(target, 'network template')
    url = '/template/apply/set/%s/%s/' % (target_oid, template_type)
    pm.addForm(TemplateSelectForm(templates, False), url, 'apply template')
    return pm.render()

@helpers.authcheck
def apply_set(request, target_oid, template_type):
    pm = helpers.PageManager(request, 'stweb/templates/apply_set.html')
    target = pm.object_store.getOID(target_oid)
    pm.path(target)

    if target.class_name in ['device']:
        templates = [template for template in \
                siptracklib.template.suggest_templates(target, 'device template')
                if not template.attributes.get('device_creation', False) and not template.inheritance_only]
    elif target.class_name in ['ipv4 network']:
        templates = siptracklib.template.suggest_templates(target, 'network template')
    form = TemplateSelectForm(templates, False, request.POST)
    if not form.is_valid():
        url = '/template/apply/set/%s/%s/' % (target_oid, template_type)
        pm.addForm(form, url, 'apply template')
        return pm.render()

    template = pm.object_store.getOID(form.cleaned_data['template'])
    pm.render_var['template'] = template
    url = '/template/apply/post/%s/%s/' % (target_oid, template.oid)
    form = TemplateSetForm(template)
    pm.addForm(form, url, 'apply template')
    return pm.render()

@helpers.authcheck
def apply_post(request, target_oid, template_oid):
    pm = helpers.PageManager(request, 'stweb/templates/apply_set.html')
    target = pm.object_store.getOID(target_oid)
    pm.path(target)

    template = pm.object_store.getOID(template_oid)
    pm.render_var['template'] = template

    url = '/template/apply/post/%s/%s/' % (target_oid, template.oid)
    form = TemplateSetForm(template, request.POST)
    pm.addForm(form, url, 'create apply template')
    if not pm.form.is_valid():
        return pm.error('')

    apply_rules = []
    for key, value in request.POST.iteritems():
        if not key.startswith('apply-argument'):
            continue
        _, _, rule_oid = key.split('-')
        apply_rules.append(rule_oid)

    arguments = {}
    for key in pm.form.cleaned_data:
        if not key.startswith('argument-'):
            continue
        prefix, rule_oid = key.split('-', 1)
        arguments[rule_oid] = [pm.form.cleaned_data[key]]

    skip_rules = []
    for rule in template.combinedRules():
        if rule.oid not in apply_rules:
            skip_rules.append(rule.oid)
        if rule.apply_arguments == 0 and rule.oid in arguments:
            del arguments[rule.oid]
        if rule.class_name == 'template rule password':
            arguments[rule.oid] = [helpers.generate_password()]
        if rule.class_name == 'template rule subdevice':
            arguments[rule.oid] = [{}, arguments[rule.oid][0]]

    overwrite = True
    try:
        template.apply(target, arguments, overwrite, skip_rules)
    except siptracklib.errors.SiptrackError, e:
        return pm.error(str(e))

    return pm.redirect('display.display', (target.oid,))

@helpers.authcheck
def copy(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.setVar('template', pm.object_store.getOID(oid))
    url = '/template/copy/post/%s/' % (template.oid)
    pm.addForm(EmptyForm(), url,
            'copy tempate', message = 'Copying template.')
    pm.path(template)

    return pm.render()

@helpers.authcheck
def copy_post(request, oid):
    pm = helpers.PageManager(request, 'stweb/generic_form.html')
    template = pm.setVar('template', pm.object_store.getOID(oid))
    pm.path(template)
    url = '/template/copy/post/%s/' % (template.oid)
    pm.addForm(EmptyForm(request.POST), url,
            'copy template', message = 'Copying template.')
    if not pm.form.is_valid():
        return pm.render()
    new_template = template.copy(pm.tagged_oid)

    return pm.redirect('template.display', (new_template.oid,))

