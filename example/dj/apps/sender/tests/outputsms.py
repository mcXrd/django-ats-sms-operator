# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import responses

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from germanium.tools import assert_equal, assert_false, assert_is_not_none, assert_true

from ats_sms_operator.config import ATS_STATES
from ats_sms_operator.management.commands.check_sms_delivery import Command as CheckDeliveryCommand
from ats_sms_operator.management.commands.send_sms import Command as SendCommand
from ats_sms_operator.sender import parse_response_codes, send_ats_requests, serialize_ats_requests

from .models.factories import OutputSMSFactory


# TODO remove this when the function is added to chamber
def strip_all(txt):
    return ''.join(txt.split())


class OutputSMSTestCase(TestCase):

    ATS_SERIALIZED_SMS = """<sms type="text" uniq="{}" sender="90099" recipient="+420731545945" opmid=""
                             dlr="1" validity="60" kw="90099RASMT">
                             <body order="0" billing="0">TEXT1</body>
                             </sms>"""

    ATS_SMS_REQUEST = """<?xml version="1.0" encoding="UTF-8" ?>
                         <messages>
                            <auth>
                                <name>pinkypink</name>
                                <password>as3d4rt321415ce2f52738972725ac8f</password>
                            </auth>
                            <sms type="text" uniq="{}" sender="90099" recipient="+420731545945" opmid=""
                             dlr="1" validity="60" kw="90099RASMT">
                                <body order="0" billing="0">TEXT1</body>
                            </sms>
                            <sms type="text" uniq="{}" sender="90099" recipient="+420777555444" opmid=""
                             dlr="1" validity="60" kw="90099RASMT">
                                <body order="0" billing="0">TEXT2</body>
                            </sms>
                         </messages>"""

    ATS_SMS_REQUEST_RESPONSE_SENT = """<?xml version="1.0" encoding="UTF-8" ?>
                                       <status>
                                            <code uniq="{}">0</code>
                                            <code uniq="{}">123456</code>
                                            <d></d>
                                       </status>"""

    ATS_SMS_DELIVERY_REQUEST = """<?xml version="1.0" encoding="UTF-8" ?>
                                  <messages>
                                      <auth>
                                          <name>pinkypink</name>
                                          <password>as3d4rt321415ce2f52738972725ac8f</password>
                                      </auth>
                                  <dlr uniq="{first_id}">{first_id}</dlr>
                                  <dlr uniq="{second_id}">{second_id}</dlr>
                                  </messages>"""

    ATS_SMS_DELIVERY_RESPONSE = """<?xml version="1.0" encoding="UTF-8" ?>
                                   <status>
                                       <code uniq="{}">22</code>
                                       <code uniq="{}">23</code>
                                       <d></d>
                                   </status>"""

    ATS_UNKNOW_STATE_RESPONSE = """<?xml version="1.0" encoding="UTF-8" ?>
                                   <status>
                                       <code>999</code>
                                   </status>"""
    ATS_TEST_UNIQ = (245, 246)

    ATS_OUTPUT_SMS1 = {
        'content': 'TĚXT1',
        'recipient': '+420731545945',
        'validity': 60,
    }

    ATS_OUTPUT_SMS2 = {
        'content': 'TĚXT2',
        'recipient': '+420777555444',
        'validity': 60,
    }

    def test_should_serialize_sms_message(self):
        sms = OutputSMSFactory(**self.ATS_OUTPUT_SMS1)
        assert_equal(strip_all(sms.serialize_ats()), strip_all(self.ATS_SERIALIZED_SMS.format(sms.pk)))

    def test_should_serialize_ats_requests(self):
        sms1 = OutputSMSFactory(**self.ATS_OUTPUT_SMS1)
        sms2 = OutputSMSFactory(**self.ATS_OUTPUT_SMS2)
        assert_equal(strip_all(serialize_ats_requests(sms1, sms2)),
                     strip_all(self.ATS_SMS_REQUEST.format(sms1.pk, sms2.pk)))

    @responses.activate
    def test_should_send_ats_request_and_parse_response_codes(self):
        responses.add(responses.POST, settings.ATS_URL, content_type='text/xml',
                      body=self.ATS_SMS_REQUEST_RESPONSE_SENT.format(*self.ATS_TEST_UNIQ), status=200)
        sms1 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[0], **self.ATS_OUTPUT_SMS1)
        sms2 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[1], **self.ATS_OUTPUT_SMS2)

        response = send_ats_requests(sms1, sms2)

        assert_equal(response.request.url, 'http://fik.atspraha.cz/gwfcgi/XMLServerWrapper.fcgi')
        assert_equal(response.request.headers['content-type'], 'text/xml')

        response_codes = parse_response_codes(response.text)

        assert_equal(response_codes[self.ATS_TEST_UNIQ[0]], 0)
        assert_equal(response_codes[self.ATS_TEST_UNIQ[1]], 123456)

    @responses.activate
    def test_command_should_send_and_update_sms(self):
        responses.add(responses.POST, settings.ATS_URL, content_type='text/xml',
                      body=self.ATS_SMS_REQUEST_RESPONSE_SENT.format(*self.ATS_TEST_UNIQ), status=200)

        sms1 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[0], **self.ATS_OUTPUT_SMS1)
        sms2 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[1], **self.ATS_OUTPUT_SMS2)

        SendCommand().handle()

        sms1.refresh_from_db()
        sms2.refresh_from_db()

        assert_equal(sms1.state, ATS_STATES.OK)
        assert_is_not_none(sms1.sent_at)
        assert_equal(sms2.state, ATS_STATES.LOCAL_UNKNOWN_ATS_STATE)
        assert_is_not_none(sms2.sent_at)

    @responses.activate
    def test_command_should_check_delivery_status(self):
        responses.add(responses.POST, settings.ATS_URL, content_type='text/xml',
                      body=self.ATS_SMS_DELIVERY_RESPONSE.format(*self.ATS_TEST_UNIQ),
                      status=200)

        sms2 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[1], sent_at=timezone.now(), state=ATS_STATES.OK,
                                **self.ATS_OUTPUT_SMS2)
        sms1 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[0], sent_at=timezone.now(), state=ATS_STATES.OK,
                                **self.ATS_OUTPUT_SMS1)

        CheckDeliveryCommand().handle()

        sms1.refresh_from_db()
        sms2.refresh_from_db()

        assert_equal(strip_all(responses.calls[0].request.body),
                     strip_all(self.ATS_SMS_DELIVERY_REQUEST.format(first_id=self.ATS_TEST_UNIQ[0],
                                                                    second_id=self.ATS_TEST_UNIQ[1])))
        assert_equal(sms1.state, ATS_STATES.SENT)
        assert_equal(sms2.state, ATS_STATES.DELIVERED)

    @responses.activate
    def test_should_correctly_handle_unknown_ats_state(self):
        responses.add(responses.POST, settings.ATS_URL, content_type='text/xml',
                      body=self.ATS_UNKNOW_STATE_RESPONSE, status=200)
        sms1 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[0], **self.ATS_OUTPUT_SMS1)
        sms2 = OutputSMSFactory(pk=self.ATS_TEST_UNIQ[1], **self.ATS_OUTPUT_SMS2)

        response = send_ats_requests(sms1, sms2)
        with open('./var/log/ats_sms.log') as ats_log:
            log_lines_count = sum(1 for _ in ats_log)
            response_codes = parse_response_codes(response.text)
            ats_log.seek(0)
            log_lines = ats_log.readlines()

            assert_equal(log_lines_count + 1, len(log_lines))
            assert_true('999' in log_lines[-1])
            assert_false(response_codes)
