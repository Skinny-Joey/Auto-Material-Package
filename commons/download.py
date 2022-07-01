import sys
sys.path.insert(0, sys.path[0] + '/../')
import os
import requests
import os
from conf.params import args
from commons.get_logger import get_logger
from commons.timestamp import generate_timestamp


logger = get_logger(args.log)


def do_load_media(url, path):
    """
    接收以.mp4结尾的视频url，并下载
    :param url:
    :param path:
    :return:
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4146.4 Safari/537.36',
            'Connection': 'close'}
        pre_content_length = 0
        # 循环接收视频数据
        requests.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False
        while True:
            # 若文件已经存在，则断点续传，设置接收来需接收数据的位置
            if os.path.exists(path):
                headers['Range'] = 'bytes=%d-' % os.path.getsize(path)

            res = requests.get(url, stream=True, headers=headers)

            content_length = int(res.headers['content-length'])
            # 若当前报文长度小于前次报文长度，或者已接收文件等于当前报文长度，则可以认为视频接收完成
            if content_length < pre_content_length or (
                    os.path.exists(path) and os.path.getsize(path) == content_length) or content_length == 0:
                break
            pre_content_length = content_length

            # 写入收到的视频数据
            with open(path, 'ab') as file:
                file.write(res.content)
                file.flush()
                # logger.info('下载成功,file size : %d   total size:%d' % (os.path.getsize(path), content_length))
                break
    except Exception as e:
        logger.info(e)
        # logger.info(e)
        pass


def load_media(video_url):
    """
    下载视频并删除多余文件
    """
    path = video_url.split('/')[-1]
    existed_file = os.listdir(args.picture_download_path)  # 文件夹中所有的视频名称
    for file_name in existed_file:
        if path in file_name:
            logger.info('视频已下载过')
            path = args.picture_download_path + file_name  # 获取已下载的视频路径
            return path

    path = args.picture_download_path + generate_timestamp() + '_' + path
    if len(existed_file) > args.temp_picture_num:
        logger.info('视频存储已达上限')
        # 则删除最早的一个视频
        early_time = int(existed_file[0].split('_')[0])
        early_filename = existed_file[0]
        for file_name in existed_file:
            timestamp = int(file_name.split('_')[0])
            if timestamp < early_time:
                early_time = timestamp
                early_filename = file_name
        logger.info('删除最早的视频：' + early_filename)
        os.remove(args.picture_download_path + early_filename)

    logger.info('开始下载……')
    do_load_media(video_url, path)
    return path


def you_get(url, file_name=None, fold_path=None):
    """
    接收以.html为结尾的视频链接，对视频内容进行爬取
    :param url:
    :param file_name:
    :param fold_path:
    :return:
    """
    command = 'you-get'
    if file_name:
        command += ' -O ' + file_name
    if fold_path:
        command += ' -o ' + fold_path
    command += ' ' + url
    os.system(command)


if __name__ == '__main__':
    load_media()
    # you_get('https://yiyouliao.com/api-server/rss/cfbb9cc6a512/item/VI0126KPKE5SA20.html', 'VI0126KPKE5SA20', '../data/')
    pass

