from flask import Flask, request

# 載入 json 標準函式庫，處理回傳的資料格式
import json

# 載入 LINE Message API 相關函式庫
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

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
from load_model import load_model
from single_predict import single_predict

os.environ['TF_FORCE_GPU_ALLOW_GROWTH'] = 'true'
### Configs
MAXLEN = 50 ### MAXLEN should be same as the MAXLEN you use in previous training
EMB_DIM = 200
UNIT = 256

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
        pred = model.predict([question, ans_input],verbose=0)#,verbose=0
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

voc, ind_voc, model = load_model()

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def linebot():
    body = request.get_data(as_text=True)                    # 取得收到的訊息內容
    try:
        json_data = json.loads(body)                         # json 格式化訊息內容
        access_token = 'LtdcS+yvQcDaJB7ZPfOtuE7LSXkd9Hb/9j3eyxlyLIE4fphjqnpwjj7sQc1Cee9aaUqYMA3GNSH3FDSO0XF8Dx26M1QTcz01temk4aDXTXg01LZwFekjSe7MnCZIVVmE4L7btAjh6Db36C3td9tI4wdB04t89/1O/w1cDnyilFU='
        secret = '8e1dcc12652dfb2cbef1068f41e50414'
        line_bot_api = LineBotApi(access_token)              # 確認 token 是否正確
        handler = WebhookHandler(secret)                     # 確認 secret 是否正確
        signature = request.headers['X-Line-Signature']      # 加入回傳的 headers
        handler.handle(body, signature)                      # 綁定訊息回傳的相關資訊
        tk = json_data['events'][0]['replyToken']            # 取得回傳訊息的 Token
        receive_type = json_data['events'][0]['message']['type']     # 取得 LINE 收到的訊息類型
        if receive_type == 'text':
            msg = json_data['events'][0]['message']['text']  # 取得 LINE 收到的文字訊息
            print(f'User: {msg}')                               
            # reply = msg                                      # Change your reply into your predict result of chatbot model
            reply = single_predict(msg, voc, ind_voc, model)
            print(f'Bot: {reply}')

        else:
            reply = '你傳的不是文字呦～'
        print(reply)
        line_bot_api.reply_message(tk,TextSendMessage(reply))# 回傳訊息
    except:
        print(body)                                          # 如果發生錯誤，印出收到的內容
    return 'OK'                                              # 驗證 Webhook 使用，不能省略

if __name__ == "__main__":
    app.run()