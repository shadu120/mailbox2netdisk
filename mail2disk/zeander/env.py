#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import sys,os
from encode import getUnicodeArgv

'''covert every args to unicode'''
def encodeArgs():
    for i in range (0, len(sys.argv)):
        sys.argv[i] = getUnicodeArgv(sys.argv[i])

'''prepare to init'''
def initEnv():
    reload(sys)
    sys.setdefaultencoding('utf-8')
#    encodeArgs()
    try:
        clear = (os.name == 'nt' and os.system('cls')) or (os.name == 'posix' and os.system('clear'))
    except:
        pass

if __name__ == '__main__':
    initEnv()
    for argv in sys.argv:
        print argv,'---',isinstance(argv,unicode)
