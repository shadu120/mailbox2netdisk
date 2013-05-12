#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import sys
import os
import time
import getpass
import dba
import imapDisk
from zeander.fileSpliter import Spliter
from fileEncryptor import fileEncryptor
from zeander.md5c import getFileMD5

class M2D:
    SingleFileMBSize       = 5
    bEncryptRemoteFile     = False
    OriginalFileFullName   = ''
    RemoteFolderName       = '/'
    
    
    _TimeBegin = 0
    _TimeEnd   = 0
    
    _spliter = None
    
    _BigFileId             = 0
    _OriginalFileSize      = 0L
    _OriginalFileHash      = ''
    _OriginalFileBaseName  = ''
    _OriginalFileMTime     = ''
    _RemoteFileName        = ''
    _RemoteFileHash        = ''
    _RemoteRarPassword     = ''
    _LocalTempFullName     = ''
    _ProcessedByteSize     = 0
    
    _imapReady = False
    
    
    def __init__(self):
        self._TimeBegin = time.time()
        self._checkIMAPConfig()
    
    def __del__(self):
        self._TimeEnd = time.time()
        if not self._TimeEnd == 0:
            print '\nTime used     : %.1f minutes' % ((self._TimeEnd - self._TimeBegin) / 60)
            if not self._ProcessedByteSize == 0:
                print "Data processed: %.3f MB processed" % (float(self._ProcessedByteSize) / 1024 /1024)
                print "Average speed : %.3f KB/s" % (float(self._ProcessedByteSize) / (self._TimeEnd - self._TimeBegin) / 1024)
        
    '''检查IMAP服务器是否配置'''
    def _checkIMAPConfig(self):
        if dba.checkIMAPConfig():
            self._imapReady = True
        else:
            self._configIMAPServer()
    
    '''配置IMAP服务器参数'''
    def _configIMAPServer(self) :
        print 'Welcome to use IMAP2Disk :)\nThank you for adding the IMAP configure!\nFor your account security, the IMAP Server must support SSL'
        while True:
            imap_vendor = raw_input('\nVendor(eg. 163,QQ,Microsoft):')
            if not len(imap_vendor) > 0:
                print 'invalid Vendor string..'
                continue
            imap_server = raw_input('Server(eg. imap.163.com)    :')
            if not len(imap_server) > 3:
                print 'invalid Server string..'
                continue
            #imap_port = raw_input('Port(eg. Enter with default 143):')
            imap_port = 143
            imap_sslport = raw_input('SSL Port(eg. default 993)   :')
            if imap_sslport == '':
                imap_sslport = '993'
            imap_username = raw_input('UserName(eg. xxx@163.com)   :')
            if not len(imap_username) > 0:
                print 'invalid UserName string..'
                continue
            imap_password = getpass.getpass('Password                    :')
            if not len(imap_password) > 0:
                print 'invalid Password string..'
                continue
            imap_disklimit = raw_input('DiskLimit(GB,eg. 20)        :')
            if imap_disklimit == '' or not int(imap_disklimit) > 0:
                print 'invalid DiskLimit value..'
                continue
            print '\n\n%s|%s|%s|%s|******|%sGB' % (imap_vendor, imap_server, imap_sslport, imap_username,imap_disklimit)
            confirm = raw_input('\nAre you sure(y/n):')
            if not confirm.upper() == 'Y':
                continue
            imapdisk = imapDisk.imapDisk()
            imapdisk.setIMAPConfig(imap_server, int(imap_port), int(imap_sslport),imap_username, imap_password, imap_vendor)
            print 'Verifing your IMAP parameters...'
            if imapdisk.checkAccout() and imapdisk.checkNetDiskFolder():
                print 'OK :)\n'
                if dba.addIMAPConfig(imap_server, int(imap_port), int(imap_sslport),imap_username, imap_password, int(imap_disklimit), imap_vendor):
                    self._imapReady = True
                    print 'Config saved successfully, continue your task..'
                else:
                    print 'Config saved failed...\n'
                print '-----------------------------------------\n'
                break
            else:
                print 'For some reason, your configure can not work correctly :(\n'
    
    def _initOriginalFileInfo(self):
        self._OriginalFileBaseName = os.path.basename(self.OriginalFileFullName)
        self._OriginalFileMTime    = '%.6f' % os.path.getmtime(self.OriginalFileFullName)
        self._OriginalFileSize     = os.path.getsize(self.OriginalFileFullName)
        self._OriginalFileHash     = getFileMD5(self.OriginalFileFullName)
        self._LocalTempFullName    = self.OriginalFileFullName
        self._RemoteFileName       = self._OriginalFileBaseName
        self._BigFileId            = self._checkFileIsInDBByHash(self._OriginalFileHash);
        
    '''断点上传数据库中所有还未完成的任务'''
    def uploadAll(self):
        FileIDsToUpload = dba.getBigFilesIdToUpload()
        for bigfileid in FileIDsToUpload:
            self._uploadBigFileById(bigfileid)
    
    '''上传指定ID的大文件,死循环逻辑检查..........'''
    def _uploadBigFileById(self, bigfileid):
        print 'Uploading Big File Id: %d' % bigfileid
        splitedfileids = dba.getSplitedFilesIdToUpload(bigfileid)
        uploadedIDs = []
        while len(uploadedIDs) <  len(splitedfileids):
            countUploaded = 0
            countToUpload = len(splitedfileids) - len(uploadedIDs)
            print "At least %d files need to upload" % countToUpload
            
            for splitedfileid in splitedfileids:
                if splitedfileid in uploadedIDs: continue  # had been uploaded
                splitedfilename = dba.getSplitedFileNameById(splitedfileid)
                
                imapdisk = imapDisk.imapDisk()
                if not imapdisk.allocateIMAPServer(splitedfileid):
                    print 'allocateIMAPServer failure'
                    continue
                imapuid = 0
                try:
                    print "(%3d/%-3d) uploading splited file : %d | %s" % (countUploaded + 1, countToUpload, splitedfileid, splitedfilename)
                    imapuid = imapdisk.uploadFile(splitedfilename)
                except Exception, e:
                    print e
                if not 0 == imapuid:
                    dba.updateSplitedFileIMAPInfo(splitedfileid, imapdisk.imap_id, imapuid, imapdisk.imap_mailsize)                 # update upload status
                    dba.updateIMAPServerInfo(imapdisk.imap_id, imapdisk.imap_mailsize)                      # update disk usage
                    uploadedIDs.append(splitedfileid)
                    countUploaded           = countUploaded + 1
                    self._ProcessedByteSize = self._ProcessedByteSize + imapdisk.imap_mailsize
                imapdisk.close()
                imapdisk = None
            splitedfileids = dba.getSplitedFilesIdToUpload(bigfileid)
        print 'splited files upload finished'
        self._finishBigFileUpload(bigfileid)  ### big file upload finished
      
    '''上传文件到网盘'''
    def upload(self):
        if not os.path.exists(self.OriginalFileFullName): return
        if not self._imapReady: return
        self._initOriginalFileInfo()
        if self._BigFileId > 0:
            if self._checkFileUploadedById(self._BigFileId):
                print 'File has been uploaded, exit...\n'
            else:
                print 'Big file exitst in DB, try to upload splited files\n'
                self._uploadBigFileById(self._BigFileId)
        else:
            print 'new file to upload :)\n'
            if self.bEncryptRemoteFile == True:
                if not self._EncryptBigFile():
                    print 'RAR Encrypted failed...'
                    return
            self._BigFileId = self._splitBigFile()
            if self._BigFileId > 0:
                self._uploadBigFileById(self._BigFileId)
            else:
                print 'Big file splited failure...\n'
    
    '''上传前加密文件'''
    def _EncryptBigFile(self):
        self._RemoteRarPassword = self._OriginalFileHash
        fE = fileEncryptor(self.OriginalFileFullName, self._RemoteRarPassword)
        self._RemoteFileName    = time.strftime('%Y%m%d%H%m%S') + '.rar'
        self._LocalTempFullName = self._RemoteFileName
        if not fE.getRarFile(self._RemoteFileName):
            self._RemoteFileName    = time.strftime('%Y%m%d%H%m%S') + '.q2d'
            self._LocalTempFullName = self._RemoteFileName
            self._RemoteRarPassword = ''
            return False
        return True

        
    '''数据库中是否有该文件'''    
    def _checkFileIsInDBByHash(self, hash):
        return dba.checkFileIsInDBByHash(hash)
    
    '''判断大文件是否已经上传'''    
    def _checkFileUploadedById(self, bigfileid):
        return dba.checkFileUploadedById(bigfileid)
    
    '''分割大文件 '''
    def _splitBigFile(self):
        print '...........spliting big file...........'
        fS = Spliter(self._LocalTempFullName)
        fS.lSingeFileMBSize = self.SingleFileMBSize
        if not fS.runSplit(): return 0
        #[RemoteFileName, RemoteFileBaseName, RemoteFileHash, RemoteFileSize, RemoteFileMName]
        BigFileInfo = fS.getBigFileInfo()
        if None == BigFileInfo: return 0
        BigFileInfo.append(self._OriginalFileBaseName)
        BigFileInfo.append(self._OriginalFileHash)
        BigFileInfo.append(self._OriginalFileSize)
        BigFileInfo.append(self._OriginalFileMTime)
        BigFileInfo.append(self._RemoteRarPassword)
        BigFileInfo.append(self.RemoteFolderName)
        bigfileid = dba.addBigFileRecord(BigFileInfo)
        if 0 == bigfileid: return 0
        SplitedFilesInfo = fS.getSplitedFilesList()
        if None == SplitedFilesInfo: return 0
        if dba.addSplitedFilesRecord(bigfileid, SplitedFilesInfo):
            return bigfileid
        else:
            return 0
    
    '''完成大文件上传，设置状态并清除文件'''
    def _finishBigFileUpload(self, bigfileid):
        dba.finishBigFileUpload(bigfileid)
        dba.cleanSplitedFilesByBigFileId(bigfileid)
        print 'Big file uploaded successfully!'
        if not self._RemoteRarPassword == '':
            print 'Please delete the temp file %s manually' % self._RemoteFileName
    
    '''下载文件'''
    def download(self, bigfileid):
        if not self._imapReady: return
        splitedfileslist = dba.getSplitedFilesListByBigFileId(bigfileid)
        if not len(splitedfileslist) > 0: return False
        print 'Downloading Big file: %s' % splitedfileslist[0][1]

        if self._downloadSplitedFiles(splitedfileslist):
            if self._rebuid(splitedfileslist):
                print 'Download successfully!'
                self._RemoteRarPassword  = splitedfileslist[0][9]
                self._RemoteFileName     = splitedfileslist[0][5]
                self._OriginalFileHash   = splitedfileslist[0][2]
                if '' != self._RemoteRarPassword :
                    fE = fileEncryptor(self._RemoteFileName, self._RemoteRarPassword)
                    if fE.getUnRarFile(self._OriginalFileBaseName) and getFileMD5(self._OriginalFileBaseName) == self._OriginalFileHash:
                        self._cleanDownloadTempFiles()
                        return True
                else:
                    if getFileMD5(self._OriginalFileBaseName) == self._OriginalFileHash:
                        self._cleanDownloadTempFiles()
                        return True
        return False
    
    '''清除下载过程中产生的临时文件'''
    def _cleanDownloadTempFiles(self,splitedfileslist):
        print 'rebuid successfully,cleaning temp files...'
        for splitedfile in splitedfileslist:
            splitedfilename = splitedfile[12]
            if os.path.exists(splitedfilename) :
                os.remove(splitedfilename)
        print 'Download temp files has been cleaned.'
            
    '''根据小文件列表，下载分割的小文件'''
    def _downloadSplitedFiles(self, splitedfileslist):
        print '%d files to download from IMAP server ' % len(splitedfileslist)
        downloadedSplitedFiles = []
        while(len(downloadedSplitedFiles) < len(splitedfileslist)):
            imapdisk = imapDisk.imapDisk()
            currentIMAPId = 0
            for fileinfo in splitedfileslist:
                (bigfileid,original_filename,original_filehash,original_filesize,original_filemtime,remote_filename,remote_filehash,remote_filesize,remote_folder,remote_rarpassword,remote_uploadtime, splitedfileid,splitedfilename,splitedfilehash,splitedfilesize,splitedfilemailsize,splitedfilesequenceid,imapid, imapuid,server,port,sslport,username,password,diskname,disklimit,diskused,vendor) = fileinfo
                # this file has been downloaded
                if not splitedfileid in downloadedSplitedFiles:
                    if not currentIMAPId == imapid:
                        imapdisk.close()
                        currentIMAPId = imapid
                        imapdisk.setIMAPConfig(server, port, sslport,username, password, vendor)
                    if imapdisk.download(imapuid, splitedfilename, splitedfilehash):
                        downloadedSplitedFiles.append(splitedfileid)
                        self._ProcessedByteSize = self._ProcessedByteSize + splitedfilemailsize
                        print 'Progress: %d/%d| Filename:%s' % (len(downloadedSplitedFiles), len(splitedfileslist), splitedfilename)
            imapdisk.close()
            imapdisk = None
        return True
    
    '''重新组合小文件为大文件'''
    def _rebuid(self,splitedfileslist):
        self._RemoteFileName = splitedfileslist[0][5]
        self._RemoteFileHash = splitedfileslist[0][6]
        try:
            fpbig = open(self._RemoteFileName, 'wb')
            for fileinfo in splitedfileslist:
                splitedfilename = fileinfo[12]
                fpsplited = open(splitedfilename, 'rb')
                fpbig.write(fpsplited.read())
                fpsplited.close()
            fpbig.close()
        except:
            return False
        tmpHash = getFileMD5(self._RemoteFileName)
        if not tmpHash == self._RemoteFileHash:
            print 'Remote file hash error..'
            return False
        return True
        
    '''列出网盘文件清单'''
    def list(self):
        filesList = dba.getBigFilesList()
        if not len(filesList) > 0:
            print 'No files in DataBase'
            return
        print ' +--------+-+------------+---------------------+-------------------------------------------------+'
        print ' |%7s |%s|  %s  |      %s     |                     %s                    |' % ('FileId', 'S', 'Size(MB)', 'FolderName', 'FileName' )
        print ' +--------+-+------------+---------------------+-------------------------------------------------+'
        for bigfile in filesList:
            (bigfileid, filename , filesize, filemtime,  foldername, fileuploaded)  = bigfile
            if fileuploaded == 1:
                status = 'Y'
            else:
                status = 'Y'
            #filename = 'AAAAAAAAAAAAAAAAAAABBBBBBVVVVVKK'
            if len(filename) > 50:
                filename = '%s...%s' % (filename[:40],filename[-10:-4])
            print ' |%8d|%s|%12.3f|%-20s |%-49s|' % (bigfileid, status, float(filesize)/1024/1024, foldername, filename )
        print ' +--------+-+------------+---------------------+-------------------------------------------------+'

    '''从网盘中删除指定ID的文件'''
    def delete(self, bigfileid):
        if not self._imapReady:
            return
        splitedfileslist = dba.getSplitedFilesListByBigFileId(bigfileid)
        if not len(splitedfileslist) > 0:
            return False
        print 'Deleting Big file: %s' % splitedfileslist[0][1]
        if self._deleteSplitedFiles(splitedfileslist):
            print 'File has been deleted ...'
            return True
        return False
    
    def _deleteSplitedFiles(self, splitedfileslist):
        print '%d emails on server to delete' % len(splitedfileslist)
        imapdisk       = imapDisk.imapDisk()
        #currentIMAPId  = splitedfileslist[0][16]
        currentIMAPId  = 0
        spfIDs_deleted = []
        while(len(spfIDs_deleted) < len(splitedfileslist)):
            for fileinfo in splitedfileslist:
                (bigfileid,original_filename,original_filehash,original_filesize,original_filemtime,remote_filename,remote_filehash,remote_filesize,remote_folder,remote_rarpassword,remote_uploadtime, splitedfileid,splitedfilename,splitedfilehash,splitedfilesize,splitedfilemailsize,splitedfilesequenceid,imapid, imapuid,server,port,sslport,username,password,diskname,disklimit,diskused,vendor) = fileinfo
                if splitedfileid in spfIDs_deleted:
                    continue
                if not currentIMAPId == imapid:
                    imapdisk.close()
                    currentIMAPId = imapid
                    imapdisk.setIMAPConfig(server, port, sslport,username, password, vendor)
                if imapdisk.delete(imapuid):
                    print 'IMAP UID deleted : %d (%d/%d)' % (imapuid, len(spfIDs_deleted) + 1, len(splitedfileslist))
                spfIDs_deleted.append(imapuid)
        imapdisk.close()
        imapdisk = None           
        return dba.deleteBigFileById(splitedfileslist[0][0])

            
'''帮助'''
def showHelp():
    print '''
@desc   Make your IMAP Server to NetDisk
@author shadu#foxmail.com

Encrypy remote file with -p parameter, with RAR tool installed before

UPLOAD   : mail2disk.py upload <LocalFilePath> <RemoteFolder> [-p]
example  : mail2disk.py upload d:\\movie\\test.mp4 /tools/

DOWNLOAD : mail2disk.py download <fileid>
example  : mail2disk.py download 903644

DELETE   : mail2disk.py delete <fileid>
example  : mail2disk.py delete 903644

LISTFILES: mail2disk.py list
example  : mail2disk.py list
'''
    sys.exit()


if __name__ == '__main__':
    clear = (os.name == 'nt' and os.system('cls')) or (os.name == 'posix' and os.system('clear'))
    initEnv()
    if not len(sys.argv) > 1:
        showHelp()
        
    if sys.argv[1] == 'upload' and len(sys.argv) > 3:
        if not os.path.exists(sys.argv[2]) or not os.path.getsize(sys.argv[2]) > 0:
            print 'File not exists or is empty...'
            sys.exit()
        m2d = M2D()
        m2d.OriginalFileFullName  = sys.argv[2]
        m2d.RemoteFolderName      = sys.argv[3]
        m2d.SingleFileMBSize      = 5             # 依据当前网速，单个文件5M比较合适
        if len(sys.argv) > 4 and sys.argv[4] == '-p':
            m2d.bEncryptRemoteFile = True
        m2d.upload()
        
    elif sys.argv[1] == 'download' and len(sys.argv) == 3:
        m2d = M2D()
        bigfileid  = int(sys.argv[2])
        m2d.download(bigfileid)
        
    elif sys.argv[1] == 'delete' and len(sys.argv) == 3:
        m2d = M2D()
        bigfileid  = int(sys.argv[2])
        m2d.delete(bigfileid)
        
    elif sys.argv[1] == 'list':
        m2d = M2D()
        m2d.list()
        
    else:
        showHelp()
