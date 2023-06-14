# C_Chat_Chatbot
111-2 NLP 期末專題

希洽板主要以討論ACG(動畫、漫畫、遊戲與相關周邊)話題為主體，目前也還是PTT的大板之一，每天文章動輒數百篇，該板也有不少特別的文化，不少PTT流行用語是發源於該板。

>目前訓練的效果不太好，可能是因為宅圈的專業術語太多，導致model怎麼學也學不會

![image](https://github.com/doudou030/C_Chat_Chatbot/blob/main/img/yuma.gif?raw=true)
## Requirement
- ngrok
- tensorflow
- linebot
- numpy
- jieba
- re
- sklearn
- tqdm

## code
- `colab/PTT_crawler` : 在colab上爬PTT資料的
- `colab/c_chat_train` : 在colab上訓練model
- `PTT_crawler` : 爬PTT資料，要哪個版從哪個index在裡面可以調
- `bot.py` : 執行bot，再去執行ngrok
- `load_model` : 使用pre_train的model
- `single_prediction` : 透過model進行prediction

## Demo
- 1.要先執行bot.py
- 2.在cmd輸入`ngrok http 5000`，之後會產生一個public url
- 3.將產生的public url丟去line developer中其中一個設定message API的webhook url，就可以開始用了

![image](https://github.com/doudou030/C_Chat_Chatbot/blob/main/img/demo1.jpg?raw=true)
![image](https://github.com/doudou030/C_Chat_Chatbot/blob/main/img/demo2.jpg?raw=true)

## Reference

[snsd0805/PTT-Chatbot](https://github.com/snsd0805/PTT-Chatbot/tree/master)

[hsuanchia/PTT-Gossiping-Chatbot](https://github.com/hsuanchia/PTT-Gossiping-Chatbot)
