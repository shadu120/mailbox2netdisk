#!/usr/bin/env python
# encoding:utf-8
import hashlib
import md5
import sys

'''get md5 of a given file'''
def getFileMD5(filename):
    strMD5 = ''
    fHandle = None
    readStep = 1024 * 1024 * 5L
    
    try:
        fHandle = open(filename, 'rb')
        md5c = hashlib.md5()
        bRead = ''
        while True:
            bRead = fHandle.read(readStep);
            if not bRead:
                break;
            md5c.update(bRead);
        strMD5 = md5c.hexdigest();
    except IOError:
        pass
    except Exception, e:
        print e
    finally:
        if fHandle: fHandle.close()
    return strMD5

'''get md5 of a binary content'''
def getBinaryContentMD5(bContent):
    strMD5 = ''
    try:
        md5c = hashlib.md5();
        md5c.update(bContent);
        strMD5 = md5c.hexdigest();
    except:
        pass
    return strMD5

if "__main__" == __name__:
    strPath = raw_input("please input some file:");
    print(getFileMD5(strPath));
