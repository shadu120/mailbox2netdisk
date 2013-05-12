#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import sys

'''return a unicode string'''
def getUnicodeArgv(str):
    try:
        rs = str.decode('utf-8')
    except:
        try:
            rs = str.decode('gbk')
        except:
            rs = str
    return rs

