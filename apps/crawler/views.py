# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import connection


def ip_in_range(ip):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT (*) FROM crawler_rangeip WHERE inet >> %s", [ip])
    return cursor.rowcount > 0
