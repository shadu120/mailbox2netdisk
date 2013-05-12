#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import sqlite3
import os, sys, time
import inspect
from zeander.md5c import getFileMD5, getBinaryContentMD5

'''返回数据库文件路径'''
def getDBPath():
    this_file = inspect.getfile(inspect.currentframe())
    this_path = os.path.abspath(os.path.dirname(this_file))
    return os.path.join(this_path, 'm2d.db3')

#DATABASE  = 'm2d.db3'
DATABASE = getDBPath()

'''新增大文件记录,并返回其ID'''
def addBigFileRecord(bigfileinfo):
    intFileId = 0
    #[RemoteFileName, RemoteFileBaseName, RemoteFileHash, RemoteFileSize, RemoteFileMName,
    # _OriginalFileBaseName, _OriginalFileHash, _OriginalFileSize, _OriginalFileMTime,
    # _RemoteRarPassword,RemoteFolderName ]
    original_filename   = bigfileinfo[5]
    original_filehash   = bigfileinfo[6]
    original_filesize   = bigfileinfo[7]
    original_filemtime  = bigfileinfo[8]
    remote_filename     = bigfileinfo[1]
    remote_filehash     = bigfileinfo[2]
    remote_filesize     = bigfileinfo[3]
    remote_rarpassword  = bigfileinfo[9]
    remote_folder       = bigfileinfo[10]
    sql1 = "insert into CloudFiles (bigfileid, original_filename, original_filehash, original_filesize, original_filemtime, remote_filename, remote_filehash, remote_filesize, remote_rarpassword, remote_folder) values (null, '%s', '%s', '%s','%s', '%s', '%s', %d, '%s', '%s')" % (original_filename, original_filehash,original_filesize, original_filemtime, remote_filename,remote_filehash, remote_filesize, remote_rarpassword, remote_folder)
    sql2 = "select bigfileid from CloudFiles where original_filehash = '%s'" % original_filehash
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor() 
        ex = cur.execute(sql1)
        conn.commit()
        ex = cur.execute(sql2)
        rs = cur.fetchone()
        intFileId = rs[0]
        conn.close()
        return intFileId
    except Exception, e:
        print e
        print sql1
        print sql2

'''添加新的分割文件记录'''
def addSplitedFilesRecord(bigfileid, SplitedFilesInfo):
    #[sequenceid, splitedFileName, getBinaryContentMD5(bRead), len(bRead)]
    sql0 = "insert into CloudSplitedFiles (fileid, sequenceid, filename, filehash, filesize, bigfileid) values ( null, %d, '%s', '%s', %d, %d)"
    try:
        conn = sqlite3.connect(DATABASE)
        cur  = conn.cursor()
        ex   = None
        for fileinfo in SplitedFilesInfo:
            sql = sql0 % (fileinfo[0], fileinfo[1], fileinfo[2], fileinfo[3], bigfileid)
            ex  = cur.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Exception ,e:
        print e
        print sql
        return False

'''分割文件上传成功后，更新imapuid信息'''
def updateCloudFileIMAPStatus(fileid, imapid, imapuid):
    sql = "update CloudSplitedFiles set imapid = %d, imapuid = %d where fileid = %d" % (imapid, imapuid, fileid)
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql)
        conn.commit()
        conn.close()
        return True
    except:
        return False
    

'''根据分割文件的id返回其对应的文件名'''
def getSplitedFileNameById(splitedfileid):
    filename = ''
    sql = "select filename from CloudSplitedFiles where fileid = %d" % splitedfileid
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql)
        rs = cur.fetchone()
        filename = rs[0]
        conn.close()
        return filename
    except:
        return filename
        
        
def getIMAPNetdiskName(imapid):
    netdiskname = 'None'
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        sql = "select netdiskname from IMAPConfig where id = %d" % imapid
        ex = cur.execute(sql)
        rs = cur.fetchone()
        netdiskname = rs[0]
        conn.close()
        return netdiskname
    except:
        return netdiskname
    
def updateIMAPNetdiskName(imapid, netdiskname):
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        sql = "update IMAPConfig set netdiskname = '%s' where id = %d" % (netdiskname, imapid)
        ex = cur.execute(sql)
        conn.commit()
        conn.close()
        return True
    except:
        return False


def allocateIMAPServer(splitedfileid):
    imapid = 0
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        sql = "select IMAPConfig.id from IMAPConfig, CloudSplitedFiles  where CloudSplitedFiles.fileid = %d and (IMAPConfig.disklimit * 1024 * 1024 * 1024 - IMAPConfig.diskused)  > CloudSplitedFiles.filesize order by IMAPConfig.id asc" % splitedfileid
        ex = cur.execute(sql)
        rs = cur.fetchone()
        imapid = rs[0]
        conn.close()
        return imapid
    except:
        return imapid

def getIMAPConfig(imapid):
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        sql = "select server, port, sslport , username, password, vendor from IMAPConfig where id = %d" % imapid
        ex = cur.execute(sql)
        rs = cur.fetchone()
        config = rs
        conn.close()
        return config
    except:
        return ('None',0, 0, 'None', 'None')

def updateSplitedFileIMAPInfo(splitedfileid, imapid, imapuid, mailsize):
    currenttime = time.strftime('%Y%m%d%H%m%S')
    sql = "update CloudSplitedFiles set imapid = %d,  imapuid = %d , uploadtime = '%s', mailsize = %d where fileid = %d" % (imapid, imapuid, currenttime, mailsize, splitedfileid)
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Exception , e:
        print e
        return False

def getBigFilesIdToUpload():
    BigFilesIdToUpload = []
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        sql = "select bigfileid from CloudFiles where remote_uploaded = 0"
        ex = cur.execute(sql)
        rs = cur.fetchall()
        if len(rs) > 0:
            for r in rs:
                BigFilesIdToUpload.append(r[0])
        conn.close()
        return BigFilesIdToUpload
    except Exception , e:
        print e
        return BigFilesIdToUpload

''' To delte '''
def getBigFileIdByFilePwd(pwd):
    bigfileid = 0
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        sql = "select fileid from CloudFiles where filepwd = '%s'" % pwd
        ex = cur.execute(sql)
        rs = cur.fetchone()
        bigfileid = rs[0]
        conn.close()
        return bigfileid
    except Exception , e:
        print e
        return bigfileid
        
        
def getSplitedFilesIdToUpload(bigfileid):
    SplitedFilesIdToUpload = []
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        sql = "select fileid from CloudSplitedFiles where bigfileid = %d and imapid = 0" % bigfileid
        ex = cur.execute(sql)
        rs = cur.fetchall()
        if len(rs) > 0:
            for r in rs:
                SplitedFilesIdToUpload.append(r[0])
        conn.close()
        return SplitedFilesIdToUpload
    except Exception , e:
        print e
        return SplitedFilesIdToUpload

def finishBigFileUpload(bigfileid):
    currenttime = time.strftime('%Y%m%d%H%m%S')
    sql = "update CloudFiles set remote_uploaded = 1, remote_uploadtime = '%s' where bigfileid = %d" % (currenttime, bigfileid)
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Exception , e:
        print e
        print sql
        return False

def cleanSplitedFilesByBigFileId(bigfileid):
    sql = "select filename from CloudSplitedFiles where bigfileid = %d " % bigfileid
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql)
        rs = cur.fetchall()
        if len(rs) > 0:
            for r in rs:
                if os.path.exists(r[0]):
                    os.remove(r[0])
        conn.close()
        return True
    except Exception, e:
        print e
        return False
        
        
def checkFileIsInDBByHash(filehash):
    sql = "select count(*) from CloudFiles where original_filehash = '%s'" % filehash
    count = 0
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor() 
        conn.text_factory=str
        ex = cur.execute(sql)
        rs = cur.fetchone()
        count = rs[0]
        conn.close()
        return count > 0
    except Exception, e:
        print e
        return False

def checkFileUploadedById(bigfileid):
    sql = "select count(*) from CloudFiles where bigfileid = %d and remote_uploaded = 1" % bigfileid
    count = 0
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor() 
        conn.text_factory=str
        ex = cur.execute(sql)
        rs = cur.fetchone()
        count = rs[0]
        conn.close()
        return count > 0
    except Exception, e:
        print e
        return False

        
def updateIMAPServerInfo(imap_id, mailsize):
    sql = "update IMAPConfig set diskused = diskused + %d where id = %d " % (mailsize, imap_id)
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        ex = cur.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Exception , e:
        print e
        return False

def getSplitedFilesListByBigFileId(bigfileid):
    sql = "select CloudFiles.[bigfileid] as bigfileid, CloudFiles.[original_filename], CloudFiles.[original_filehash], CloudFiles.[original_filesize],CloudFiles.[original_filemtime],CloudFiles.[remote_filename], CloudFiles.[remote_filehash], CloudFiles.[remote_filesize],CloudFiles.[remote_folder], CloudFiles.[remote_rarpassword],CloudFiles.[remote_uploadtime], CloudSplitedFiles.[fileid] as splitedfileid, CloudSplitedFiles.[filename] as splitedfilename, CloudSplitedFiles.[filehash] as splitedfilehash, CloudSplitedFiles.[filesize] as splitedfilesize, CloudSplitedFiles.[mailsize] as splitedfilemailsize , CloudSplitedFiles.[sequenceid] as splitedfilesequenceid, CloudSplitedFiles.[imapid], CloudSplitedFiles.[imapuid], IMAPConfig.[server], IMAPConfig.[port], IMAPConfig.[sslport], IMAPConfig.[username], IMAPConfig.[password], IMAPConfig.[diskname], IMAPConfig.[disklimit], IMAPConfig.[diskused], IMAPConfig.[vendor] from CloudFiles, CloudSplitedFiles, IMAPConfig where  IMAPConfig.[id] = CloudSplitedFiles.[imapid] and CloudSplitedFiles.[bigfileid] = CloudFiles.[bigfileid] and CloudFiles.[bigfileid] =%d order by CloudSplitedFiles.[fileid] asc" % bigfileid
    #(bigfileid,original_filename,original_filehash,original_filesize,original_filemtime,remote_filename,remote_filehash,remote_filesize,remote_folder,remote_rarpassword,remote_uploadtime, splitedfileid,splitedfilename,splitedfilehash,splitedfilesize,splitedfilemailsize,splitedfilesequenceid,imapid, imapuid,server,port,sslport,username,password,diskname,disklimit,diskused,vendor)
    #('bigfileid','original_filename','original_filehash','original_filesize','original_filemtime','remote_filename','remote_filehash','remote_filesize','remote_folder','remote_rarpassword','remote_uploadtime','splitedfileid','splitedfilename','splitedfilehash','splitedfilesize','splitedfilemailsize','splitedfilesequenceid','imapid','imapuid','server','port','sslport','username','password','diskname','disklimit','diskused','vendor')
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor() 
        ex = cur.execute(sql)
        rs = cur.fetchall()
        conn.close()
        return rs
    except Exception, e:
        print e
        return False

def getBigFilesList():
    sql = "select bigfileid, original_filename , original_filesize, original_filemtime,  remote_folder, remote_uploaded from CloudFiles order by bigfileid"
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor() 
        conn.text_factory=str
        ex = cur.execute(sql)
        rs = cur.fetchall()
        conn.close()
        if len(rs) > 0:
            return rs
        else:
            return []
    except Exception, e:
        print e
        return []

def checkIMAPConfig():
    sql = "select count(*) from IMAPConfig"
    count = 0
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor() 
        conn.text_factory=str
        ex = cur.execute(sql)
        rs = cur.fetchone()
        count = rs[0]
        conn.close()
        return count > 0
    except Exception, e:
        print e
        return False

def addIMAPConfig(server, port, sslport,username, password, disklimit, vendor):
    sql = "insert into IMAPConfig (id, server, port, sslport, username, password, disklimit,vendor) values (null, '%s', %d, %d , '%s', '%s', %d, '%s')" % (server, port, sslport,username, password, disklimit, vendor)
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        conn.text_factory=str
        ex = cur.execute(sql)
        conn.commit()
        conn.close()
        return True
    except Exception , e:
        print e
        return False

def deleteBigFileById(bigfileid):
    sql1 = 'delete from CloudSplitedFiles where bigfileid = %d' % bigfileid
    sql2 = 'delete from CloudFiles where bigfileid = %d' % bigfileid
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql1)
        ex = cur.execute(sql2)
        conn.commit()
        conn.close()
        return True
    except Exception , e:
        print e
        print sql1, sql2
        return False

def getRARPathFromDB():
    rarpath = ''
    sql = "select rarpath from RARConfig" 
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql)
        rs = cur.fetchone()
        rarpath = rs[0]
        conn.close()
        return rarpath
    except Exception, e:
        print e
        return rarpath
        
def addRARPathToDB(rarpath):
    sql = "insert into RARConfig set rarpath='%s'"   % rarpath
    try:
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        ex = cur.execute(sql)
        cur.commit()
        conn.close()
        return True
    except Exception, e:
        print e
        return False
        
if __name__ == '__main__':
    print deleteBigFileById(966053)
