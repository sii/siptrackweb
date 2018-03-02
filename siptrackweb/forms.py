from django import forms

class EmptyForm(forms.Form):
    pass

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        label='Username'
    )
    password = forms.CharField(
        max_length=32,
        label='Password',
        widget=forms.PasswordInput(),
        required=True
    )

class DeleteForm(forms.Form):
    verify = forms.CharField(
        initial='true',
        widget=forms.HiddenInput()
    )

class ConfirmForm(forms.Form):
    verify = forms.CharField(
        initial='true',
        widget=forms.HiddenInput()
    )

class ViewAddForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )

class ViewUpdateForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )

class ViewSearchForm(forms.Form):
    searchstring = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'id': 'searchbox'})
    )


class ViewAdvancedSearchForm(forms.Form):
    searchAttribute = forms.CharField(
        max_length=50,
        required=True
    )

    searchValue = forms.CharField(
        max_length=50,
        required=False
    )

    attributesList = forms.CharField(
        max_length=256,
        required=False
    )

    OPTIONS = (
        ('devices', 'devices'),
        ('device categories', 'device categories'),
        ('passwords', 'passwords'),
        ('password categories', 'password categories'),
        ('networks', 'networks')
    )

    displayTypes = forms.MultipleChoiceField(
        choices=OPTIONS,
        required=False
    )

class NetworkTreeAddForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    protocol = forms.ChoiceField(
        label='Protocol',
        choices=(('ipv4', 'ipv4'), ('ipv6', 'ipv6'))
    )

class NetworkAddForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Address',
        help_text='The network/address in CIDR form (x.x.x.x or x.x.x.x/xx)'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )

class NetworkRangeAddForm(forms.Form):
    range = forms.CharField(
        max_length=50,
        label='Range'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )

class NetworkDeleteForm(forms.Form):
    recursive = forms.BooleanField(
        label='Recursive delete',
        required=False
    )

class PasswordKeyAddForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    key = forms.CharField(
        max_length=32,
        label='Key',
        widget=forms.PasswordInput(),
        required=False
    )
    validate = forms.CharField(
        max_length=32,
        label='Key (again)',
        widget=forms.PasswordInput(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )

class CounterAddBasicForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )

class CounterAddLoopingForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )
    values = forms.CharField(
        max_length=5000,
        label='Values',
        help_text='one value per row',
        widget=forms.Textarea(attrs={'cols':'30', 'rows': '5'})
    )

class CounterUpdateBasicForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )
    value = forms.DecimalField(
        min_value=0,
        decimal_places=0,
        label='Value'
    )

class CounterUpdateLoopingForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name'
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )
    value = forms.CharField(
        max_length=50,
        label='Value'
    )
    values = forms.CharField(
        max_length=5000,
        label='Values',
        help_text='one value per row',
        widget=forms.Textarea(attrs={'cols':'30', 'rows': '5'})
    )

class CounterSetForm(forms.Form):
    value = forms.DecimalField(
        min_value=0,
        decimal_places=0,
        label='Value'
    )

class PasswordAddForm(forms.Form):
    pw_username = forms.CharField(
        max_length=50,
        label='Username',
        required=False
    )
    pw_password = forms.CharField(
        max_length=250,
        label='Password',
        widget=forms.PasswordInput(),
        required=False,
        help_text='Max length: 250, leave empty for generated password.'
    )
    validate = forms.CharField(
        max_length=250,
        label='Password (again)',
        widget=forms.PasswordInput(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False,
        label='Description'
    )

    def __init__(self, password_keys, *args, **kwargs):
        super(PasswordAddForm, self).__init__(*args, **kwargs)
        keylist = [('__no-password-key__', 'None')]
        for key in password_keys:
            value = (key.oid, key.attributes['name'])
            if key.attributes.get('default', False) is True:
                keylist.insert(0, value)
            else:
                keylist.append(value)
        field = forms.ChoiceField(
            label='Password key',
            choices=keylist
        )
        self.fields['passwordkey'] = field

class PasswordUpdateForm(forms.Form):
    pw_username = forms.CharField(max_length = 50, label = 'Username',
            required = False)
    pw_password = forms.CharField(max_length = 250, label = 'Password',
            widget = forms.PasswordInput(), required = False,
            help_text = 'Max length: 250, leave empty for generated password.')
    validate = forms.CharField(max_length = 250, label = 'Password (again)',
            widget = forms.PasswordInput(), required = False)
    description = forms.CharField(max_length = 100, required = False,
            label = 'Description')

    def __init__(self, password_keys, *args, **kwargs):
        super(PasswordUpdateForm, self).__init__(*args, **kwargs)
        keylist = [('__no-password-key__', 'None')]
        for key in password_keys:
            value = (key.oid, key.attributes['name'])
            if key.attributes.get('default', False) is True:
                keylist.insert(0, value)
            else:
                keylist.append(value)
        field = forms.ChoiceField(label = 'Password key', choices = keylist)
        self.fields['passwordkey'] = field

class DeviceTemplateAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this template.', required = False)
    inheritance_only = forms.BooleanField(label = 'Inheritance only',
            required = False,
            initial = False,
            help_text = 'Template is used for inheritance only.')
    device_creation = forms.BooleanField(label = 'Device creation',
            required = False,
            initial = False,
            help_text = 'Template is used for device creation.')

    def __init__(self, templates, *args, **kwargs):
        super(DeviceTemplateAddForm, self).__init__(*args, **kwargs)
        choices = []
        for template in templates:
            choices.append((template.oid,
                template.attributes.get('name', '[UKNOWN]')))
        field = forms.MultipleChoiceField(required = False,
                label = 'Inherited templates',
                choices = choices)
        self.fields['inherited_templates'] = field

class NetworkTemplateAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this template.', required = False)
    inheritance_only = forms.BooleanField(label = 'Inheritance only',
            required = False,
            initial = False,
            help_text = 'Template is used for inheritance only.')


    def __init__(self, templates, *args, **kwargs):
        super(NetworkTemplateAddForm, self).__init__(*args, **kwargs)
        choices = []
        for template in templates:
            choices.append((template.oid,
                template.attributes.get('name', '[UKNOWN]')))
        field = forms.MultipleChoiceField(required = False,
                label = 'Inherited templates',
                choices = choices)
        self.fields['inherited_templates'] = field

class DeviceTemplateUpdateForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this template.', required = False)
    inheritance_only = forms.BooleanField(label = 'Inheritance only',
            required = False,
            initial = False,
            help_text = 'Template is used for inheritance only.')
    device_creation = forms.BooleanField(label = 'Device creation',
            required = False,
            initial = False,
            help_text = 'Template is used for device creation.')

    def __init__(self, templates, *args, **kwargs):
        super(DeviceTemplateUpdateForm, self).__init__(*args, **kwargs)
        choices = []
        for template in templates:
            choices.append((template.oid,
                template.attributes.get('name', '[UKNOWN]')))
        field = forms.MultipleChoiceField(required = False,
                label = 'Inherited templates',
                choices = choices)
        self.fields['inherited_templates'] = field

class NetworkTemplateUpdateForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this template.', required = False)
    inheritance_only = forms.BooleanField(label = 'Inheritance only',
            required = False,
            initial = False,
            help_text = 'Template is used for inheritance only.')

    def __init__(self, templates, *args, **kwargs):
        super(NetworkTemplateUpdateForm, self).__init__(*args, **kwargs)
        choices = []
        for template in templates:
            choices.append((template.oid,
                template.attributes.get('name', '[UKNOWN]')))
        field = forms.MultipleChoiceField(required = False,
                label = 'Inherited templates',
                choices = choices)
        self.fields['inherited_templates'] = field

class TemplateRuleTextAddForm(forms.Form):
    attr_name = forms.CharField(max_length = 50, label = 'Attribute name',
            help_text = 'Name of attribute to create.')
    hidden = forms.BooleanField(label = 'Hide attribute',
                                required = False,
                                initial = False,
                                help_text = 'If true, the attribute will hidden per default if it is large/wikitext.')
    important = forms.BooleanField(label = 'Important attribute',
            required = False,
            initial = False,
            help_text = 'If true, the attribute will be displayed on the device/entity overview page.')
    large = forms.BooleanField(label = 'Large attribute',
            required = False,
            initial = False,
            help_text = 'If true, the attribute will have a separate display box.')
    wikitext = forms.BooleanField(label = 'Wikitext attribute',
            required = False,
            initial = False,
            help_text = 'If true, the attribute will be displayed using wikitext parsing, implies "large".')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')
    versions = forms.IntegerField(label = 'Versions',
            min_value = 1, initial = 1,
            help_text = 'Number of stored versions of the attribute.')

class TemplateRuleFixedAddForm(forms.Form):
    attr_name = forms.CharField(max_length = 50, label = 'Attribute name',
            help_text = 'Name of attribute to create.')
    string_value = forms.CharField(max_length = 100, label = 'String value',
            help_text = 'The created attributes value.')
    variable_expansion = forms.BooleanField(label = 'Expand variables',
            required = False,
            initial = False)
    important = forms.BooleanField(label = 'Important attribute',
                                   required = False,
                                   initial = False,
                                   help_text = 'If true, the attribute will be displayed on the device/entity overview page.')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')
    versions = forms.IntegerField(label = 'Versions',
            min_value = 1, initial = 1,
            help_text = 'Number of stored versions of the attribute.')

class TemplateRuleRegmatchAddForm(forms.Form):
    attr_name = forms.CharField(max_length = 50, label = 'Attribute name',
            help_text = 'Name of attribute to create.')
    regexp = forms.CharField(max_length = 50, label = 'Regexp',
            help_text = 'Regular expression that must match the input value.')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    versions = forms.IntegerField(label = 'Versions',
            min_value = 1, initial = 1,
            help_text = 'Number of stored versions of the attribute.')
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')
    important = forms.BooleanField(label = 'Important attribute',
                                   required = False,
                                   initial = False,
                                   help_text = 'If true, the attribute will be displayed on the device/entity overview page.')

class TemplateRuleBoolAddForm(forms.Form):
    attr_name = forms.CharField(max_length = 50, label = 'Attribute name',
            help_text = 'Name of attribute to create.')
    default = forms.ChoiceField(label = 'Default',
            choices = (('true', 'True'), ('false', 'False')),
            help_text = 'Default value for attribute.')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    versions = forms.IntegerField(label = 'Versions',
            min_value = 1, initial = 1,
            help_text = 'Number of stored versions of the attribute.')
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')
    important = forms.BooleanField(label = 'Important attribute',
                                   required = False,
                                   initial = False,
                                   help_text = 'If true, the attribute will be displayed on the device/entity overview page.')

class TemplateRuleIntAddForm(forms.Form):
    attr_name = forms.CharField(max_length = 50, label = 'Attribute name',
            help_text = 'Name of attribute to create.')
    default = forms.IntegerField(label = 'Default',
            initial = 0,
            help_text = 'Default value.')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    versions = forms.IntegerField(label = 'Versions',
            min_value = 1, initial = 1,
            help_text = 'Number of stored versions of the attribute.')
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')
    important = forms.BooleanField(label = 'Important attribute',
                                   required = False,
                                   initial = False,
                                   help_text = 'If true, the attribute will be displayed on the device/entity overview page.')

class TemplateRuleDeleteAttributeAddForm(forms.Form):
    attr_name = forms.CharField(max_length = 50, label = 'Attribute name',
            help_text = 'Name of attribute to delete.')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')

class TemplateRuleFlushNodesAddForm(forms.Form):
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')

    def __init__(self, node_types, *args, **kwargs):
        super(TemplateRuleFlushNodesAddForm, self).__init__(*args, **kwargs)
        choices = []
        for node_type in node_types:
            choices.append((node_type, node_type))
        field = forms.MultipleChoiceField(required = False,
                label = 'Included node types',
                choices = choices,
                help_text = 'If no node types are chosen for include, all types will match.')
        self.fields['include'] = field
        field = forms.MultipleChoiceField(required = False,
                label = 'Excluded node types',
                choices = choices)
        self.fields['exclude'] = field

class TemplateRuleFlushAssociationsAddForm(forms.Form):
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')

    def __init__(self, node_types, *args, **kwargs):
        super(TemplateRuleFlushAssociationsAddForm, self).__init__(*args, **kwargs)
        choices = []
        for node_type in node_types:
            choices.append((node_type, node_type))
        field = forms.MultipleChoiceField(required = False,
                label = 'Included node types',
                choices = choices,
                help_text = 'If no node types are chosen for include, all types will match.')
        self.fields['include'] = field
        field = forms.MultipleChoiceField(required = False,
                label = 'Excluded node types',
                choices = choices)
        self.fields['exclude'] = field

class TemplateRulePasswordAddForm(forms.Form):
    username = forms.CharField(max_length = 50, label = 'Username',
            required = False)
    passwd_description = forms.CharField(max_length = 50, label = 'Description',
            required = False, help_text = 'Description of the added password.')
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')

    def __init__(self, password_keys, *args, **kwargs):
        super(TemplateRulePasswordAddForm, self).__init__(*args, **kwargs)
        keylist = [('__no-password-key__', 'None')]
        for key in password_keys:
            keylist.append((key.oid, key.attributes['name']))
        field = forms.ChoiceField(label = 'Password key', choices = keylist)
        self.fields['passwordkey'] = field

class TemplateRuleSubdeviceAddForm(forms.Form):
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    num_devices = forms.IntegerField(label = 'Number of subdevices',
            min_value = 1, initial = 1,
            help_text = 'Number of subdevices to create.')
    sequence_offset = forms.IntegerField(label = 'Sequence offset',
            initial = 0,
            help_text = 'Base offset of sequence counter used when applying subdevice templates.')
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')

    def __init__(self, templates, *args, **kwargs):
        super(TemplateRuleSubdeviceAddForm, self).__init__(*args, **kwargs)
        templatelist = [('none', 'None')]
        for template in templates:
            templatelist.append((template.oid, template.attributes['name']))
        field = forms.ChoiceField(label = 'Template', choices = templatelist)
        self.fields['template'] = field

class TemplateRuleAssignNetworkAddForm(forms.Form):
    description = forms.CharField(max_length = 80, label = 'Description',
            help_text = 'Description of this rule.', required = False)
    priority = forms.IntegerField(label = 'Priority',
                                  min_value = 0, initial = 10,
                                  help_text = 'The priority of this rule when using the templates, lower value will be displayed first.')

class NetworkAttributeAddSelectTypeForm(forms.Form):
    ruletype = forms.ChoiceField(label = 'Attribute type',
            choices = (('text', 'text'),
                ('bool','boolean')))


class AttributeAddSelectTypeForm(forms.Form):
    ruletype = forms.ChoiceField(label = 'Attribute type',
            choices = (
                ('text', 'text'),
                ('bool', 'boolean'),
                ('int', 'int')
                ))

class AttributeUpdateTextForm(forms.Form):
    value = forms.CharField(max_length = 50, label = 'New value',
            required = False)

class AttributeUpdateBoolForm(forms.Form):
    value = forms.BooleanField(label = 'New value (true/false)',
            required = False)

class AttributeUpdateIntForm(forms.Form):
    value = forms.IntegerField(label = 'New value', initial = 0)

class AttributeUpdateLargeTextForm(forms.Form):
    def __init__(self, attribute, *args, **kwargs):
        super(AttributeUpdateLargeTextForm, self).__init__(*args, **kwargs)
        field = forms.CharField(
                max_length=5000,
                label=attribute.name,
                initial=attribute.value,
                required=False,
                widget=forms.Textarea(attrs={'cols':'100', 'rows': '20'})
        )
        self.fields['value'] = field


class AttributeAddTextForm(forms.Form):
    name = forms.CharField(
        max_length=50,
        label='Name',
        widget=forms.TextInput(
                attrs={
                        'placeholder': 'Name'
                }
        )
    )
    value = forms.CharField(
        max_length=50,
        label='Value',
        required=False,
        widget=forms.TextInput(
                attrs={
                        'placeholder': 'Value'
                }
        )
    )
    ruletype = forms.CharField(
            initial='text',
            widget=forms.HiddenInput()
    )
    large = forms.BooleanField(
            label='Large attribute',
            required=False,
            help_text='Attribute will have a separate display box.'
    )
    wikitext = forms.BooleanField(
            label='Wikitext attribute',
            required=False,
            help_text='Attribute will be displayed using textile wikitext parsing, implies "large".'
    )
    hidden = forms.BooleanField(
            label='Hidden attribute',
            required=False,
            help_text='Attribute will hidden per default if it is large/wikitext.'
    )
    important = forms.BooleanField(
            label='Important attribute',
            required=False,
            help_text='Attribute will be displayed on a device/entities overview page.'
    )
    versions = forms.IntegerField(
            label='Versions',
            min_value=1,
            initial=1,
            help_text='If set to > 1 a versioned attribute will be created.'
    )


class PasswordAttributeAddTextForm(AttributeAddTextForm):
    encrypted = forms.BooleanField(
            label='Encrypted attribute',
            required=False,
            help_text='Attribute will be encrypted using the same key as the parent password.'
    )


class AttributeAddBoolForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    value = forms.ChoiceField(label = 'Value',
            choices = (('true', 'True'), ('false', 'False')))
    ruletype = forms.CharField(initial = 'bool',
            widget = forms.HiddenInput())
    versions = forms.IntegerField(label = 'Versions',
            min_value = 1, initial = 1,
            help_text = 'If set to > 1 a versioned attribute will be created.')
    important = forms.BooleanField(label = 'Important attribute',
                                   required = False,
                                   help_text = 'If true, the attribute will be displayed on a device/entities overview page.')

class AttributeAddIntForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    value = forms.IntegerField(label = 'Integer Value', initial = 0)
    ruletype = forms.CharField(initial = 'int',
            widget = forms.HiddenInput())
    versions = forms.IntegerField(label = 'Versions',
            min_value = 1, initial = 1,
            help_text = 'If set to > 1 a versioned attribute will be created.')
    important = forms.BooleanField(label = 'Important attribute',
                                   required = False,
                                   help_text = 'If true, the attribute will be displayed on a device/entities overview page.')

class DeviceCategoryAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 100, required = False,
            label = 'Description')

class DeviceCategoryUpdateForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 100, required = False,
            label = 'Description')

class TemplateSelectForm(forms.Form):
    def __init__(self, templates, permit_none = True, *args, **kwargs):
        super(TemplateSelectForm, self).__init__(*args, **kwargs)
        tmpllist = []
        if permit_none:
            tmpllist.append((-1, 'None'))
        for template in templates:
            tmpllist.append((template.oid,
                template.attributes.get('name', '[UNKNOWN]')))
        field = forms.ChoiceField(label = 'Select template',
                choices = tmpllist)
        self.fields['template'] = field

class TemplateSetForm(forms.Form):
    def __init__(self, template, *args, **kwargs):
        super(TemplateSetForm, self).__init__(*args, **kwargs)
        rules = list(template.combinedRules())
        rules.sort(cmp=lambda x,y: cmp(x.attributes.get('priority', 10), y.attributes.get('priority', 10)))
        for rule in rules:
            field = None
            if rule.class_name == 'template rule text':
                wikitext = rule.attributes.get('wikitext', False)
                if not wikitext:
                    field = forms.CharField(max_length = 50,
                            label = rule.attr_name,
                            required = False,
                            help_text = rule.attributes.get('description', None))
            elif rule.class_name == 'template rule regmatch':
                if rule.attributes.get('description', None):
                    help_text = '%s (must match: %s)' % (
                            rule.attributes.get('description'),
                            rule.regexp
                            )
                else:
                    help_text = 'Must match: "%s"' % (rule.regexp)
                field = forms.RegexField(max_length = 50,
                        label = rule.attr_name,
                        regex = rule.regexp, required = False,
                        help_text = help_text)
            elif rule.class_name == 'template rule bool':
                field = forms.BooleanField(label = rule.attr_name,
                        required = False,
                        initial = rule.default_value,
                        help_text = rule.attributes.get('description', None))
            elif rule.class_name == 'template rule int':
                field = forms.IntegerField(label = rule.attr_name,
                        initial = rule.default_value,
                        help_text = rule.attributes.get('description', None))
            elif rule.class_name == 'template rule subdevice':
                field = forms.IntegerField(label = 'Number of subdevices',
                        required = False,
                        initial = rule.num_devices,
                        help_text = rule.attributes.get('description', None))
            if field:
                self.fields['argument-%s' % (rule.oid)] = field
        for rule in template.combinedRules():
            if rule.class_name in [
                    'template rule regmatch', 'template rule bool',
                    'template rule int', 'template rule subdevice']:
                continue
            if rule.class_name == 'template rule text':
                wikitext = rule.attributes.get('wikitext', False)
                if wikitext:
                    field = forms.CharField(max_length = 50,
                            label = rule.attr_name,
                            required = False,
                            widget = forms.HiddenInput(),
                            help_text = rule.attributes.get('description', None))
                else:
                    continue
            elif rule.class_name == 'template rule password':
                initial = ''
                if rule.username:
                    initial = '%s' % (rule.username)
                else:
                    initial = '[no username]'
                if rule.description:
                    initial = '%s - %s' % (initial, rule.description)
                field = forms.CharField(label = 'Add password',
                        required = False,
                        initial = initial,
                        widget=forms.TextInput(attrs={'readonly':'readonly'}),
                        help_text = rule.attributes.get('description', ''))
            elif rule.class_name == 'template rule assign network':
                field = forms.CharField(label = 'Auto-assign ip-address',
                        required = False,
                        widget = forms.HiddenInput(),
                        help_text = rule.attributes.get('description', ''))
            elif rule.class_name == 'template rule fixed':
                field = forms.CharField(label = rule.attr_name,
                        required = False,
                        initial = rule.value,
                        widget=forms.TextInput(attrs={'readonly':'readonly'}),
                        help_text = rule.attributes.get('description', ''))
                apply_label = 'Add attribute %s = %s' % (rule.attr_name, rule.value)
            elif rule.class_name == 'template rule flush nodes':
                field = forms.CharField(label = 'Flush existing nodes',
                        required = False,
                        widget = forms.HiddenInput(),
                        help_text = rule.attributes.get('description', ''))
            elif rule.class_name == 'template rule flush associations':
                field = forms.CharField(label = 'Flush existing associations',
                        required = False,
                        widget = forms.HiddenInput(),
                        help_text = rule.attributes.get('description', ''))
            elif rule.class_name == 'template rule delete attribute':
                field = forms.CharField(label = 'Delete attribute',
                        required = False,
                        initial = rule.attr_name,
                        widget=forms.TextInput(attrs={'readonly':'readonly'}),
                        help_text = rule.attributes.get('description', ''))
            else:
                field = forms.CharField(label = rule.class_name,
                        required = False,
                        widget = forms.HiddenInput(),
                        help_text = rule.attributes.get('description', ''))
            self.fields['argument-%s' % (rule.oid)] = field
#        field = forms.BooleanField(label = 'Overwrite',
#                required = False,
#                initial = True,
#                help_text = 'Overwrite existing attributes that have the same name as an attribute being created.')
#        self.fields['overwrite'] = field
#        self.fields['template'] = forms.CharField(initial = template.oid,
#                widget = forms.HiddenInput())

class DeviceSetValuesForm(forms.Form):
    def __init__(self, rules, *args, **kwargs):
        super(DeviceSetValuesForm, self).__init__(*args, **kwargs)
        for rule in rules:
            is_wikitext = rule.attributes.get('wikitext', False)
            if rule.dtype == 'text' and not is_wikitext:
                field = forms.CharField(max_length = 50, label = rule.name,
                        required = False,
                        help_text = rule.attributes.get('description', None))
                self.fields['attr-%s' % (rule.oid)] = field
            elif rule.dtype == 'text' and is_wikitext:
                widget = forms.HiddenInput()
                field = forms.CharField(label = rule.name, widget = widget,
                        initial = ' ')
                self.fields['attr-%s' % (rule.oid)] = field
            elif rule.dtype == 'regmatch':
                field = forms.RegexField(max_length = 50, label = rule.name,
                        regex = rule.value, required = False,
                        help_text = 'Must match: "%s"' % (rule.value))
                self.fields['attr-%s' % (rule.oid)] = field
#            elif rule.dtype == 'fixed':
#                widget = forms.HiddenInput()
#                field = forms.CharField(max_length = 50, label = rule.name,
#                        widget = widget, initial = rule.value)
#                self.fields['attr-%s' % (rule.oid)] = field
            if rule.dtype == 'bool':
                field = forms.BooleanField(label = rule.name, required = False,
                        initial = rule.attributes.get('default', True),
                        help_text = rule.attributes.get('description', None))
                self.fields['attr-%s' % (rule.oid)] = field
            else:
                pass

class DeviceNetworkAddForm(forms.Form):
    def __init__(self, network_trees, *args, **kwargs):
        super(DeviceNetworkAddForm, self).__init__(*args, **kwargs)
        nt_choices = []
        for tree in network_trees:
            value = (tree.oid, tree.attributes.get('name', '[UNKNOWN]'))
            if tree.attributes.get('default', False) is True:
                nt_choices.insert(0, value)
            else:
                nt_choices.append(value)
        field = forms.ChoiceField(label = 'Network Tree',
                choices = nt_choices,
                help_text = 'Network tree for address.')
        self.fields['networktree'] = field
        self.fields['network_name'] = \
                forms.CharField(max_length = 50, label = 'IP-Address',
                        help_text = 'Valid forms: host: "a.b.c.d", '
                        'cidr subnet: "a.b.c.d/nn"')
        self.fields['description'] = forms.CharField(max_length = 50, label = 'Description (optional)',
                required = False)

class UserAddForm(forms.Form):
    user_name = forms.CharField(max_length = 50, label = 'User Name')
    real_name = forms.CharField(max_length = 50, label = 'Real Name (optional)',
            required = False)
    description = forms.CharField(max_length = 50, label = 'Description (optional)',
            required = False)
    administrator = forms.BooleanField(label = 'Administrator',
            required = False,
            initial = False)
    password = forms.CharField(max_length = 32, label = 'Password',
            widget = forms.PasswordInput(), required = True)
    validate = forms.CharField(max_length = 32, label = 'Password (again)',
            widget = forms.PasswordInput(), required = True)

class UserUpdateAdminForm(forms.Form):
    user_name = forms.CharField(max_length = 50, label = 'User Name')
    real_name = forms.CharField(max_length = 50, label = 'Real Name (optional)',
            required = False)
    description = forms.CharField(max_length = 50, label = 'Description (optional)',
            required = False)
    administrator = forms.BooleanField(label = 'Administrator',
            required = False,
            initial = False)

class UserUpdateForm(forms.Form):
    user_name = forms.CharField(max_length = 50, label = 'User Name')
    real_name = forms.CharField(max_length = 50, label = 'Real Name (optional)',
            required = False)
    description = forms.CharField(max_length = 50, label = 'Description (optional)',
            required = False)

class UserResetPasswordForm(forms.Form):
    password = forms.CharField(max_length = 32, label = 'Password',
            widget = forms.PasswordInput(), required = False,
            help_text = 'Reseting the password for a user will disconnect all subkeys etc. Use this if the old password for the user is unknown.')
    validate = forms.CharField(max_length = 32, label = 'Password (again)',
            widget = forms.PasswordInput(), required = False)

class UserUpdatePasswordForm(forms.Form):
    password = forms.CharField(max_length = 32, label = 'New Password',
            widget = forms.PasswordInput(), required = False)
    validate = forms.CharField(max_length = 32, label = 'New Password (again)',
            widget = forms.PasswordInput(), required = False)
    old_password = forms.CharField(max_length = 32, label = 'Old Password',
            widget = forms.PasswordInput(), required = False,
            help_text = 'Needs to be supplied if you are changing the password of a user other than your own.')

class UserConnectKeyForm(forms.Form):

    password_key_key = forms.CharField(max_length = 32, label = 'Password key password',
            widget = forms.PasswordInput(), required = False,
            help_text = 'Required if the current active user doesn\'t have the selected password key connected.')

    def __init__(self, password_keys, require_user_password, *args, **kwargs):
        super(UserConnectKeyForm, self).__init__(*args, **kwargs)

        self.message = '''
        If you're connecting a password key for another user, keep in mind; that
        user must logout and login to siptrack before the key will be connected.
        '''

        keylist = []
        for key in password_keys:
            value = (key.oid, key.attributes['name'])
            if key.attributes.get('default', False) is True:
                keylist.insert(0, value)
            else:
                keylist.append(value)
        field = forms.ChoiceField(label = 'Password key', choices = keylist)
        self.fields['passwordkey'] = field
        if require_user_password:
            field = forms.CharField(
                max_length=32,
                label='User\'s password',
                help_text='Required to create the users keypair if they\'ve never logged in before.',
                widget=forms.PasswordInput(),
                required=False
            )
            self.fields['user_password'] = field

class UserManagerLocalAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 50, label = 'Description (optional)',
            required = False)

class UserManagerLDAPAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 50, label = 'Description (optional)',
            required = False)
    connection_type = forms.ChoiceField(label = 'Connection type',
            choices = (('ldap', 'ldap'), ('ldaps', 'ldaps')))
    server = forms.CharField(max_length = 256, label = 'LDAP server')
    port = forms.CharField(max_length = 5, label = 'LDAP server port')
    base_dn = forms.CharField(max_length = 128, label = 'Base DN')
    valid_groups = forms.CharField(max_length = 1000, label = 'Valid LDAP group',
            help_text = 'Only members of the given group will be able to log in, use ":" to seperate groups.',
            required = False)

class UserManagerActiveDirectoryAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 50, label = 'Description (optional)',
            required = False)
    server = forms.CharField(max_length = 256, label = 'AD server')
    base_dn = forms.CharField(max_length = 128, label = 'Base DN')
    valid_groups = forms.CharField(max_length = 1000, label = 'Valid LDAP group',
            help_text = 'Only members of the given group will be able to log in, use ":" to seperate groups.',
            required = False)
    user_domain = forms.CharField(max_length = 128, label = 'User Domain')

class DeviceResetForm(forms.Form):
    reset_attributes = forms.BooleanField(label = 'Reset attributes',
            required = False,
            initial = True)
    reset_device_links = forms.BooleanField(label = 'Reset device links',
            required = False,
            initial = False)
    reset_passwords = forms.BooleanField(label = 'Reset passwords',
            required = False,
            initial = True)
    reset_subdevices = forms.BooleanField(label = 'Reset subdevices',
            required = False,
            initial = True)

class ConfigAddSelectTypeForm(forms.Form):
    def __init__(self, parent, *args, **kwargs):
        super(ConfigAddSelectTypeForm, self).__init__(*args, **kwargs)
        choices = []
        if parent.class_name not in ['view tree', 'ipv4 network',
                'ipv6 network', 'network tree', 'ipv4 network range',
                'ipv6 network range']:
            choices.append(('netautoassign', 'Network auto assignment'))
        choices.append(('value', 'Config value'))
        field = forms.ChoiceField(label = 'Config type', choices = choices)
        self.fields['config_type'] = field

class ConfigAddNetworkAutoassignForm(forms.Form):
    config_type = forms.CharField(initial = 'netautoassign',
            widget = forms.HiddenInput())

    def __init__(self, network_trees, *args, **kwargs):
        super(ConfigAddNetworkAutoassignForm, self).__init__(*args, **kwargs)
        nt_choices = []
        for tree in network_trees:
            value = (tree.oid, tree.attributes.get('name', '[UNKNOWN]'))
            if tree.attributes.get('default', False) is True:
                nt_choices.insert(0, value)
            else:
                nt_choices.append(value)
        field = forms.ChoiceField(label = 'Network Tree',
                choices = nt_choices,
                help_text = 'Network tree for address.')
        self.fields['networktree'] = field
        self.fields['range_start'] = \
                forms.CharField(max_length = 50, label = 'Range Start',
                        help_text = 'Enter the start address of the range used for assignment"')
        self.fields['range_end'] = \
                forms.CharField(max_length = 50, label = 'Range End',
                        help_text = 'Enter the end address of the range used for assignment"')

class ConfigAddValueForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    value = forms.CharField(max_length = 50, label = 'Value', required = False)
    config_type = forms.CharField(initial = 'value',
            widget = forms.HiddenInput())

class PermissionAddForm(forms.Form):
    read_access = forms.BooleanField(label = 'Read access',
            required = False)
    write_access = forms.BooleanField(label = 'Write access',
            required = False)
    all_users = forms.BooleanField(label = 'Applies to all users',
            required = False)
    recursive = forms.BooleanField(label = 'Recursive',
            required = False,
            help_text = 'Applies recursively up the node tree.')

    def __init__(self, users, groups, *args, **kwargs):
        super(PermissionAddForm, self).__init__(*args, **kwargs)
        field = forms.MultipleChoiceField(required = False,
                label = 'Users',
                choices = users,
                help_text = 'Included users.')
        self.fields['users'] = field
        field = forms.MultipleChoiceField(required = False,
                label = 'Groups',
                choices = groups,
                help_text = 'Included groups.')
        self.fields['groups'] = field

class UserGroupAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 50, label = 'Description',
            required = False)

    def __init__(self, users, *args, **kwargs):
        super(UserGroupAddForm, self).__init__(*args, **kwargs)
        field = forms.MultipleChoiceField(required = False,
                label = 'Users',
                choices = users,
                help_text = 'Included users.')
        self.fields['users'] = field

class UserGroupUpdateForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 50, label = 'Description (optional)',
            required = False)

    def __init__(self, users, *args, **kwargs):
        super(UserGroupUpdateForm, self).__init__(*args, **kwargs)
        field = forms.MultipleChoiceField(required = False,
                label = 'Users',
                choices = users,
                help_text = 'Included users.')
        self.fields['users'] = field

class CommandAddForm(forms.Form):
    freetext = forms.CharField(max_length = 200, label = 'Command text')

class CommandUpdateForm(forms.Form):
    freetext = forms.CharField(max_length = 200, label = 'Command text')

class CommandQueueAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')

class CommandQueueUpdateForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')

class EventTriggerAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')

class EventTriggerUpdateForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')

class EventTriggerRulePythonAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    code = forms.CharField(max_length = 5000, label = 'Code',
                help_text = 'python code',
                widget = forms.Textarea(attrs={'cols':'80', 'rows': '50'}))

class EventTriggerRulePythonUpdateForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    code = forms.CharField(max_length = 5000, label = 'Code',
                help_text = 'python code',
                widget = forms.Textarea(attrs={'cols':'80', 'rows': '50'}))

class UsermanagerADSyncUsersForm(forms.Form):
    username = forms.CharField(max_length = 50, label = 'Username')
    password = forms.CharField(max_length = 32, label = 'Password',
            widget = forms.PasswordInput(), required = True)

class PasswordCategoryAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 100, required = False,
            label = 'Description')

class DeviceCopyForm(forms.Form):
   skip_attributes = forms.BooleanField(label = 'Skip attributes',
                                           required = False, initial = False)
   skip_devices = forms.BooleanField(label = 'Skip sub-devices',
                                           required = False, initial = False)
   skip_networks = forms.BooleanField(label = 'Skip networks',
                                           required = False, initial = True)

class AttributeEditNotesForm(forms.Form):
    notes = forms.CharField(max_length = 50000, label = '',
                            help_text = '',
                            required = False,
                            widget = forms.Textarea(attrs={'cols':'100', 'rows': '15'}))

class AttributeQuickeditForm(forms.Form):
    value = forms.CharField(max_length = 100, required = False,
            label = 'Value')

class RackUnitOccupiedForm(forms.Form):
    reason = forms.CharField(max_length = 500, required = False,
                             label = 'Reason',
                             help_text = 'Describe what is occupying this unit.')

class RackUnitReservedForm(forms.Form):
    reason = forms.CharField(max_length = 500, required = False,
                                  label = 'Reason',
                             help_text = 'Describe why this unit is reserved.')

class DeviceConfigAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 100, required = False,
            label = 'Description')
    max_versions = forms.IntegerField(label = 'Retained versions',
                                  min_value = 0, initial = 10,
                                  help_text = 'The number of config versions to retain, set to 0 for unlimited.')

class DeviceConfigSubmitForm(forms.Form):
    data = forms.CharField(max_length = 1000000, label = '',
                            help_text = '',
                            required = True,
                            widget = forms.Textarea(attrs={'cols':'100', 'rows': '15'}))

class DeviceConfigTemplateAddForm(forms.Form):
    name = forms.CharField(max_length = 50, label = 'Name')
    description = forms.CharField(max_length = 100, required = False,
            label = 'Description')
    data = forms.CharField(max_length = 1000000, label = '',
                            help_text = '',
                            required = True,
                            widget = forms.Textarea(attrs={'cols':'100', 'rows': '15'}))

class DeviceConfigTemplateSubmitForm(forms.Form):
    data = forms.CharField(max_length = 1000000, label = '',
                            help_text = '',
                            required = True,
                            widget = forms.Textarea(attrs={'cols':'100', 'rows': '15'}))

