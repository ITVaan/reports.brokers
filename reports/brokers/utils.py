# coding=utf-8
from ConfigParser import SafeConfigParser


def get_root_pwd():
    conf_parser = SafeConfigParser()
    conf_parser.read("auth.ini")
    return conf_parser.get("Database", "root_password")
