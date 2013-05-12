#!/usr/bin/python env
# -*- coding: UTF-8 -*-

import imaplib2
import smtplib
import mimetypes
import email
import email.mime.application
import dba
import os
from zeander.md5c import getFileMD5

IMAP4_PORT = 143
IMAP4_SSL_PORT = 993

class imapDisk():
    _imap = None
    _imap_user = ''
    _imap_pass = ''
    _imap_server = ''
    _imap_port = IMAP4_PORT
    _imap_ssl_port = IMAP4_SSL_PORT
    _imap_vendor = 'vendor'

    imap_id         = 0
    imap_mailfrom   = 'shadu@foxmail.com'
    imap_mailto     = 'shadu@foxmail.com'
    imap_diskname   = 'M2D'
    imap_mailsize   = 0
    imap_SSLEnable  = True
    
    _tmpfolder = './tmp'
    
    def __init__(self):
        if not os.path.exists(self._tmpfolder):
            os.mkdir(self._tmpfolder)
        pass

    def allocateIMAPServer(self, splitedfileid):
        self.imap_id = dba.allocateIMAPServer(splitedfileid)
        if self.imap_id == 0:
            return False
        (self._imap_server, self._imap_port, self._imap_ssl_port, self._imap_user, self._imap_pass, self._imap_vendor) = dba.getIMAPConfig(self.imap_id)
        if 'None' == self._imap_user:
            return False
        self.imap_mailfrom  = self._imap_user
        self.imap_mailto    = self._imap_user
        if self._imap_ssl_port > 0:
            self.imap_SSLEnable = True
        return True
        
    def setIMAPConfig(self, server, port, sslport, username, password, vendor):
        self._imap_server = server
        self._imap_port = port
        self._imap_ssl_port = sslport
        self._imap_user = username
        self._imap_pass = password
        self._imap_vendor = vendor
        
    def checkAccout(self):
        return self._login()
        
    def _login(self):
        if self.imap_SSLEnable and self._imap_ssl_port > 0:
            self._imap = imaplib2.IMAP4_SSL(self._imap_server, port = self._imap_ssl_port)
        else:
            self._imap = imaplib2.IMAP4(self._imap_server, port = self._imap_port)
        try:
            t,d = self._imap.login(self._imap_user, self._imap_pass)
            if t == 'OK':
                return True
            else:
                return False
        except Exception , e:
            print e
            return False
        
    def _createNetDiskFolder(self):
        if not self._imap:
            if not self._login():
                return False
        t,d = self._imap.create(self.imap_diskname)
        return t == 'OK'
    
    def checkNetDiskFolder(self):
        if not self._imap:
            if not self._login():
                return False
        t,d = self._imap.select(self.imap_diskname)
        if t == 'OK':
            return True
        return self._createNetDiskFolder()
        
    def _file2email(self, filename, subject, bodycontent):
        msg = email.mime.Multipart.MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = self.imap_mailfrom
        msg['To'] = self.imap_mailto

        body = email.mime.Text.MIMEText(bodycontent)
        msg.attach(body)

        try:
            fp=open(filename,'rb')
            att = email.mime.application.MIMEApplication(fp.read(),_subtype="m2d")
            fp.close()
            att.add_header('Content-Disposition','attachment',filename=filename)
            msg.attach(att)
            return msg.as_string()
        except:
            return ''
        
    def uploadFile(self, filename):
        if not os.path.exists(filename):
            return 0
        imapuid = 0
        if not self._imap:
            if not self._login():
                return imapuid
        subject = 'M2D: %s' % filename
        bodycontent = 'M2D: %s' % filename
        message = self._file2email(filename, subject, bodycontent)
        self.imap_mailsize = len(message) # 邮件大小
        t,d = self._imap.append(self.imap_diskname, None, None, message)
        if not t == 'OK':
            return imapuid
        #print d
        return self._getIMAPUIDFromUploadMessage(d)

    def _getIMAPUIDFromUploadMessage(self, msg):
        imapuid = 0
        if self._imap_vendor == '163' or self._imap_vendor == 'qq':
            imapuid = long(msg[0].split(']')[0].split(' ')[-1])
        else:
            imapuid = long(msg[0].split(']')[0].split(' ')[-1])
        #print msg,imapuid
        return imapuid
        
    def download(self, imapuid, splitedfilename, splitedfilehash):
        if not self._imap:
            if not self._login():
                return False
        t,d = self._imap.select(self.imap_diskname)
        if not t == 'OK':
            print 'self._imap.select(self.imap_diskname)'
            return False
        t,d = self._imap.uid('FETCH', imapuid, '(RFC822)')
        if not t == 'OK':
            print 'imap uid search failure..'
            return False
        email_body = d[0][1]
        mail = email.message_from_string(email_body)
        for part in mail.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            #filename = part.get_filename()
            fp = open(splitedfilename, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()
        #print splitedfilename
        if not os.path.exists(splitedfilename):
            print 'file downloaded but not exists'
            return False
        tmpHash = getFileMD5(splitedfilename)
        if not tmpHash == splitedfilehash:
            print 'imapDisk hash failure..'
            return False
        return True
    
    def delete(self, imapuid):
        if not self._imap:
            if not self._login():
                return False
        t,d = self._imap.select(self.imap_diskname)
        if not t == 'OK':
            print 'self._imap.select(self.imap_diskname) failure'
            return False
        t,d = self._imap.uid('STORE', imapuid,  '+FLAGS', "(\\Deleted)")
        if not t == 'OK':
            return True # mail might been delete from other client or web
        t,d = self._imap.expunge()
        return t == 'OK'
    
    def close(self):
        try:
            self._imap.close()
            self._imap.logout()
        except:
            pass
            
    def _checkIMAPFolder(self):
        return True

if __name__ == '__main__':
    imapdisk = imapDisk()
    imapdisk.checkNetdiskFolder()
