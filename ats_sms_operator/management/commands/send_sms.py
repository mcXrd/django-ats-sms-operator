from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ats_sms_operator.config import ATS_STATES, get_output_sms_model
from ats_sms_operator.sender import send_and_update_sms_states


class Command(BaseCommand):

    def handle(self, *args, **options):
        messages = get_output_sms_model().objects.filter(state=ATS_STATES.LOCAL_TO_SEND)
        if messages.exists():
            send_and_update_sms_states(*list(messages))
