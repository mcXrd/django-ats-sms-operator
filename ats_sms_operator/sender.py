from __future__ import unicode_literals

import logging
from itertools import chain

import ats_sms_operator.logged_requests as requests

from bs4 import BeautifulSoup

from django.utils import timezone

from chamber.shortcuts import get_object_or_none

from .config import ATS_PASSWORD, ATS_STATES, ATS_URL, ATS_USERNAME, get_output_sms_model


logger = logging.getLogger('ats_sms')

header = """<?xml version="1.0" encoding="UTF-8" ?>
            <messages>
                <auth>
                    <name>{username}</name>
                    <password>{password}</password>
                </auth>"""
footer = '</messages>'


class DeliveryRequest(object):
    """
    Helper class to create ATS delivery requests from an output SMS. Since the output SMS itself must implement
    serialize_ats() method as well.
    """

    def __init__(self, output_sms):
        self.output_sms = output_sms

    def serialize_ats(self):
        return """<dlr uniq="{}">{}</dlr>""".format(self.output_sms.pk, self.output_sms.pk)


def serialize_ats_requests(*ats_requests):
    """
    Prepares XML with the given ATS elementary requests. The requests must be an instance of a class implementing
    the serialize_ats() method.
    """
    not_serializable = set(request.__class__.__name__ for request in ats_requests
                           if not hasattr(request, 'serialize_ats'))
    if not_serializable:
        raise NotImplementedError('Passed classes do not implement serialize_ats() method: {}'.format(not_serializable))
    return ''.join(chain(
        (header.format(username=ATS_USERNAME, password=ATS_PASSWORD),),
        (request.serialize_ats() for request in ats_requests),
        (footer,),
    ))


def send_ats_requests(*ats_requests):
    """
    Performs the actual POST request with the given elementary ATS requests.
    """
    requests_xml = serialize_ats_requests(*ats_requests)
    return requests.post(ATS_URL, data=requests_xml, headers={'Content-Type': 'text/xml'}, related_objects=ats_requests)


def parse_response_codes(xml):
    """
    Finds all <code> tags in the given XML and returns a mapping "uniq" -> "response code" for all SMS.
    In case of an error, the error is logged.
    """
    soup = BeautifulSoup(xml, 'html.parser')
    code_tags = soup.find_all('code')

    logger.warning(', '.join(
        [ATS_STATES.get_label(c) if c in ATS_STATES.all else 'ATS returned an unknown state {}.'.format(c)
         for c in [int(error_code.string) for error_code in code_tags if not error_code.attrs.get('uniq')]],
    ))

    return {int(code.attrs['uniq']): int(code.string) for code in code_tags if code.attrs.get('uniq')}


def send_and_parse_response(*ats_requests):
    """
    Glue function to perform sending ATS requests and parsing the ATS server response in one go.
    """
    response = send_ats_requests(*ats_requests)
    return parse_response_codes(response.text)


def send_and_update_sms_states(*ats_requests):
    """
    Higher-level function performing serialization of ATS requests, parsing ATS server response and updating
    SMS messages state according the received response.
    """
    for uniq, state in send_and_parse_response(*ats_requests).items():
        sms = get_object_or_none(get_output_sms_model(), pk=uniq)
        if sms:
            sms.state = state if state in ATS_STATES.all else ATS_STATES.LOCAL_UNKNOWN_ATS_STATE
            sms.sent_at = timezone.now()
            sms.save()
