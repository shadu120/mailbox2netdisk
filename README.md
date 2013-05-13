Welcome to use this  <Mailbox To Netdisk> tool.

You can use your email's mailbox as a net disk by IMAP protocol now!

As you know, dropbox is free but its disk space is limited for free user.There also some Internet Companies allow you to use much more space for email services. So, why don't we use the email mailbox as a super net disk?

This small tool can help you to upload ,download, delte and list big files to/on "net disk" by IMAP protocol.

encrypted file uploading is also supported, by using RAR command tool which should be installed on your local system, for example: C:\Program Files\Winrar\rar.exe, or /usr/bin/rar.


OS:Windows/Linux + Python 2.7+


    Usage: m2d.py [options] args ... 

    Welcome to use this <Mailbox To Netdisk> tool.You can use your email's mailbox
    as a net disk by IMAP protocol.For your email accout's security, your email
    server must support IMAP SSL.To get new version , please visit:https://github.com/shadu120/mailbox2netdisk

Options:

    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -l, --list            list files in net disk,include the id of each file.
    -c, --continue        continue to upload all the unfinished files for
                        network disconnect or other reasons.
    -d FILE_ID, --download=FILE_ID
                        download a file from net disk by given file id
    -r FILE_ID, --remove=FILE_ID
                        remove a file from net disk by given file id
     -u FILE_NAME, --upload=FILE_NAME
                        upload a file to net disk, eg: c:\test\test.mp3

  upload parameters:
    important parameters when "-u" is using.

    -f REMOTE_FOLDER, --folder=REMOTE_FOLDER
                        which folder you want to store the file on net
                        disk,eg: /video/, default is /.
    -s SIZE, --size=SIZE
                        splited file size in MB, default is 2. this depends on
                        your email attachment limits and your network quality
    -e, --Encrypt       encrypt the file before storing to net disk.RAR
                        command tool should be installed first, such as
                        "C:\Program Files\WinRAR\RAR.exe" or "/usr/bin/rar"
    -v, --Verify        verify the splited files after uploading.this will
                        cost you much more time.Unfortunately, this fucntion
                        has not been implemented now.


m2d.py --list

    +--------+-+------------+---------------------+------------------------------+
    | FileId |S|  Size(MB)  |      FolderName     |          FileName            |
    +--------+-+------------+---------------------+------------------------------+
    |      62|Y|      35.058|/Audio/Podcast/      |First Impressions Episode.mp3 
    +--------+-+------------+---------------------+------------------------------+


