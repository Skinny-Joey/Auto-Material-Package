# coding=gbk
import sys

sys.path.insert(0, sys.path[0] + '/../')
from commons import content_wash,request
import  pandas as pd
import time
from tqdm import tqdm

import re
pattern = re.compile(r'[\(|（].*[\)|）]')
str = '美丽新世界（1'
result = pattern.search(str)

df = pd.read_csv('网易acr对比文档.csv', encoding='gbk')
wy_asr = []

# for i in tqdm(range(len(df))):
#     request.post_video_extract('SY00N3GO16MBSL9', df.iat[i, 3])
#     time.sleep(0.5)
#
# time.sleep(180)
#
# audio_url = []
# for i in tqdm(range(len(df)), desc='get video-audio'):
#     url = request.get_video_extract('SY00N3GO16MBSL9', df.iat[i, 3])
#     audio_url.append(url)
#     time.sleep(0.5)
#
# df['audio_url'] = audio_url
# df.to_csv('网易acr对比文档.csv', encoding='gbk')
# time.sleep(1200)

# for i in range(len(df)):
#     audio_url.append(df.iat[i, 3][:-1]+'3')

# sn = []
# for url in tqdm(audio_url, desc='post audio text'):
#     response = request.post_audio_text('SY00N3GO16MBSL9', url)
#     sn.append(response)
#     time.sleep(0.5)
#
# df['sn'] = sn
# df.to_csv('网易acr对比文档.csv', encoding='gbk')
# time.sleep(1200)


for i in range(len(df)):
    results = request.get_audio_text(df.iat[i, 7], df.iat[i, 6])
    res = ''
    if not results:
        wy_asr.append('')
        continue
    for r in results:
        res += r['onebest']
    wy_asr.append(res)
# for url, s in tqdm(zip(audio_url, sn), desc='get audio text'):
#     results = request.get_audio_text(s, url)
#     wy_asr.append(results)
#     time.sleep(0.5)

df['网易ASR'] = wy_asr
df.to_csv('网易acr对比文档.csv', encoding='gbk')
