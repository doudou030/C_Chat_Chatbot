import os
import numpy as np
import pandas as pd
import jieba
import re
from tqdm import tqdm
from sklearn.utils import shuffle
import tensorflow as tf
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint

def fit_sentence(sen, voc):
    res = []
    for i in sen:
        res.append(voc[i])
    return res

def single_predict(input_text, voc, ind_voc, model):
    ### Answer input initial state --> [<SOS>] --> [4977, 0, 0, 0,...]
    ans_input = np.zeros((1,MAXLEN),dtype='int64')
    ans_input[0,0] = voc["<SOS>"]

    ### Convert your question into number label
    res = fit_sentence(input_text, voc)
    while len(res) < MAXLEN: # If sentence is shorter than maxlen, append 0 until length reach maxlen
        res.append(0)
    question = np.array([res])

    ind = 0
    ### Stop condition: 1. Prediction until MAXLEN, 2. Output '<EOS>' or 0
    while (ans_input[0][ind] != voc['<EOS>'] or ans_input[0][ind] != 0) and ind < MAXLEN-1:
        ind += 1
        pred = model.predict([question, ans_input])#,verbose=0
        res = np.argmax(pred,axis=-1) # Get highest probabilty index of character in vocabulary
        ans_input[0,ind] = res[0][ind]
    ### Convert prediction into human language 
    ans = ""
    # print(ans_input[0][1:])
    for i in ans_input[0][1:]:
        if i == 0 or i == voc['<EOS>']:
            break
        ans += ind_voc[i] 
    return str(ans) # Return string --> Send string back to ngrok and forwarding to Line