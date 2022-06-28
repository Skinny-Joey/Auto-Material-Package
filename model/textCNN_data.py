from torch.utils.data import Dataset, DataLoader
import random
import numpy as np


def get_vec(file):
    datas = open(file, 'r').read().split('\n')
    datas = list(filter(None, datas))
    return datas


class textCNN_data(Dataset):
    def __init__(self, trainDataFile):
        trainData = open(trainDataFile, 'r').read().split('\n')
        trainData = list(filter(None, trainData))
        random.shuffle(trainData)
        self.trainData = trainData

    def __len__(self):
        return len(self.trainData)

    def __getitem__(self, idx):
        data = self.trainData[idx]
        data = list(filter(None, data.split(',')))
        data = [int(x) for x in data]
        cla = data[0]
        sentence = np.array(data[1:])

        return cla, sentence


def textCNN_dataLoader(param):
    dataset = textCNN_data(param['trainDataFile'])
    batch_size = param['batch_size']
    shuffle = param['shuffle']
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)


if __name__ == "__main__":
    from conf.params import parse_args
    args = parse_args()
    dataset = textCNN_data(args.train_vec)
    cla, sen = dataset.__getitem__(0)

    # print(cla)
    # print(sen)
