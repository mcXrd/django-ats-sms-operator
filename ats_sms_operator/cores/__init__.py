from __future__ import unicode_literals

from is_core.main import UIRESTModelISCore

from ats_sms_operator.config import get_input_sms_model
from ats_sms_operator.cores.resources import InputATSSMSmessageResource


class InputATSSMSmessageISCore(UIRESTModelISCore):
    model = get_input_sms_model()
    list_display = ('created_at', 'received_at', 'sender', 'recipient', 'uniq')
    abstract = True
    form_fields = ('created_at', 'received_at', 'sender', 'recipient', 'uniq', 'okey', 'opid', 'opmid', 'content')

    def has_create_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
