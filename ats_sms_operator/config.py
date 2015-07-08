from django.conf import settings


ATS_SMS_SENDER_IP = getattr(settings, 'ATS_SMS_SENDER_IP', '80.188.94.234')
ATS_SMS_DEBUG = getattr(settings, 'ATS_SMS_DEBUG', False)
