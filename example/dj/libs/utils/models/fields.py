from __future__ import unicode_literals

from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from chamber.utils.datastructures import ChoicesNumEnum, ChoicesEnum
from chamber.models.fields import SouthMixin

from is_core.forms.widgets import SmartWidgetMixin


class SequenceSelect(SmartWidgetMixin, forms.Select):

    def __init__(self, enum, attrs=None, choices=()):
        super(SequenceSelect, self).__init__(attrs, choices)
        self.enum = enum

    def set_allowed_choices(self, value):
        allowed_next_values = self.enum.get_allowed_next_states(value)
        allowed_choices = []
        for choice in self.choices:
            if choice[0] in allowed_next_values:
                allowed_choices.append(choice)

        self.choices = allowed_choices

    def smart_render(self, request, name, value, initial_value, *args, **kwargs):
        self.set_allowed_choices(initial_value)
        return super(SequenceSelect, self).smart_render(request, name, value, initial_value, *args, **kwargs)


class SequenceChoicesEnumMixin(object):

    def __init__(self, *items):
        assert len(items) > 0

        # The last value of every item are omitted and send to ChoicesEnum constructor
        super(SequenceChoicesEnumMixin, self).__init__(*(item[:-1] for item in items if item[0] is not None))

        self.first_choices = self._get_first_choices(items)
        self.sequence_graph = {}

        # The last value of every item is used for construction of graph that define allowed next states for every state
        for item in items:
            if item[0] is not None:
                self.sequence_graph[getattr(self, item[0])] = [getattr(self, next_choice) for next_choice in item[-1]]

    def _get_first_choices(self, items):
        for item in items:
            if item[0] is None:
                return [getattr(self, key) for key in item[1]]
        return [getattr(self, items[0][0])]

    def get_allowed_next_states(self, state):
        if not state:
            return self.first_choices
        else:
            return self.sequence_graph.get(state)


class SequenceChoicesEnum(SequenceChoicesEnumMixin, ChoicesEnum):
    pass


class SequenceChoicesNumEnum(SequenceChoicesEnumMixin, ChoicesNumEnum):
    pass


class StringChoicesNumEnum(ChoicesNumEnum):

    def __init__(self, *items):
        assert len(items) > 0

        # The last value of every item are omitted and send to ChoicesEnum constructor
        super(StringChoicesNumEnum, self).__init__(*(item[:-1] for item in items if item[0] is not None))
        self.mapping = {key: value for _, _, key, value in items}

    def get_string(self, value):
        return self.mapping[value]


class EnumSequenceFieldMixin(object):

    def __init__(self, *args, **kwargs):
        self.enum = kwargs.pop('enum', None)
        assert self.enum is None or isinstance(self.enum, SequenceChoicesEnumMixin)
        if self.enum:
            kwargs['choices'] = self.enum.choices
        super(EnumSequenceFieldMixin, self).__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super(EnumSequenceFieldMixin, self).validate(value, model_instance)
        if self.enum:
            prev_value = model_instance.pk and model_instance.initial_values[self.attname] or None
            allowed_next_values = self.enum.get_allowed_next_states(prev_value)

            if value not in allowed_next_values:
                raise ValidationError(_('Allowed choices are %s.') %
                                      ', '.join(('%s (%s)' % (self.enum.get_label(val), val)
                                                 for val in allowed_next_values)
                    )
                )

    def formfield(self, **kwargs):
        defaults = {'widget': SequenceSelect(self.enum)}
        defaults.update(kwargs)
        return super(EnumSequenceFieldMixin, self).formfield(**defaults)

class EnumSequencePositiveIntegerField(EnumSequenceFieldMixin, SouthMixin, models.PositiveIntegerField):
    pass


class EnumSequenceCharField(EnumSequenceFieldMixin, SouthMixin, models.CharField):
    pass
