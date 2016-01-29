from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ats_sms_operator.config import ATS_STATES, get_output_sms_model
from ats_sms_operator.sender import DeliveryRequest, send_and_update_sms_states


class Command(BaseCommand):

    def handle(self, *args, **options):
        to_check = get_output_sms_model().objects.filter(
            state__in=(ATS_STATES.OK, ATS_STATES.NOT_SENT, ATS_STATES.SENT))
        if to_check.exists():
            send_and_update_sms_states(*[DeliveryRequest(sms) for sms in to_check])
