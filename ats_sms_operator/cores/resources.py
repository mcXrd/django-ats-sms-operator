from __future__ import unicode_literals

from datetime import datetime

from django.utils import timezone
from django.utils.encoding import force_text
from django.db import IntegrityError
from django.conf import settings

from ipware.ip import get_ip

from bs4 import BeautifulSoup

from is_core.rest.resource import RestResource

from ats_sms_operator.models import InputATSSMSmessage
from ats_sms_operator import config


class InputATSSMSmessageResource(RestResource):
    login_required = False

    def __init__(self, request, callback_function):
        super(InputATSSMSmessageResource, self).__init__(request)
        self.callback_function = callback_function

    def _deserialize(self):
        soup = BeautifulSoup(force_text(self.request.body), 'html.parser')
        data = []
        for message in soup.messages.find_all('sms'):
            message_data = message.attrs
            message_data['content'] = message.string
            data.append(message_data)
        self.request.data = data
        return self.request

    def _serialize(self, result):
        output = ['<?xml version="1.0" encoding="UTF-8" ?>']
        output.append('<status>')
        for code, uniq in result:
            output.append('<code uniq="%s">%s</code>' % (uniq, code))
        output.append('</status>')
        return '\n'.join(output), 'text/xml'

    def post(self):
        data = self.request.data
        result = []
        for message in data:
            try:
                input_message, created = InputATSSMSmessage.objects.get_or_create(
                    uniq=message.get('uniq'),
                    sender=message.get('sender'),
                    recipient=message.get('recipient'),
                    okey=message.get('okey'),
                    opid=message.get('opid'),
                    opmid=message.get('opmid'),
                    received_at=timezone.make_aware(datetime.strptime(message.get('ts'), "%Y-%m-%d %H:%M:%S"),
                                                     timezone.get_default_timezone()),
                    content=message.get('content')
                )
                code = 23  if self.callback_function(input_message, created) else 24
                result.append((code, input_message.uniq))
            except (IntegrityError, TypeError) as er:
                if 'uniq' in message:
                    result.append((24, message.get('uniq')))

        return result

    def has_post_permission(self, *args, **kwargs):
        return (super(InputATSSMSmessageResource, self).has_post_permission(*args, **kwargs) and
                (get_ip(self.request) == config.ATS_SMS_SENDER_IP or getattr(settings, 'ATS_SMS_DEBUG', False)))
