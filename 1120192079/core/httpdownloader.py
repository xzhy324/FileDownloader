import requests
import os
from tqdm import tqdm
import logging
from concurrent import futures
import threading
import time
import exrex


# 多线程下载时供执行体对象调用的分段下载函数
def _download_by_range(lock, url, segment_id, start, end, target_filename):
    """
    :param lock: 对磁盘的互斥读写锁
    :param url:文件链接
    :param segment_id:分段号
    :param start:开始字节
    :param end:结束字节
    :param target_filename:输出路径
    :return: {'cracked':bool [,'segment_id':int] }
    """
    headers = {'Range': 'bytes=%d-%d' % (start, end)}
    r = requests.get(url=url, headers=headers)
    expected_segment_length = end - start + 1
    if not r or len(r.content) != expected_segment_length:
        logging.error("segment[%d]:bytes=%d-%d failed!" % (segment_id, start, end))
        return {'cracked': True}

    lock.acquire()  # 将内存中下载好的内容保存到磁盘中需要读写锁
    try:
        with open(target_filename, mode='rb+') as fp:
            fp.seek(start)  # 定位到起始字节
            fp.write(r.content)
    except Exception as e:
        logging.error("segment[{}]:bytes={}-{} failed!,Reason:{}".format(segment_id, start, end, e))
        return {
            'cracked': True,
            'segment_id': segment_id
        }
    finally:
        lock.release()

    logging.debug("segment[{}]:bytes={}-{} downloaded!".format(segment_id, start, end))
    return {
        'cracked': False,
        'segment_id': segment_id,
        'seg_size': expected_segment_length
    }


class HttpDownloader:
    settings = {}

    def __init__(self):
        # 对象初始化时完成一次更新
        self.update_settings()

    # 命令行版本全部使用该函数
    # 开始前会从内存的设置字典中检查是否开启了正则表达
    def start_task(self, url: str, output: str, concurrency: int):
        # 从配置文件中加载正则表达式的上限
        regular_limit = int(self.settings.get('template_language'))
        if regular_limit > 0:
            urls = list(exrex.generate(url, regular_limit))
            for single_url in urls:
                self._start_single_task(url=single_url, output=output, concurrency=concurrency)
        else:  # 若为0则表示不开启正则表达，普通处理单个url
            self._start_single_task(url=url, output=output, concurrency=concurrency)

    # GUI版本全部使用该函数
    # 只指定了url，此时的output路径和concurrency线程数从成员字典settings中加载
    def start_default_task(self, url: str):
        output = self.settings.get('output')
        concurrency = int(self.settings.get('concurrency'))
        self._start_single_task(url, output, concurrency)

    # gui和命令行的入口函数均调用该函数，是下载功能的核心函数
    # 指定了output和concurrency，此时按照指定的值下载
    def _start_single_task(self, url: str, output: str, concurrency: int):
        """
        :param url: 下载地址
        :param output: 输出目录
        :param concurrency: 线程数
        :return: None
        """
        #  通过网址形式先判断是否有文件可以下载
        remote_filename = os.path.basename(url)
        if remote_filename is '':
            logging.error("The URL cannot be downloaded!")
            return

        target_filename = os.path.join(output, remote_filename)
        # 判断临时文件是否存在
        if os.path.exists(target_filename):
            logging.error("The File %s has already been created!" % target_filename)
            return

        #  判断url是否是request可以请求的

        try:
            r = requests.head(url)
        except requests.exceptions.RequestException as e:
            logging.error("cannot open url, reason: %s" % e)
            return

        # 判断是否能够正常连接
        if not r:
            logging.error("Get URL headers failed.Task aborted!")
            return

        logging.debug(r.content)

        file_size = r.headers.get('Content-Length')
        if file_size is None:
            logging.info('failed to get content size')  # 注意有些下载无法请求到文件大小，仍可以流式下载
        else:
            file_size = int(file_size)
            logging.debug("file_size %d Bytes" % file_size)

        r = requests.head(url, headers={'Range': 'bytes=0-0'})  # 请求一个字节以判断是否支持range请求

        start_time = time.time()
        # 多线程下载
        if r.status_code == 206:  # 支持range请求
            logging.info("MultiThread Supported! Concurrency:{} ".format(concurrency))
            # 由于 _download_by_range 中使用 rb+ 模式，必须先保证文件存在，所以要先创建指定大小的临时文件 (用0填充)
            mt_chunk_size = int(self.settings['chunk_size'])  # 加载多线程下载中所使用的分块大小
            with open(target_filename, 'wb') as fp:
                fp.seek(file_size - 1)
                fp.write(b'\0')

            # 注意with as 块在结束的时候会调用__exit__方法，而ThreadPoolExecutor的退出函数（.shutdown()）是等待所有的线程任务完成，隐含了一层同步的语义
            with futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                # 计算分块的数量
                tmp_part_count, tmp_mod = divmod(file_size, mt_chunk_size)
                segments = tmp_part_count if tmp_mod == 0 else int(tmp_part_count) + 1
                logging.debug("chunk_count %d Bytes, chunk_mod %d" % (tmp_part_count, tmp_mod))

                lock = threading.Lock()  # 创建互斥文件读写锁
                thread_queue = []  # 线程标记队列
                for segment_id in range(segments):
                    start_byte = segment_id * mt_chunk_size
                    end_byte = start_byte + mt_chunk_size - 1
                    # 注意若当前块为最后一块，则结束字节需要重新指定
                    if segment_id == segments - 1:
                        end_byte = file_size - 1
                    # 对每个线程调用_download_by_range函数，函数的返回值可以通过future对象的result方法得到
                    future = executor.submit(_download_by_range, lock, url, segment_id, start_byte, end_byte,
                                             target_filename)
                    thread_queue.append(future)

                # futures.as_completed([future set]) 返回已经完成任务的线程future
                completed_futures = futures.as_completed(thread_queue)
                with tqdm(
                        unit='B',  # 默认为位，改为字节作为默认单位
                        unit_divisor=1024,  # 将传输速率的单位改为存储字节的单位
                        unit_scale=True,  # 自动扩展单位
                        ascii=True,  # windows下正确显示需要指定显示模式为utf8
                        desc=os.path.basename(target_filename),  # 在进度条前方显示下载的文件名
                        total=file_size) as bar:
                    for future in completed_futures:
                        # result()方法指向回调函数的返回值
                        res = future.result()
                        if res.get("cracked"):
                            logging.error("part {} has cracked".format(res.get("segment_id")))
                        else:
                            bar.update(res.get('seg_size'))

        # 单线程下载
        else:
            logging.info("The HTTP File doesn't support multithreading-download")
            bar = tqdm(
                unit='B',  # 默认为位，改为字节作为默认单位
                unit_divisor=1024,  # 将传输速率的单位改为存储字节的单位
                unit_scale=True,  # 自动扩展单位
                ascii=True,  # windows下正确显示需要指定显示模式为utf8
                desc=target_filename,  # 在进度条前方显示下载的文件名
                total=file_size
            )
            single_response = requests.get(url, stream=True)
            single_response.raise_for_status()
            with open(target_filename, 'wb') as fp:
                for chunk in single_response.iter_content(chunk_size=512):
                    if chunk:  # chunk的大小不为零，继续下载
                        fp.write(chunk)
                        bar.update(len(chunk))

        # 下载完成，提示信息并打印花费时间
        time_gap = time.time() - start_time
        minutes, sec = divmod(time_gap, 60)
        hour, minutes = divmod(minutes, 60)

        if hour == 0 and minutes == 0:
            logging.info("download completed! Total time:%.2fs " % sec)
        elif hour == 0:
            logging.info("download completed! Total time:%dm:%.2fs" % (minutes, sec))
        else:
            logging.info("download completed! Total time:%dh:%02dm:%02ds" % (hour, minutes, sec))

    # 加载配置文件并指定控制台日志的级别
    # 在类对象初始化以及每次修改settings.txt之后，应该调用该函数
    def update_settings(self):
        # default settings
        self.settings['chunk_size'] = 1024
        self.settings['logging.level'] = 'INFO'
        # 加载配置文件
        with open('./settings.txt', 'r', encoding='utf8') as fp:
            for line in fp.readlines():
                line = line.split()
                config_name = line[0]
                config_value = line[1]
                self.settings[config_name] = config_value
        # print(settings)
        logging.basicConfig(level=self.settings['logging.level'],  # 设置日志的默认响应级别为INFO,按需要更改成为debug，默认等级为warning
                            format='[%(asctime)s] %(filename)s:%(lineno)s - [%(levelname)s] %(message)s')  # 规定logging的输出格式
