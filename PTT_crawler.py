# # Requirement
# !pip install requests beautifulsoup4 jieba 

import requests
from bs4 import BeautifulSoup
import jieba
from tracemalloc import start
from urllib import response
from itsdangerous import exc
import time
import json
import os
import platform
# 去看哪一條評論最多讚
class CommentJudge():
    def getBest(self, comments):
        self.comments = comments
        self.segment_comments = []
        self.wordDict = {}
        self.commentsScore = []

        self.segment()
        self.buildWordDict()
        self.score()

        maxScore, maxIndex = 0, 0
        for index in range(len(self.commentsScore)):
            score = self.commentsScore[index]
            if score > maxScore:
                maxScore = score
                maxIndex = index
        return self.comments[maxIndex], self.commentsScore[maxIndex]
    
    def segment(self):
        banned = [' ', ',', '，', '。', '？', '?', '='] #過濾的字符
        for comment in self.comments:
            words = [ word for word in jieba.cut(comment) if word not in banned] # 用jieba做分詞
            self.segment_comments.append(words)

    def buildWordDict(self):
        for comment in self.segment_comments:
            for word in comment:
                if word in self.wordDict:
                    self.wordDict[word] += 1 #如果說是重複的詞+1
                else:
                    self.wordDict[word] = 0 #如果是新的則初始化為0
    
    def score(self):
        for index in range(len(self.segment_comments)):
            comment = self.segment_comments[index]
            if len(self.comments[index]) >= 15: #如果此評論超過15個字元，則是0分
                self.commentsScore.append(0)
                continue

            weight = 0
            for word in comment:
                weight += self.wordDict[word] # 根據jieba中的字典累加得分

            self.commentsScore.append(weight)

class PTTCrawler():
    def __init__(self, board, startURL='index.html'):
        self.board = board
        self.startURL = startURL
        self.judge = CommentJudge()
        if requests.get('https://www.ptt.cc/bbs/{}/index.html'.format(self.board)).status_code != 200:
            raise Exception("No board in PTT named {}".format(self.board))
    
    def getPosts(self, number=50000):
        url = 'https://www.ptt.cc/bbs/{}/{}'.format(self.board, self.startURL)
        
        if os.path.isfile('train.json'):
            with open('train.json') as fp:
                ans = json.load(fp)
                counter = len(ans)
        else:
            ans = []
            counter = 0

        while counter < number:
            print(url)
            response = requests.get(url, headers={'cookie': 'over18=1;'})
            if response.status_code == 200:
                # 取得文章的標題和URL，並進一步 call getComments() 取得推文
                root = BeautifulSoup(response.text, 'html.parser')
                posts = root.find_all('div', class_='r-ent')
                for post in posts:
                    link = post.find("a")
                    if link:                        # 如果被刪文，則會是 Noneor "[閒聊]"[問題]
                        if  "[問題]" in link.text and "Re:" not in link.text:
                            counter += 1

                            comments = self.getComments(link.get('href'))
                            if len(comments) != 0:
                                bestComment, score = self.judge.getBest(comments)
                                ans.append({
                                    "Q": link.text.replace('[問題]', ''),
                                    "A": bestComment
                                })
                                print(ans[-1], counter)
                                time.sleep(2.5)
                                if counter % 100 == 0:
                                    with open('train.json', 'w') as fp:
                                        json.dump(ans, fp)
                        if  "[閒聊]" in link.text and "Re:" not in link.text:
                            counter += 1

                            comments = self.getComments(link.get('href'))
                            if len(comments) != 0:
                                bestComment, score = self.judge.getBest(comments)
                                ans.append({
                                    "Q": link.text.replace('[閒聊]', ''),
                                    "A": bestComment
                                })
                                print(ans[-1], counter)
                                time.sleep(2.5)
                                if counter % 100 == 0:
                                    with open('train.json', 'w') as fp:
                                        json.dump(ans, fp)
                
                # 取得上一頁的位址
                btns = root.find_all('a', class_='btn wide')
                for btn in btns:
                    if '上頁' in btn.text:
                        url = 'https://www.ptt.cc{}'.format(btn.get('href'))
                        print(url)
                        print()
                # time.sleep(3)
            else:
                raise Exception("Response status code {}".format(response.status_code))
        return ans
    #取得評論
    def getComments(self, url):
        url = 'https://www.ptt.cc{}'.format(url)
        ans = []
        response = requests.get(url, headers={'cookie': 'over18=1;'})
        root = BeautifulSoup(response.text, 'html.parser')
        comments = root.find_all('div', class_='push')
        for comment in comments:
            try:
                text = comment.find_all('span')[2].text
                if 'http' not in text:
                    ans.append(text.replace(': ', ''))
            except:
                print(comment)  # 推文太多會出現 error
        return ans

crawler = PTTCrawler("C_Chat", 'index17650.html')
posts = crawler.getPosts()

def json2txt(file):
    name = file.split(".")[0]  #取得檔名
    with open(file, 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
    
    text_data = ''
    for item in json_data:
        text_data += f"Q: {item['Q']}\n"
        text_data += f"A: {item['A']}\n\n"

    with open('{}.txt'.format(name), 'w', encoding='utf-8') as txt_file:
        txt_file.write(text_data)

json2txt('train.json')
