from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class InputATSSMSmessage(models.Model):

    created_at = models.DateTimeField(verbose_name=_('created at'), null=False, blank=False, auto_now_add=True)
    received_at = models.DateTimeField(verbose_name=_('received at'), null=False, blank=False)
    uniq = models.PositiveIntegerField(verbose_name=_('uniq'), null=False, blank=False, unique=True)
    sender = models.CharField(verbose_name=_('sender'), null=False, blank=False, max_length=20)
    recipient = models.CharField(verbose_name=_('recipient'), null=False, blank=False, max_length=20)
    okey = models.CharField(verbose_name=_('okey'), null=False, blank=False, max_length=255)
    opid = models.CharField(verbose_name=_('opid'), null=False, blank=False, max_length=255)
    opmid = models.CharField(verbose_name=_('opmid'), null=False, blank=True, max_length=255)
    content = models.TextField(verbose_name=_('content'), null=False, blank=False)

    def __str__(self):
        return self.sender

    class Meta:
        verbose_name = _('input ATS message')
        verbose_name_plural = _('input ATS messages')
