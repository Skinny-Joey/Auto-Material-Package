# -*- coding: utf_8 -*-
import sys
sys.path.insert(0, sys.path[0] + '/../')
from conf.params import parse_args
import jieba
import pandas as pd
from tqdm import tqdm
from etl.get_wordlists import read_stopword


args = parse_args()


def get_worddict(file):
    datas = open(file, 'r', encoding='utf_8').read().split('\n')
    datas = list(filter(None, datas))
    word2ind = {}
    for line in datas:
        line = line.split(' ')
        word2ind[line[0]] = int(line[1])

    ind2word = {word2ind[w]: w for w in word2ind}
    return word2ind, ind2word


word2ind, ind2word = get_worddict(args.word_id)
stoplist = read_stopword(args.stopwords)


def content2inds(content, **cla_ind):
    """
    将文字转化为vec
    :param content: 代转化的内容
    :param cla_ind: 可变标签，是否在向量开头插入分类标签，填入则为训练数据
    :return: 向量
    """
    title_seg = jieba.cut(content, cut_all=False)
    if None != cla_ind.get('cla_ind'):
        title_ind = [cla_ind.get('cla_ind')]
    else:
        title_ind = []
    for w in title_seg:
        if args.filter_stopwords and w in stoplist:
            continue
        if None != word2ind.get(w):
            title_ind.append(word2ind.get(w))
    length = len(title_ind)
    if length > args.max_len + 1:
        title_ind = title_ind[0: args.max_len + 1]
    if length < args.max_len + 1:
        title_ind.extend([0] * (args.max_len - length + 1))
    return title_ind


def data2vec(vec_path, data_path, is_cla):
    """
    将存放原始数据的csv文件转化为向量并存储
    :param vec_path:
    :param data_path:
    :param is_cla: 是否在向量开头加入分类标签（生成训练数据时需要加入，生成预测数据时不需要）
    :return:
    """
    vec_file = open(vec_path, 'w')

    datas = pd.read_csv(data_path)
    datas = datas.sample(frac=1)
    for i in tqdm(range(len(datas)), desc='Process Raw Data into Vec'):
        content = datas.iloc[i, 1]
        cla = datas.iloc[i, 2]
        cla_ind = int(cla)
        if is_cla:
            content_ind = content2inds(content=content, cla_ind=cla_ind)
        else:
            content_ind = content2inds(content=content)
        for n in content_ind:
            vec_file.write(str(n) + ',')
        vec_file.write('\n')
    vec_file.close()


if __name__ == "__main__":
    data2vec(vec_path=args.train_vec, data_path=args.train_raw, is_cla=True)
    data2vec(vec_path=args.val_vec, data_path=args.val_raw, is_cla=False)
