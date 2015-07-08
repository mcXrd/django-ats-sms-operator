from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from is_core.main import UIRestModelISCore

from ats_sms_operator.models import InputATSSMSmessage


class InputATSSMSmessageIsCore(UIRestModelISCore):
    model = InputATSSMSmessage
    list_display = ('created_at' , 'received_at', 'sender', 'recipient', 'uniq')
    abstract = True
    form_fields = ('created_at' , 'received_at', 'sender', 'recipient', 'uniq', 'okey', 'opid', 'opmid', 'content')

    def has_create_permission(self, request, obj=None):
        return False

    def has_update_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
