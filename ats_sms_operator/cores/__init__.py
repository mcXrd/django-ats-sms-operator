from __future__ import unicode_literals

# TODO remove the try-except once old is-core does not have to be supported
try:
    from is_core.main import UIRESTModelISCore
except ImportError:
    from is_core.main import UIRestModelISCore as UIRESTModelISCore


from ats_sms_operator import config


class InputATSSMSmessageISCore(UIRESTModelISCore):
    model = config.get_input_sms_model()
    list_display = ('created_at', 'received_at', 'sender', 'recipient', 'uniq', 'content')
    abstract = True
    form_fields = ('created_at', 'received_at', 'sender', 'recipient', 'uniq', 'okey', 'opid', 'opmid', 'content')

    def has_create_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class OutputATSSMSmesssageISCore(UIRESTModelISCore):
    model = config.get_output_sms_model()
    list_display = ('sent_at', 'sender', 'recipient', 'content', 'state')
    abstract = True

    def has_create_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SMSTemplateISCore(UIRESTModelISCore):
    model = config.get_sms_template_model()
    abstract = True
