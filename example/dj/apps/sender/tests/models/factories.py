from __future__ import unicode_literals

import string
from datetime import datetime, timedelta

import factory
from factory import django as factory_django
from factory import fuzzy

from sender.models import InputSMS, OutputSMS, SMSTemplate


class InputSMSFactory(factory_django.DjangoModelFactory):

    received_at = fuzzy.FuzzyNaiveDateTime(start_dt=datetime.now() - timedelta(days=150))
    uniq = factory.Sequence(lambda n: n)
    sender = '777123456'
    recipient = '777444888'
    okey = fuzzy.FuzzyText(length=50)
    opid = fuzzy.FuzzyText(length=50)
    opmid = fuzzy.FuzzyText(length=50)
    content = fuzzy.FuzzyText(length=50)
    created_at = fuzzy.FuzzyNaiveDateTime(start_dt=datetime.now() - timedelta(days=150))
    changed_at = fuzzy.FuzzyNaiveDateTime(start_dt=datetime.now() - timedelta(days=150))

    class Meta:
        model = InputSMS


class OutputSMSFactory(factory_django.DjangoModelFactory):
    # Do NOT add sent_at to the factory, must be set by hand to be able to test functionality
    sender = '+420777123456'
    recipient = fuzzy.FuzzyText(length=9, prefix='+420', chars=string.digits)
    opmid = ''
    dlr = '1'
    kw = fuzzy.FuzzyText(length=30)
    content = fuzzy.FuzzyText(length=160)
    created_at = fuzzy.FuzzyNaiveDateTime(start_dt=datetime.now() - timedelta(days=150))
    changed_at = fuzzy.FuzzyNaiveDateTime(start_dt=datetime.now() - timedelta(days=150))

    class Meta:
        model = OutputSMS


class SMSTemplateFactory(factory_django.DjangoModelFactory):

    slug = 'test'
    body = 'Does rendering context variables work? {{ variable }}'
    created_at = fuzzy.FuzzyNaiveDateTime(start_dt=datetime.now() - timedelta(days=150))
    changed_at = fuzzy.FuzzyNaiveDateTime(start_dt=datetime.now() - timedelta(days=150))

    class Meta:
        model = SMSTemplate
