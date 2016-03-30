from __future__ import unicode_literals

from germanium.rest import RESTTestCase
from germanium.tools import assert_equal

from sender.models import InputSMS


class InputSMSTestCase(RESTTestCase):

    API_URL = '/api/atsinputsmsmessage/'
    ATS_SMS_POST_PAYLOAD = """<?xml version="1.0" encoding="UTF-8" ?>
                           <messages>
                               <sms uniq="2" sender="+420731545945" recipient="9001103" okey="T2" opid="tmsms"
                                   opmid="" ts="2006-04-10 09:32:18">test2</sms>
                               <sms uniq="3" sender="+420731545945" recipient="9001103" okey="T2" opid="tmsms"
                                   opmid="" ts="2006-04-10 09:32:23">test3</sms>
                               <sms uniq="4" sender="+420731545945" recipient="9001103" okey="T2" opid="tmsms"
                                   opmid="" ts="2006-04-10 09:32:23"></sms>
                           </messages>"""

    def test_ats_request_should_create_input_sms(self):
        sms_count = InputSMS.objects.count()
        response = self.post(self.API_URL, self.ATS_SMS_POST_PAYLOAD)
        self.assert_http_ok(response)  # ATS requires to return 200 in every situation
        assert_equal(sms_count + 3, InputSMS.objects.count())
        assert_equal('test3', InputSMS.objects.get(uniq=3).content)
        assert_equal('', InputSMS.objects.get(uniq=4).content)
