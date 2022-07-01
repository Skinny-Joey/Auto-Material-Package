# -*- coding: utf-8 -*-
import base64


def image_to_base64(path):
    with open(path, "rb") as f:
        # b64encode是编码，b64decode是解码
        base64_data = base64.b64encode(f.read())
        # base64.b64decode(base64data)
        return base64_data


if __name__ == '__main__':
    print(image_to_base64('../data/temp_picture/带括号的图片.jpg'))
