# encoding=utf-8
import sys
sys.path.insert(0, sys.path[0] + '/../')
import requests
import json
from conf.params import *
from commons.get_logger import get_logger


logger = get_logger(args.log)


def http_get(url, params, headers):
    if len(params) > 0:
        url += '?'
        for key in params:
            url += key + '=' + str(params[key]) + '&'
        url = url[:-1]
    response = requests.get(url=url, headers=headers)
    return response


def get_package_article(package_id=None, content_type=None):
    """
        根据素材包ID从素材包中取出文章
    """
    url = get_article_param.url
    params = get_article_param.params.copy()
    if content_type:
        params['contentType'] = content_type
    if package_id:
        params['materialPackageId'] = package_id

    headers = get_article_param.headers.copy()
    logger.info('开始请求 url: ' + url + ' params: ' + str(params) + ' headers: ' + str(headers))
    for _ in range(args.max_request_num):
        try:
            response = http_get(url, params, headers)
            response = json.loads(response.text).get('data').get('records')
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def get_packages():
    """
        获取所有素材包的信息，主要是ID
    """
    url = get_packages_param.url
    params = get_packages_param.params.copy()

    headers = get_packages_param.headers.copy()
    logger.info('开始请求 url: ' + url + ' params: ' + str(params) + ' headers: ' + str(headers))
    for _ in range(args.max_request_num):
        try:
            response = http_get(url, params, headers)
            response = json.loads(response.text).get('data').get('records')
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def get_candidate(package_id=None):
    """
        获取备选池中文章的ID
    """
    url = get_candidate_param.url
    params = get_candidate_param.params.copy()
    headers = get_candidate_param.headers.copy()
    if package_id:
        params['materialPackageId'] = package_id
    for _ in range(args.max_request_num):
        try:
            response = http_get(url, params, headers)
            response = json.loads(response.text).get('data').get('records')
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def get_detail(id=None):
    """
        根据ID获取文章或视频内容
    """
    url = get_article_detail_param.url
    params = get_article_detail_param.params.copy()
    headers = get_article_detail_param.headers.copy()
    if id:
        url = url.replace('xxxxxxxxxx', id)
    for _ in range(args.max_request_num):
        try:
            response = http_get(url, params, headers)
            response = json.loads(response.text).get('data')
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def get_package_detail(package_id=None):
    """
        得到包的细节信息
    """
    url = get_package_detail_param.url
    params = get_package_detail_param.params.copy()
    headers = get_package_detail_param.headers.copy()
    if package_id:
        url = url.replace('xxxxxxxxxx', package_id)
    for _ in range(args.max_request_num):
        try:
            response = http_get(url, params, headers)
            response = json.loads(response.text).get('data').get('packageInfo')
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def post_video_extract(info_id=None, video_url=None):
    """
        发送视频转音频的请求
    """
    data = {'infoId': info_id, 'videoUrl': video_url}
    url = video_extract_param.url
    params = video_extract_param.params
    headers = video_extract_param.headers
    for _ in range(args.max_request_num):
        try:
            response = requests.post(url, data=json.dumps(data), headers=headers, params=params)
            response = json.loads(response.text)
            if response.get('code') != 0 and response.get('code') != 10003:
                raise Exception
            logger.info('请求成功: 第' + str(_) + '次')
            return True
            # response = json.loads(response.data)
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def get_video_extract(info_id=None, video_url=None):
    """
        得到视频转音频的结果
    """
    url = video_extract_param.url
    params = video_extract_param.params.copy()
    headers = video_extract_param.headers.copy()
    if info_id:
        params['infoId'] = info_id
    if video_url:
        params['videoUrl'] = video_url
    for _ in range(args.max_request_num):
        try:
            response = http_get(url, params, headers)
            response = json.loads(response.text).get('data').get('audioUrl')
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def post_audio_text(info_id=None, audio_url=None):
    """
        发送音频转文本的请求
    """
    data = {'infoId': info_id, 'url': audio_url}
    url = audio_text_param.url
    params = audio_text_param.params.copy()
    headers = audio_text_param.headers.copy()
    for _ in range(args.max_request_num):
        try:
            response = requests.post(url, data=data, headers=headers, params=params)
            response = json.loads(response.text)
            if not response.get('success'):
                raise Exception
            logger.info('请求成功: 第' + str(_) + '次')
            return response.get('message')
            # response = json.loads(response.data)
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def get_audio_text(sn=None, audio_url=None):
    """
        得到音频转文本的结果
    """
    url = audio_text_result_param.url
    params = audio_text_result_param.params.copy()
    headers = audio_text_result_param.headers.copy()
    if sn:
        params['sn'] = sn
    if audio_url:
        params['url'] = audio_url
    for _ in range(args.max_request_num):
        try:
            response = http_get(url, params, headers)
            response = json.loads(response.text).get('data').get('data')
            if not response:
                raise Exception
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None


def post_tag(title='', content='', industry='保险行业'):
    """
    得到文章的标签
    """
    url = post_tag_param.url
    params = post_tag_param.params
    headers = post_tag_param.headers
    data = {'title': title, 'content': content, 'industry': industry}
    for _ in range(args.max_request_num):
        try:
            response = requests.post(url, json=data, headers=headers, params=params)
            response = json.loads(response.text).get('data')
            response = [tag for tag in response if tag.get('categoryName') == '保险险种']
            if not response:
                raise Exception
            logger.info('请求成功: 第' + str(_) + '次')
            return response
        except Exception:
            logger.info('请求失败: 第' + str(_) + '次')
    return None



if __name__ == '__main__':
    # articleinpackage = get_package_article(package_id='3eddf3d46f284909cc9dc4855ea722d0')
    allpackage = get_packages()
    # package_ids = [{'id': p['packageInfo']['id'], 'name': p['packageInfo']['name']} for p in allpackage]
    # candidate = get_candidate(package_id='3eddf3d46f284909cc9dc4855ea722d0')
    # article_detail = get_detail(id='IC00P2DBRWDT968')
    # package_detail = get_package_detail(package_id='338f53c2ddf612aee8c9728cd141e591')
    # #
    # pass
    # a=post_video_extract('VI00P3TUN6NRBZG', 'http://supermarket-video.yiyouliao.com/08ee87837f5601d3f6d594f79fdd83aa.mp4')
    # if a:
    #     b=get_video_extract('VI00P3TUN6NRBZG', 'http://supermarket-video.yiyouliao.com/08ee87837f5601d3f6d594f79fdd83aa.mp4')
    #     c=post_audio_text('VI00P3TUN6NRBZG', b)
    #     d=get_audio_text(c, b)
    # pass

    # result = post_tag(title='寿险是什么?寿险的意义与功用是什么?',
    #                   content='寿险，即人寿保险，是一种以人的生死为保险目标的保险。是被保险人在保险条款期内生存或死亡，由保险人根据契约要求给付保险金的一种保险。　　依照经营范围来划分，寿险包含生存保险、死亡保险和两全保险。依照保障期限来划分，寿险可分成定期寿险和终身寿险。热卖的万能险，也是终身寿险的一种。　　但是由于受制于传统观念的原因，大伙儿针对死亡这一话题讨论是很忌讳的，乃至我们在和粉丝探讨寿险时也尽量少提或是用别的词句代替。受制于此，也造成 现阶段寿险在国内还很不受重视，但小编感觉有必要提一下。今日小编就根据一篇文章，多方位来拆解“寿险”，解答你有关寿险的疑问，一起发现它的美。')

    data = get_detail('VC0126V23F8DQ6G')

    pass
