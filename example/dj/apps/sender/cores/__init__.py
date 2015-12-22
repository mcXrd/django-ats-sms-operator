from django.contrib.auth.models import User

try:
    from is_core.main import UIRESTModelISCore
except ImportError:
    from is_core.main import UIRestModelISCore as UIRESTModelISCore

from sender.models import OutputSMS

from ats_sms_operator.cores import InputATSSMSmessageISCore


class UserIsCore(UIRESTModelISCore):
    model = User
    list_display = ('id', '_obj_name')

    def has_read_permission(self, request, obj=None):
        return request.user.is_superuser or not obj or obj.pk == request.user.pk

    def has_create_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_update_permission(self, request, obj=None):
        return (obj and obj.pk == request.user.pk) or request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_queryset(self, request):
        qs = super(UserIsCore, self).get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(pk=request.user.pk)
        return qs


class OutputSMSISCore(UIRESTModelISCore):
    model = OutputSMS
    list_display = ('id', '_obj_name', 'watched_by_string', 'leader__email', 'leader__last_name')


class InputSMSISCore(InputATSSMSmessageISCore):
    abstract = False
