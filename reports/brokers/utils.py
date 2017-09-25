# -*- coding: utf-8 -*-
from ConfigParser import SafeConfigParser
from logging import getLogger

from pkg_resources import get_distribution

PKG = get_distribution(__package__)
LOGGER = getLogger(PKG.project_name)
VERSION = '{}.{}'.format(int(PKG.parsed_version[0]),
                         int(PKG.parsed_version[1]) if PKG.parsed_version[1].isdigit() else 0)
USERS = {}
ROUTE_PREFIX = '/api/{}'.format(VERSION)
default_error_status = 403


def get_root_pwd():
    conf_parser = SafeConfigParser()
    conf_parser.read("auth.ini")
    return conf_parser.get("Database", "root_password")
