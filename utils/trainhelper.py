import numpy as np

import torch 
from torch.autograd import Variable
from models.hierarchical_pack import HAN  # TODO
import utils.calculatescore as cs

def accuracy(predictions, labels):
    return (100.0 * np.sum(np.array(predictions) == np.array(labels))
            / len(labels))

def model_selector(config, model_id, use_element):
    model = None
    if model_id == 4:
        model = HAN(config)
    else:
        print("Input ERROR!")
        exit(2)
    return model


def _get_loss_weight(predicted, label, num_class):

    sample_per_class = torch.zeros(num_class)
    error_per_class = torch.zeros(num_class)
    for p, t in zip(predicted, label):
        # print(p, t)
        sample_per_class[t] += 1
        if p != t:
            error_per_class[t] += 1

    return error_per_class / sample_per_class


def do_eval(valid_loader, model, model_id, has_cuda, dmpv_model=None, dbow_model=None):
    """ 在验证集上做验证，报告损失、精确度"""
    true_labels = []
    predicted_labels = []
    model.is_training = False
    model.dropout_rate = 0
    for data in valid_loader:
        ids, texts, labels = data
        if has_cuda:
            texts = texts.cuda()
        # if dmpv_model is not None and dbow_model is not None:  # cnn and rcnn with doc2vec
        #     doc2vec = gdv.build_doc2vec(ids, dmpv_model, dbow_model)
        #     if has_cuda:
        #         doc2vec = Variable(torch.FloatTensor(doc2vec).cuda())
        #     else:
        #         doc2vec = Variable(torch.FloatTensor(doc2vec))
        #     outputs = model(Variable(texts), doc2vec)
        outputs = model(Variable(texts))
        _, predicted = torch.max(outputs.data, 1)
        true_labels.extend(labels)
        predicted_labels.extend(predicted.cpu())

    loss_weight = _get_loss_weight(predicted_labels, true_labels, 8)
    print(true_labels[:10])
    print(predicted_labels[:10])
    print("Acc:", accuracy(predicted_labels, true_labels))
    score = cs.micro_avg_f1(predicted_labels, true_labels, model.num_class)
    print("Micro-Averaged F1:", score)
    model.is_training = True
    model.dropout_rate = 0.5
    return loss_weight, score

