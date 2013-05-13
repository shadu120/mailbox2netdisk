#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from mail2disk.zeander.env import initEnv
from mail2disk.zeander.encode import getUnicodeArgv
from mail2disk.mail2disk import M2D
from optparse import OptionParser, OptionGroup

def cmdParse():
    usage="%prog [options] args ... "
    version="\nMailbox2Netdisk (v1.0) by sshadu@foxmail.com on May 5th, 2013\n"
    description = "Welcome to use this <Mailbox To Netdisk> tool.You can use your email's mailbox as a net disk by IMAP protocol.For your email accout's security, your email server must support IMAP SSL.download address:https://github.com/shadu120/mailbox2netdisk"
    parser = OptionParser(usage=usage, version=version)
    parser.set_description(description)
    parser.add_option("-l", "--list",     action="store_true",  dest="list",                                             help="list files in net disk,include the id of each file.")
    parser.add_option("-c", "--continue", action="store_true",  dest="continues",                                        help="continue to upload all the unfinished files for network disconnect or other reasons.")
    parser.add_option("-d", "--download", action="store",       dest="download", type="int",    metavar="FILE_ID",       help="download a file from net disk by given file id")
    parser.add_option("-r", "--remove",   action="store",       dest="remove",   type="int",    metavar="FILE_ID",       help="remove a file from net disk by given file id")
    parser.add_option("-u", "--upload",   action="store",       dest="upload",   type="string", metavar="FILE_NAME",     help="uploade a file to net disk, eg: c:\\test\\test.mp3")

    group = OptionGroup(parser, "upload parameters",  
                    "important parameters when \"-u\" is using.")  
    group.add_option("-f", "--folder",   action="store",       dest="folder",  type="string", metavar="REMOTE_FOLDER", help="which folder you want to store the file on net disk,eg: /video/, default is /.", default="/")
    group.add_option("-s", "--size"  ,   action="store",       dest="size"    ,type="int",    metavar="SIZE",          help="splited file size in MB, default is 2. this depends on your email attachment limits and your network quality", default=2)
    group.add_option("-e", "--Encrypt"  ,action="store_true",  dest="encrypt" ,                                        help="encrypt the file before storing to net disk")
    group.add_option("-v", "--Verify"   ,action="store_true",  dest="verify" ,                                         help="verify the splited files after uploading.this will cost you much more time.Unfortunately, this fucntion has not been implemented now.")

    parser.add_option_group(group)
    (options, args) = parser.parse_args()

    if options.list:
        M2D().list()
    elif options.continues:
        M2D().uploadAll()
    elif options.download:
        if options.download > 0:
            M2D().download(options.download)
        else:
            print 'invalid file id'
    elif options.remove:
        if options.remove > 0:
            M2D().delete(options.remove)
        else:
            print 'invalid file id'
    elif options.upload:
        filename = getUnicodeArgv(options.upload)
        if not os.path.exists(filename) or not os.path.getsize(filename) > 0:
            print 'File not exists'
            return
        m2d = M2D()
        m2d.OriginalFileFullName = filename
        if not options.folder.endswith('/'):
            m2d.RemoteFolderName = options.folder + "/"
        else:
            m2d.RemoteFolderName = options.folder
        m2d.SingleFileMBSize     = options.size
        m2d.bEncryptRemoteFile   = (options.encrypt == True)
        m2d.upload()
    else:
        parser.print_help() 
        


if __name__ == '__main__':
    initEnv()
    cmdParse()
