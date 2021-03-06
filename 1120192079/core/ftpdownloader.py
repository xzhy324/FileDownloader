import ftplib
import os
import logging


class FtpDownloader:
    def start_task(self, host, username, password, remotefile, localpath):
        _ftpDownload(host, username, password, remotefile, localpath)


def _ftpDownload(host, username, password, remotefile, localpath, port=21):
    # 连接ftp远程服务器
    ftp = ftplib.FTP()
    try:
        ftp.connect(host, port)
        ftp.login(username, password)
    except ftplib.all_errors as e:
        logging.error("Cannot Connect to FTP Server! Reason: %s" % e)
        return
    # 获取文件名以及本地的文件完整路径
    filename = os.path.basename(remotefile)
    localfile = os.path.join(localpath, filename)

    if os.path.exists(localfile):
        logging.error("[ftpDownload]:localfile already exists")
        return

    with open(localfile, 'wb') as fp:
        ftp.retrbinary("RETR %s" % remotefile, fp.write)
    logging.info("[ftpDownload]:download completed!")
