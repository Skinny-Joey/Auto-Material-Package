import argparse
import os

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def parse_args():
    parser = argparse.ArgumentParser(description='gpt text generation service')

    parser.add_argument('--filter_stopwords', default=False, type=bool, required=False, help='处理文本时是否过滤停词')
    parser.add_argument('--val_raw', default=basedir + '/data/val.csv', type=str, required=False, help='验证集路径')
    parser.add_argument('--word_id', default=basedir + '/data/word_id.txt', type=str, required=False, help='词表路径')
    parser.add_argument('--stopwords', default=basedir + '/data/stopwords.txt', type=str, required=False, help='停词词表路径')
    parser.add_argument('--val_vec', default=basedir + '/data/valdata_vec.txt', type=str, required=False,
                        help='验证集向量路径')
    parser.add_argument('--max_len', default=3000, type=int, required=False, help='输入的最大长度')
    parser.add_argument('--label', default=basedir + '/data/label.txt', type=str, required=False, help='标签路径')
    parser.add_argument('--model', default=basedir + '/data/iter_43_loss_0.01_acc_0.88.pkl', type=str, required=False,
                        help='模型路径')
    parser.add_argument('--log', default=basedir + '/log/auto_package.log', type=str, required=False, help='预测日志路径')
    parser.add_argument('--max_request_num', default=3, type=int, required=False, help='发送请求的最大次数')
    parser.add_argument('--min_length', default=500, type=int, required=False, help='可选文章的最短长度')
    parser.add_argument('--sentence_transformers', default=basedir + '/data/paraphrase-multilingual-MiniLM-L12-v2',
                        type=str, required=False, help='sentence transformer模型路径')
    parser.add_argument('--summary_num', default=3, type=int, required=False, help='计算包的描述和文章标题加前n句的相似度')
    parser.add_argument('--require_article_num', default=5, type=int, required=False, help='需要输出的文章数量')
    parser.add_argument('--require_video_num', default=5, type=int, required=False, help='需要输出的视频数量')
    parser.add_argument('--filter_words', default=[basedir + '/data/保险名称.txt', basedir + '/data/保险公司名称.txt'], type=list, required=False, help='需要过滤的词语列表')
    parser.add_argument('--tag_filter_package', default=['重疾险','医疗险','教育险','养老险','教育险','意外险'], type=list,
                        required=False, help='需要过滤的词语列表')
    parser.add_argument('--picture_download_path', default=basedir+'/data/temp_picture/', type=str, required=False, help='封面图下载路径')
    parser.add_argument('--temp_picture_num', default=20, type=int, required=False, help='可以缓存在本地的封面图数量')
    parser.add_argument('--pattern', default=r'[\(|（].*[\)|）]', type=str, required=False, help='正则匹配括号')

    args = parser.parse_args()

    return args


args = parse_args()

# 模型参数
textCNN_param = {
    'vocab_size': len(open(args.word_id, 'r', encoding='utf_8').read().split('\n')),
    'embed_dim': 60,
    'class_num': len(open(args.label, 'r', encoding='utf_8').read().split('\n')),
    "kernel_num": 16,
    "kernel_size": [2, 5, 10, 20],  # [3, 4, 5]
    "dropout": 0.5,
}


class RequestParam:
    """
        定义http请求发送用到的参数
    """

    def __init__(self, url, params, headers):
        self.url = url
        self.params = params
        self.headers = headers


headers = {'Accept': '*/*',
           'Connection': 'keep-alive',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4146.4 Safari/537.36',
           }

headers_market = headers.copy()
headers_market['token'] = 'd85ac1c30d0741fb9e4a4880309cf25f'
headers_market['Host'] = 'market.yiyouliao.com'

headers_manager = headers.copy()
headers_manager['token'] = '808fa45b8bf44f5abf335e2715b28d47'
headers_manager['Host'] = 'manager.yiyouliao.net'

headers_json = headers.copy()
headers_json['Content-Type'] = 'application/json'

headers_form = headers.copy()
headers_form['Content-Type'] = 'application/x-www-form-urlencoded'

get_article_param = RequestParam(url='https://market.yiyouliao.com/supermarket/contents/',
                                 params={'pageSize': 100,
                                         'pageNo': '1',
                                         'orderBy': 'saleUpdateTime',
                                         },
                                 headers=headers_market)
get_packages_param = RequestParam(url='https://market.yiyouliao.com/supermarket/packages/',
                                  params={'pageNo': 1,
                                          'pageSize': 100,
                                          },
                                  headers=headers_market)
get_candidate_param = RequestParam(url='http://manager.yiyouliao.net/manager/material/package/content',
                                   params={'pageNo': 1,
                                           'pageSize': 100,
                                           'desc': True,
                                           'orderBy': 'saleUpdateTime',
                                           },
                                   headers=headers_manager)
get_article_detail_param = RequestParam(url='https://market.yiyouliao.com/supermarket/content/xxxxxxxxxx/detail',
                                        params={},
                                        headers=headers_market)
get_package_detail_param = RequestParam(url='http://manager.yiyouliao.net/manager/material/package/xxxxxxxxxx',
                                        params={},
                                        headers=headers_manager)
# 视频转音频
video_extract_param = RequestParam(url='http://10.0.0.178:6661/inforec/imgsrv/video/extract/audio/',
                                   params={},
                                   headers=headers_json)

# 音频转文字
audio_text_param = RequestParam(url='http://algorithm.yiyouliao.net/tag/analyse/v2/audio',
                                params={},
                                headers=headers_form)
audio_text_result_param = RequestParam(url='http://algorithm.yiyouliao.net/tag/analyse/audio/result',
                                       params={},
                                       headers=headers)

# 文章打标签
post_tag_param = RequestParam(url='http://test.ai.yiyouliao.net/nlp/tag/industry_tag',
                              params={},
                              headers=headers_json)


class PackageDescription:
    def __init__(self, package, description):
        self.package = package
        self.description = description


package_bao = PackageDescription('宝爸宝妈',
                                 ['孩子教育',
                                  '孩子健康'])

all_description = [package_bao]
