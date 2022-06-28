# coding=gbk
import sys

sys.path.insert(0, sys.path[0] + '/../')
from commons import content_wash,request
import  pandas as pd
import time
from tqdm import tqdm


df = pd.read_csv('asr对比测试文档.csv', encoding='gbk')
wy_asr = []

# for i in tqdm(range(len(df))):
#     request.post_video_extract('SY00N3GO16MBSL6', df.iat[i, 2])
#     time.sleep(0.5)

audio_url = []
# for i in tqdm(range(len(df)), desc='get video-audio'):
#     url = request.get_video_extract('SY00N3GO16MBSL6', df.iat[i, 2])
#     audio_url.append(url)
#     time.sleep(0.5)

for i in range(len(df)):
    audio_url.append(df.iat[i, 2][:-1]+'3')

# for url in tqdm(audio_url, desc='post audio text'):
#     request.post_audio_text('SY00N3GO16MBSL6', url)
#     time.sleep(0.5)



for url in tqdm(audio_url, desc='get audio text'):
    results = request.get_audio_text('SY00N3GO16MBSL6', url)
    wy_asr.append(results)
    time.sleep(0.5)

df['网易ASR'] = wy_asr
df.to_csv('asr对比测试文档.csv', encoding='gbk')
