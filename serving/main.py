# -*- coding: utf-8 -*-
import sys
import torch
sys.path.insert(0, sys.path[0] + '/../')
from commons import request, content_wash
from model.predict import prepare_model, predict
from commons.softmax import softmax_round2
from sentence_transformers.util import cos_sim
from sentence_transformers import SentenceTransformer as SBert
from commons.get_logger import get_logger
from conf.params import *
import time
import socket

socket.setdefaulttimeout(5)


def filter_keywords(candidates, filter_words):
    for cand in candidates:
        for f_w in filter_words:
            if f_w in cand.get('filter_content'):
                cand['invalid_word'] = True
                break
        if not cand.get('invalid_word'):
            cand['invalid_word'] = False
    candidates = [cand for cand in candidates if not cand['invalid_word']]
    return candidates


def filter_low_quality(candidates, cnn_model, device):
    for cand in candidates:
        output, label_pre = predict(cnn_model, device, cand['filter_content'])
        # output = softmax_round2(output)
        cand['quality'] = label_pre  # output[1]是文章为正样本的概率, label_pre判断该文章是好文章还是坏文章
    candidates = [cand for cand in candidates if cand['quality']]
    return candidates


def filter_tag(candidates, package_detail):
    for cand in candidates:
        tags = request.post_tag(title=cand.get('title'), content=cand.get('filter_content'))
        if not tags:
            # 如果车险包中可能会出现一个标也没打出来的情况，先放过 todo
            cand['invalid_tag'] = False
            continue
        for tag in tags:
            if package_detail.get('name')[:-1] not in tag.get('tagName'):
                cand['invalid_tag'] = True
                break
        if not cand.get('invalid_tag'):
            cand['invalid_tag'] = False
    candidates = [cand for cand in candidates if not cand['invalid_tag']]
    return candidates


def calculate_title_cos(candidates, sentence_transformers):
    for cand in candidates:
        title = sentence_transformers.encode(cand['title'])
        content = sentence_transformers.encode(cand['filter_content'])
        cand['filter_content_embedding'] = content
        cand['title_embedding'] = title
        cosine_score = cos_sim(title, content)
        cand['title_cos'] = cosine_score
    return candidates


def calculate_author_ratio(pac_articles, package_detail):
    author_ratio = {}
    amount = 0
    for art in pac_articles:
        amount += 1
        author_ratio[art['authorId']] = author_ratio.get(art['authorId'], 0) + 1
    for key in author_ratio:
        author_ratio[key] /= amount
    package_detail['author_ratio'] = author_ratio
    return package_detail


def calculate_des_cos(package_detail, candidates, sentence_transformers):
    description = False
    for package_des in all_description:
        if package_detail.get('name') == package_des.package:
            description = []
            for des in package_des.description:
                description.append(sentence_transformers.encode(des))
            break
    if not description:
        description = [sentence_transformers.encode(package_detail['description'].split()[0])]
    for cand in candidates:
        cand['desc_cos'] = []
        for des in description:
            d_c = cos_sim(des, cand['filter_content_embedding'])  # 计算相似度
            cand['desc_cos'].append(d_c)
    return candidates


def calculate_final_score(candidates, package_detail):
    for cand in candidates:  # todo
        cand['score'] = []
        for d_c in cand['desc_cos']:
            # 部分包具有多个描述，需要计算多次描述与文章内容的相关度
            score = 0.3 * package_detail['author_ratio'].get(cand.get('authorId'), 0) + \
                    0.5 * d_c + \
                    0.2 * cand['title_cos']

            cand['score'].append(score)
    return candidates


def update_single_package(package_id, cnn_model, device, sentence_transformers, logger, filter_words):
    """
        更新单个包
    """
    # logger.info('请求素材包信息')
    # packages = request.get_packages()  # 素材包信息
    # if not packages:
    #     logger.info('请求超时')
    #     return
    # packages_articles = []
    # for pac in packages:
    #     logger.info('请求素材包中内已有文章，素材包ID: ' + str(pac.get('packageInfo').get('id')))
    #     pac_article = request.get_package_article(package_id=pac.get('packageInfo').get('id'))
    #     packages_articles.append(pac_article)  # 素材包中已有的文章
    # if None in packages_articles:
    #     logger.info('请求超时')
    #     return

    # 从接口中请求需要的数据
    logger.info('1-请求素材包中内已有文章视频，素材包ID: ' + package_id)
    pac_articles = request.get_package_article(package_id=package_id)  # 素材包中已有的文章
    if not pac_articles:
        logger.info('请求超时')
        return

    logger.info('2-请求素材包中的细节（如描述）')
    package_detail = request.get_package_detail(package_id=package_id)  # 备选的素材池文章
    if not package_detail:
        logger.info('请求超时')
        return

    logger.info('3-请求备选的素材池文章视频')
    candidates = request.get_candidate(package_id=package_id)  # 备选的素材池文章
    if not candidates:
        logger.info('请求超时')
        return

    logger.info('4-根据备选ID得到备选文章视频')
    logger.info('5-过滤备选文章中的html')
    logger.info('6-发送将备选视频转化为音频的请求')
    for cand in candidates:
        detail = request.get_detail(id=cand['infoId'])
        time.sleep(1)
        if detail:
            cand['authorId'] = detail['authorId']
            if 'article' == detail['contentType']:
                cand['content'] = detail['content']
                cand['filter_content'] = content_wash.filter_tags(cand['content'])  # 清除html后的文本
            else:
                cand['videoUrl'] = detail['videoUrl']
                cand['is_post_video_extract_success'] = request.post_video_extract(cand['infoId'], cand['videoUrl'])

    logger.info('7-接收将备选视频转化为音频的结果')
    for cand in candidates:
        if cand.get('is_post_video_extract_success'):
            cand['audio_url'] = request.get_video_extract(cand['infoId'], cand['videoUrl'])

    logger.info('8-发送将音频转化为文本的请求')
    for cand in candidates:
        if cand.get('audio_url'):
            time.sleep(2)  # todo
            cand['text_id'] = request.post_audio_text(cand['infoId'], cand['audio_url'])

    logger.info('等待30s')
    time.sleep(120)

    logger.info('9-接收音频转文本的结果')
    for cand in candidates:
        if cand.get('text_id'):
            # 视频转文本得到的结果和普通的过滤掉html的文章同样命名为filter_content，因为后续对于他们的操作是一样的，用相同的命名方便处理
            text_result = request.get_audio_text(cand['text_id'], cand['audio_url'])
            if text_result:
                cand['filter_content'] = ''
                for t in text_result:
                    cand['filter_content'] += t['onebest']

    # 正式开始处理
    logger.info('过滤长度过短的文章')
    candidates = [cand for cand in candidates if
                  cand.get('filter_content') and
                  (len(cand['filter_content']) > args.min_length or
                   'article' != cand['contentType'])]

    # candidates = [cand for cand in candidates if cand.get('contentType') != 'article']  # todo 只保留视频（调试用）

    logger.info('过滤掉包含产品名称和公司名称的内容')
    candidates = filter_keywords(candidates, filter_words)

    logger.info('过滤掉低质量文章，使用textCNN计算备选文章质量')
    candidates = filter_low_quality(candidates, cnn_model, device)

    if package_detail.get('name') in args.tag_filter_package:
        logger.info('对部分素材包，使用打标功能，过滤掉其他不属于该保险种类的文章')
        candidates = filter_tag(candidates, package_detail)

    # 过滤完成后若没有内容剩余，则直接返回空
    if not candidates:
        logger.info('所有内容均不符合条件，全部被过滤，返回空值')
        return [], []

    logger.info('开始计算指标')

    logger.info('指标1：使用sentenceTransformer计算标题与文章内容的相关性')
    candidates = calculate_title_cos(candidates, sentence_transformers)

    logger.info('指标2：计算素材包中已有文章的历史作者投稿比例')
    package_detail = calculate_author_ratio(pac_articles, package_detail)

    logger.info('指标3：使用sentenceTransformer计算文章和素材包描述之间的相似度')
    candidates = calculate_des_cos(package_detail, candidates, sentence_transformers)

    logger.info('指标计算完成，综合所有指标，加权求和所有的分数')
    candidates = calculate_final_score(candidates, package_detail)

    # 取出分数最高的n个备选文章和n个备选视频
    # 因为部分包具有多个描述，导致每条内容可能具有多个分数，根据最终需要的文章量和视频量，平均分配在每组分数中要选取的文章量和视频量
    if len(candidates[0]['score']) > 1:
        single_article_num = int(args.require_article_num / len(candidates[0]['score']))
        single_video_num = int(args.require_video_num / len(candidates[0]['score']))
        each_article_num = []
        each_video_num = []
        for _ in range(len(candidates[0]['score'])):
            each_article_num.append(single_article_num)
            each_video_num.append(single_video_num)
        each_article_num[0] += args.require_article_num - sum(each_article_num)
        each_video_num[0] += args.require_video_num - sum(each_video_num)
    else:
        each_article_num = [args.require_article_num]
        each_video_num = [args.require_video_num]

    selected_article = []
    selected_video = []
    for score_index, current_require_article_num, current_require_video_num in zip(range(len(candidates[0]['score'])),
                                                                                   each_article_num, each_video_num):
        candidates = sorted(candidates, key=lambda cand: cand['score'][score_index], reverse=True)
        current_selected_article = [cand for cand in candidates if 'article' == cand['contentType']][
                                   :current_require_article_num * 2]
        current_selected_video = [cand for cand in candidates if 'article' != cand['contentType']][
                                 :current_require_video_num * 2]

        # TODO 计算每个cand与其他cand之间的相似度
        for i in range(len(current_selected_article)):
            if 'diversity' not in current_selected_article[i]:
                current_selected_article[i]['diversity'] = []
            avg_embedding = torch.mean(
                torch.tensor([cand['filter_content_embedding'] for cand in current_selected_article if
                              cand['infoId'] != current_selected_article[i]['infoId']]), dim=0)
            sim = cos_sim(current_selected_article[i]['filter_content_embedding'], avg_embedding)
            current_selected_article[i]['diversity'].append(sim)

        for i in range(len(current_selected_video)):
            if 'diversity' not in current_selected_video[i]:
                current_selected_video[i]['diversity'] = []
            avg_embedding = torch.mean(
                torch.tensor([cand['filter_content_embedding'] for cand in current_selected_video if
                              cand['infoId'] != current_selected_video[i]['infoId']]), dim=0)
            sim = cos_sim(current_selected_video[i]['filter_content_embedding'], avg_embedding)
            current_selected_video[i]['diversity'].append(sim)

        current_selected_article = sorted(current_selected_article, key=lambda cand: cand['diversity'][score_index],
                                          reverse=False)

        current_selected_video = sorted(current_selected_video, key=lambda cand: cand['diversity'][score_index],
                                        reverse=False)

        for cand in current_selected_article:
            selected_article.append('https://market.yiyouliao.com/v2/content-detail/article/' + cand['infoId'])
            candidates.remove(cand)
        for cand in current_selected_video:
            selected_video.append('https://market.yiyouliao.com/v2/content-detail/article/' + cand['infoId'])
            candidates.remove(cand)

    return selected_article, selected_video


if __name__ == '__main__':
    logger = get_logger(args.log)
    net, device = prepare_model()
    sentence_transformers = SBert(args.sentence_transformers)
    sentence_transformers.max_seq_length = 64
    allpackage = request.get_packages()
    filter_words = []
    for filter_file in args.filter_words:
        with open(filter_file, encoding='utf-8') as f:
            line = f.readline()[:-1]
            filter_words.append(line)
            while line:
                line = f.readline()[:-1]
                filter_words.append(line)
    filter_words = [f_w for f_w in filter_words if f_w]
    if allpackage:
        # allpackage = allpackage[-2:]  # todo
        package_ids = [{'id': p['packageInfo']['id'], 'name': p['packageInfo']['name']} for p in allpackage]
        for i in package_ids:
            f = open('aaa.txt', 'a', encoding='utf-8')
            f.write(i['name'] + ':\n')
            selected_article, selected_video = update_single_package(package_id=i['id'],
                                                                     cnn_model=net,
                                                                     device=device,
                                                                     sentence_transformers=sentence_transformers,
                                                                     logger=logger,
                                                                     filter_words=filter_words)
            f.write('文章：\n')
            for s in selected_article:
                f.write(s + '\n')
            f.write('视频：\n')
            for s in selected_video:
                f.write(s + '\n')
