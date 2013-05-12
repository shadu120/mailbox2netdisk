#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import sys

'''返回一个Unicode编码的字符串'''
def getUnicodeArgv(str):
    try:
        rs = str.decode('utf-8')
    except:
        try:
            rs = str.decode('gbk')
        except:
            rs = str
    return rs

