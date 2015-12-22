from __future__ import unicode_literals

from ats_sms_operator.models import AbstractInputATSSMSmessage, AbstractOutputATSSMSmessage, AbstractSMSTemplate


class OutputSMS(AbstractOutputATSSMSmessage):
    pass


class InputSMS(AbstractInputATSSMSmessage):
    pass


class SMSTemplate(AbstractSMSTemplate):
    pass
