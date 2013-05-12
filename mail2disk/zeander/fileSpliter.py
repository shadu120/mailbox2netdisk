#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import os
import sys
from md5c import getFileMD5, getBinaryContentMD5


class Spliter():
    lSingeFileMBSize         = 5L                # 单个文件大小
    _lReadSizeLimit          = 1024 * 1024 * 5L  # lSingeFileMBSize * 1024 * 1024
    _iAutoIncrementIDBegin   = 10001
    _iAutoIncrementIDEnd     = 10001
    _sTempFolder             = './tmp/'          # 临时文件夹
    _sBigFileHash            = ''                # 大文件Hash
    _sBigFileSourceFullName  = ''                # 大文件原始文件名全路径
    _sBigFileSourceBaseName  = ''                # 大文件简单文件名
    _ListSplitedFiles        = []                # [[10001,'./tmp/ABCD1234.10001.q2d', '0000000000'],]
    _bSplitedResult          = False
    
    def __init__(self, filename):
        self._sBigFileSourceFullName = filename
    
    '''prepare before splite'''
    def _prepareSplit(self):
        self._lReadSizeLimit         = self.lSingeFileMBSize * 1024 * 1024
        self._createTempFolder()
        self._sBigFileHash = getFileMD5(self._sBigFileSourceFullName)
    
    '''create temp folder'''
    def _createTempFolder(self):
        if not os.path.exists(self._sTempFolder):
            try:
                os.mkdir(self._sTempFolder)
            except:
                self._sTempFolder = './'
    
    '''split'''
    def runSplit(self):
        print self._sBigFileSourceFullName
        if not os.path.exists(self._sBigFileSourceFullName): return False
        self._prepareSplit()
        self._splitBigFile()
        if self._checkSplitedResult():
            self._bSplitedResult = True
        return self._bSplitedResult
    
    '''split big file'''
    def  _splitBigFile(self):
        sequenceid  = 0
        fHandle     = None
        try:
            fHandle = open(self._sBigFileSourceFullName, 'rb')
            bRead   = fHandle.read(self._lReadSizeLimit)
            while len(bRead) > 0:
                splitedid       = self._iAutoIncrementIDBegin + sequenceid
                splitedFileName = self._generateSplitedFileName(splitedid)
                self._createSplitedFile(splitedFileName, bRead)
                
                splitedFile = [splitedid, splitedFileName, getBinaryContentMD5(bRead), len(bRead)]
                self._ListSplitedFiles.append(splitedFile)
                
                sequenceid = sequenceid + 1
                bRead      = fHandle.read(self._lReadSizeLimit)
        except IOError:
            pass
        except Exception, e:
            print e
        finally:
            if fHandle: fHandle.close()
        self._iAutoIncrementIDEnd = self._iAutoIncrementIDBegin + sequenceid

    '''create splite file by filename and binary content'''
    def _createSplitedFile(self, filename, bContent):
        fHandle = None
        try:
            fp = open(filename, 'wb')
            fp.write(bContent)
        except IOError:
            pass
        except Exception,e:
            print e
        finally:
            fp.close()
    
    '''generate splitefile name by id'''
    def _generateSplitedFileName(self, splitedid):
        return '%s%s.%d.q2d' % (self._sTempFolder, self._sBigFileHash, splitedid)
    
    '''check file splited result'''
    def _checkSplitedResult(self):
        if not (self._iAutoIncrementIDEnd - self._iAutoIncrementIDBegin) == len(self._ListSplitedFiles): return False
        for splitedFile in self._ListSplitedFiles:
            splitedFileName = splitedFile[1]
            if not os.path.exists(splitedFileName): return False
        return True

    '''return big file info list'''
    def getBigFileInfo(self):
        if not self._bSplitedResult: return None
        fullfilename        = self._sBigFileSourceFullName
        filename            = os.path.basename(self._sBigFileSourceFullName)
        filesize            = os.path.getsize(self._sBigFileSourceFullName)
        filemtime           = os.path.getmtime(self._sBigFileSourceFullName)
        filehash            = self._sBigFileHash
        return [fullfilename, filename, filehash, filesize, filemtime]
    
    '''retuen splited files info list'''
    def getSplitedFilesList(self):
        if not self._bSplitedResult: return None
        return self._ListSplitedFiles
        #[sequenceid, splitedFileName, getBinaryContentMD5(bRead), len(bRead)]
    
if __name__ == '__main__':
    x = Spliter(sys.argv[1])
    x.runSplit()
    print x.getBigFileInfo()
    print x.getSplitedFilesList()
