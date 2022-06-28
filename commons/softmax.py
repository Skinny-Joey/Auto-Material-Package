import numpy as np


def softmax(x):
    """Compute the softmax of vector x."""
    exp_x = np.exp(x)
    softmax_x = exp_x / np.sum(exp_x)
    return softmax_x


def softmax_round2(x):
    """对softmax的结果保留两位小数"""
    x = softmax(x)
    x = [round(float(i), 2) for i in x]
    return x
