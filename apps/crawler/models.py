# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from netfields import CidrAddressField, NetManager


class RangeIP(models.Model):
    created_time = models.DateTimeField(auto_now_add=True)
    inet = CidrAddressField(blank=True)

    objects = NetManager()

    @property
    def network(self):
        return self.inet.network
