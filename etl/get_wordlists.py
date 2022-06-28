# -*- coding: utf-8 -*-
"""
将训练数据使用jieba分词工具进行分词。并且剔除stopList中的词。
得到词表：
        词表的每一行的内容为：词 词的序号 词的频次
"""
import sys
sys.path.insert(0, sys.path[0] + '/../')
import jieba
from tqdm import tqdm
import pandas as pd
from conf.params import parse_args


args = parse_args()


def read_stopword(file):
    data = open(file, 'r', encoding='utf_8').read().split('\n')
    return data


def get_wordlists():
    worddict = {}
    stoplist = read_stopword(args.stopwords)
    datas = pd.read_csv(args.train_raw)
    len_dic = {}
    for i in tqdm(range(len(datas)), desc='Build Vocabulary'):
        title = datas.iloc[i, 1]
        title_seg = jieba.cut(title, cut_all=False)
        length = 0
        for w in title_seg:
            if args.filter_stopwords and w in stoplist:
                continue
            length += 1
            if w in worddict:
                worddict[w] += 1
            else:
                worddict[w] = 1
        if length in len_dic:
            len_dic[length] += 1
        else:
            len_dic[length] = 1

    wordlist = sorted(worddict.items(), key=lambda item: item[1], reverse=True)
    f = open(args.word_id, 'w', encoding='utf_8')
    ind = 0
    for t in wordlist:
        d = t[0] + ' ' + str(ind) + ' ' + str(t[1]) + '\n'
        ind += 1
        f.write(d)

    for k, v in len_dic.items():
        len_dic[k] = round(v * 1.0 / len(datas), 3)
    len_list = sorted(len_dic.items(), key=lambda item: item[0], reverse=True)
    f = open(args.length, 'w')
    for t in len_list:
        d = str(t[0]) + ' ' + str(t[1]) + '\n'
        f.write(d)


if __name__ == "__main__":
    get_wordlists()
