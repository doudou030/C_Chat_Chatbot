# tenforflow會用到的
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

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
### Configs
MAXLEN = 50 ### MAXLEN should be same as the MAXLEN you use in previous training
EMB_DIM = 200
UNIT = 256
def tokenize_chinese(texts, voc, voc_ind):
    for t in tqdm(texts):
        for ch in str(t):
            if ch not in voc:
                voc[ch] = voc_ind
                voc_ind += 1 
    return voc, voc_ind

def build_model(voc):
    Q_in = Input((MAXLEN,),name='Q_input')
    Q_emb = Embedding(len(voc)+1,EMB_DIM,mask_zero=True,name='Q_emb')(Q_in)
    Q_out, Q_h, Q_c = LSTM(UNIT,return_state=True,recurrent_dropout=0.2,name='Q_LSTM')(Q_emb)
    Q_state = [Q_h,Q_c]
    A_in = Input((MAXLEN,),name='A_input')
    A_emb = Embedding(len(voc)+1,EMB_DIM,mask_zero=True,name='A_emb')(A_in)
    A_out = LSTM(UNIT,return_sequences=True,recurrent_dropout=0.2,name='A_LSTM')(A_emb,initial_state=Q_state)
    output = Dense(len(voc)+1,activation='softmax',name='Output')(A_out)

    model = Model(inputs=[Q_in,A_in],outputs=output,name='ChatBot')

    return model

def load_model():
    voc = {} # Vocabulary dictionary
    voc_ind = 1 # vocabulary index start from 1, index 0 means nothing
    ### Import your training data for re-build vocabulary
    q_data = []
    a_data = []
    f = open('train_data/train.txt',encoding="utf-8")
    lines = f.readlines() #總共行數
    for line in lines:
        line = line.strip()  
        if line.startswith('Q:'):
            q_data.append(line[3:])
        elif line.startswith('A:'):
            a_data.append(line[3:])  
    f.close

    # 如果說第一個有空格就去掉
    for i in range(len(q_data)):
      q_data[i] = q_data[i].lstrip()
      a_data[i] = a_data[i].lstrip()

    # 用jieba去掉一些不必要的字
    for i in range(len(q_data)):
      q_data[i] = jieba.lcut(q_data[i])
      q_data[i] = [q_data[i] for q_data[i] in q_data[i] if re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', q_data[i])]
      q_data[i] = ''.join(q_data[i])
      a_data[i] = jieba.lcut(a_data[i])
      a_data[i] = [a_data[i] for a_data[i] in a_data[i] if re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$', a_data[i])]
      a_data[i] = ''.join(a_data[i])

    # 轉成nparray並打亂
    q_data = np.array(q_data)
    a_data = np.array(a_data)
    q_data, a_data = shuffle(q_data,a_data)

    q, a = [], []
    for i in range(len(q_data)):
      seq_q, seq_a = q_data[i], a_data[i]
      q.append("".join(seq_q))
      a.append("".join(seq_a))

    ### Re-build vocabulary
    voc, voc_ind = tokenize_chinese(q, voc, voc_ind)
    voc, voc_ind = tokenize_chinese(a, voc, voc_ind)
    voc["<SOS>"] = len(voc)+1
    voc["<EOS>"] = len(voc)+1
    ind_voc = {}
    for k, v in voc.items():
        ind_voc[v] = k

    ### Build model and load the weight
    model = build_model(voc)
    model.load_weights('chatbot.h5')

    return voc, ind_voc, model

