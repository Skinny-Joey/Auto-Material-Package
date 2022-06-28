import sys
sys.path.insert(0, sys.path[0] + '/../')
import torch
import numpy as np
from etl.data2vec import content2inds
from model.textCNN import textCNN
from conf.params import textCNN_param, parse_args
from commons.get_logger import get_logger
import pandas as pd
from tqdm import tqdm
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


args = parse_args()
logger = get_logger(args.log)


def parse_net_result(out):
    score = max(out)
    label = np.where(out == score)[0][0]

    return label, score


def prepare_model():
    logger.info('init net...')
    net = textCNN(textCNN_param)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    net.load_state_dict(torch.load(args.model, map_location=device))
    net.to(device)
    net.eval()
    return net, device


def predict(net, device, text):
    text = content2inds(text)
    sentence = np.array([int(x) for x in text])
    sentence = torch.from_numpy(sentence)
    output = net(sentence.unsqueeze(0).type(torch.LongTensor).to(device)).cpu().detach().numpy()[0]
    label_pre, score = parse_net_result(output)
    """ 输出样例
    output:  [-0.58343625 -0.81639504]
    label_pre:  0
    score:  -0.58343625
    """
    logger.info('预测结果: output=' + str(output) + ' label_pre=' + str(label_pre))
    return output, label_pre


if __name__ == "__main__":
    # predict(net, device, '奔驰比宝马好')
    net, device = prepare_model()
    datas = pd.read_csv(args.test_raw)
    datas = datas.sample(frac=1)
    ground_truth = []
    prediction = []
    bad_case = []
    for i in tqdm(range(len(datas)), desc='模型预测'):
        content = datas.iloc[i, 1]
        cla = datas.iloc[i, 2]
        cla_ind = int(cla)
        _, label_pre = predict(net, device, content)
        ground_truth.append(cla_ind)
        prediction.append(label_pre)
        if cla_ind != label_pre:
            bad_case.append({"actual": cla_ind, "predict": label_pre, "content": content})

    precision = precision_score(ground_truth, prediction, average="binary", pos_label=1)
    accuracy = accuracy_score(ground_truth, prediction)
    recall = recall_score(ground_truth, prediction, average="binary", pos_label=1)
    f1 = f1_score(ground_truth, prediction, average="binary", pos_label=1)
    print('model: ', args.model)
    print('precision: ', precision)
    print('recall: ', recall)
    print('f1: ', f1)
    print('accuracy: ', accuracy)

    pass


