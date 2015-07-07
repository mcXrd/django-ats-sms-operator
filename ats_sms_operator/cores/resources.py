from __future__ import unicode_literals

from datetime import datetime

from django.utils import timezone
from django.utils.encoding import force_text
from django.db import IntegrityError

from is_core.rest.resource import RestResource

from piston.response import RestNoConetentResponse

from ats_sms_operator.models import InputATSSMSmessage

from bs4 import BeautifulSoup


class InputATSSMSmessageResource(RestResource):
    login_required = False

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
                input_message, _ = InputATSSMSmessage.objects.get_or_create(
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
                result.append((22, input_message.uniq))
            except (IntegrityError, TypeError):
                if 'uniq' in message:
                    result.append((23, message.get('uniq')))

        return result
