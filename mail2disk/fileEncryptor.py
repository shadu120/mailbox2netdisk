#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import shlex, subprocess
import os,sys
from zeander.md5c import getFileMD5
import dba

class fileEncryptor():
    _sPassWord       = ''
    _sSourceFileName = ''
    _sTargetFileName = ''
    _sRARPath        = ''
    _sRARPath_NT     = "c:\\Program Files\\WinRAR\\RAR.EXE"
    _sRARPath_POSIX  = "/usr/bin/rar"
    
    def __init__(self, filename, password = ''):
        self._sSourceFileName = filename
        self._sPassWord       = password
        self._sRARPath        = self._getRARPath()
    
    '''
    Check RAR  tool has been installed
    '''
    def _checkRARInstall(self):
        return os.path.exists(self._sRARPath)
    
    '''
    return RAR tool's path or get from user input
    '''
    def _getRARPath(self):
        if os.name == 'nt':
            self._sRARPath = self._sRARPath_NT
        elif os.name == 'posix':
            self._sRARPath = self._sRARPath_POSIX
        if not self._checkRARInstall():
            print 'Default RAR Tools not found'
            rarPath = dba.getRARPathFromDB()
            if not os.path.exists(rarPath):
                return self._askRARPathInput()
            else:
                self._sRARPath = rarPath
        return self._sRARPath
    
    def _askRARPathInput(self):
        while True:
            RARPath = raw_input("Please input WinRAR Command Full Path\n(eg. c:\\Program Files\\WinRAR\\RAR.EXE or /usr/bin/rar ):")
            if not os.path.exists(RARPath):
                continue
            else:
                self._sRARPath = RARPath
                dba.addRARPathToDB(self._sRARPath)
                return self._sRARPath
    
    '''
    encrypt a file by given target RAR name
    '''
    def getRarFile(self, TargetFileName):
        self._sTargetFileName = TargetFileName
        if not os.path.exists(self._sSourceFileName) or not os.path.exists(self._sRARPath):
            return False
        rarCommand = "\"%s\" a" % self._sRARPath
        if not self._sPassWord == '':
            rarCommand = rarCommand + " -hp%s " % self._sPassWord
        rarCommand = rarCommand + " %s \"%s\" " % (self._sTargetFileName, self._sSourceFileName)
        #print rarCommand
        print 'Encrypting file with RAR...'
        p = subprocess.Popen(rarCommand, shell=True)
        p.wait()
        if not os.path.exists(self._sTargetFileName):
            return False
        return True

    '''
    decrypt a file by given target file name from RAR
    '''
    def getUnRarFile(self, targetFileName):
        if not os.path.exists(self._sSourceFileName) or not os.path.exists(self._sRARPath):
            return False
        rarCommand = "\"%s\" e " % self._sRARPath
        if not self._sPassWord == '':
            rarCommand = rarCommand + " -p%s "  % self._sPassWord
        rarCommand = rarCommand + " -o+ \"%s\"" % self._sSourceFileName
        #print rarCommand
        print 'Decrypting file with RAR....'
        p = subprocess.Popen(rarCommand, shell=True)
        p.wait()
        if not targetFileName == '':
            if not os.path.exists(targetFileName):
                return False
        return True

if __name__ == '__main__':
    fc = fileEncryptor(sys.argv[1], '2')
    fc.getUnRarFile('rar')
