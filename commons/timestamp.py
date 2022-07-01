import time
import random


def generate_timestamp():
    # 生成当前的时间戳，并加上1位随机数作为生成记录的key
    millis = str(int(time.time() * 1000))
    millis += str(random.randint(0, 9))
    return millis
