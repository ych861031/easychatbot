#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from dateutil import parser
r = requests.get('http://web.lib.fcu.edu.tw/library/index.html')
soup = BeautifulSoup(r.text,'lxml')
res = soup.find('div',{'id':'box-blog'})
blog_title = []
blog_date = []
link = []
for text in res.find_all('span',{'class':'field-content'}):
    if  text.find('a'):
        title = text.find('a').text.strip()
        blog_title.append(title)
        link.append(text.find('a',href=True).get('href'))
    else:
        date= text.text.strip()
        blog_date.append(date)

content = []
for i in link:
    r = requests.get(i)
    soup = BeautifulSoup(r.text,'lxml')
    content.append(soup.find('div',{'class':'entry-content'}).find_all('p'))

new_content = []
for i in content:
        string = ""
        for j in i:
            string += j.text.strip()
        new_content.append(string)
        
def getNews():
    r = requests.get('http://web.lib.fcu.edu.tw/library/index.html')
    soup = BeautifulSoup(r.text,'lxml')
    res = soup.find('div',{'id':'box-news'})
    news_title = []
    news_date = []
    for text in res.find_all('span',{'class':'field-content'}):
        if  text.find('a'):
            title = text.find('a').text.strip()
            news_title.append(title)
        else:
            date= text.text.strip()
            news_date.append(date)
    return '最新消息：' +news_title[0] #+'\n發佈時間： ' + news_date[0] 
            
def getBook(s):
    print(s)
    target = s
    r = requests.get('https://innopac.lib.fcu.edu.tw/search*cht/a?searchtype=X&searcharg={}&searchscope=9&SORT=D&submit=查詢'.format(target))
    soup = BeautifulSoup(r.text,'lxml')

    if soup.find('div',{'class','browseSearchtoolMessage'}):
        found = soup.find('div',{'class','browseSearchtoolMessage'}).find('i').text.strip()[:-3]
        result = soup.find('span',{'class':'briefCitTitle'})
        url = 'https://innopac.lib.fcu.edu.tw'+ result.find('a',href=True).get('href').strip()
        print(url)
        book_name = result.text.strip()
        r = requests.get(url)
        soup = BeautifulSoup(r.text,'lxml')
        result = soup.find('td',{'width':'21%'})
        status = result.text.strip()
        print('查獲：'+found)
        print('推薦書名：'+book_name)
        print('狀態：'+status)
        return '查獲：'+found + '\n'+ '推薦書名：'+book_name + '\n' + '狀態：'+status

    elif soup.find('div',{'class','bibSearchtoolMessage'}):
        found = soup.find('div',{'class','bibSearchtoolMessage'}).find('i').text.strip()[:-3]
        result = soup.find('span',{'class':'briefCitTitle'})
        book_name = soup.find('td',{'class':'bibInfoData'}).text.strip()
        status = soup.find('td',{'width':'21%'}).text.strip()
        print('查獲：'+found)
        print('推薦書名：'+book_name)
        print('狀態：'+status)
        return '查獲：'+found + '推薦書名：'+book_name + '\n' + '狀態：'+status
    else:
        print('找不到：'+target)
        return '找不到：'+target
    
def get_blog(index):
    if index > len(new_content) :
        return "抱歉你輸入的我們找不到"
    return new_content[index-1]

from flask import Flask, request, make_response, jsonify
import json

app = Flask(__name__)

@app.route("/")
def verify():
    return "Hello world", 200


@app.route('/', methods=['POST'])
def webhook():
    
    req = request.get_json(silent=True, force=True)
    if req.get('queryResult').get('action') == 'findbook':
        book = req.get('queryResult').get('queryText')
        if ":" in book:
            book = book.split(':')
            book = ''.join(book[1:])
        else:
            book = book.split('：')
            book = ''.join(book[1:])
        res = {'fulfillmentText':getBook(book)}
        return make_response(jsonify(res))
    
    if req.get('queryResult').get('action') == 'library_news':
        res = {"fulfillmentText": getNews()}
        print('return news')
        return make_response(jsonify(res))
    
    if req.get('queryResult').get('action') == 'askBlog':
        content = "目前有" + str(len(blog_title)) + '個blog內容:\n'
        for i in range(len(blog_title)):
            content += str(i+1) + ':' + blog_title[i] +  '\n'
        content += '你想看哪個呢？'
        res = {"fulfillmentText": content}
        print('return blog title')
        return make_response(jsonify(res))
    if req.get('queryResult').get('action') == 'askFunction':
        content = "目前ChatBot提供的功能：查詢圖書館最新消息、查詢書籍、查詢圖書館部落格"
        res = {"fulfillmentText": content}
        print('return function')
        return make_response(jsonify(res))
    
    if req.get('queryResult').get('action') == 'libraryblog.libraryblog-custom':
        print(int(req.get('queryResult').get('parameters').get('number')))
        res = {"fulfillmentText": get_blog(int(req.get('queryResult').get('parameters').get('number')))}
        print('return blog')
        return make_response(jsonify(res))
    
    res = {"fulfillmentText": "抱歉這我無法告訴你"}
    return make_response(jsonify(res))
            
if __name__ == '__main__':
    app.run(port=8000)


# In[ ]:




