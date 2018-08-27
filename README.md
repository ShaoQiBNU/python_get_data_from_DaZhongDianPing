python爬取大众点评数据
===================

# 一. 导入包

```python 
import re
import requests
from bs4 import BeautifulSoup
import json  
import threading  
import requests  
import pandas as pd
```

# 二. 爬虫过程分析

## (一) url解析

> URL是Uniform Resource Locator的缩写，译为“统一资源定位 符”。 通俗地说，URL是Internet上描述信息资源的字符串，主要用在各种WWW客户程序和服务器程序上。采用URL可以用一种统一的格式来描述各种信息资源，包括文件、服务器的地址和目录等。
>
> URL的一般格式为(带方括号[]的为可选项)： 
> **protocol :**// **hostname**[:port] / **path** / [;parameters][?query]#fragment
>
> URL的格式由三部分组成： 
> ①第一部分是协议(或称为服务方式)。 
> ②第二部分是存有该资源的主机IP地址(有时也包括端口号)。 
> ③第三部分是主机资源的具体地址，如目录和文件名等。
>
> 第一部分和第二部分用“://”符号隔开， 
> 第二部分和第三部分用“/”符号隔开。 
> 第一部分和第二部分是不可缺少的，第三部分有时可以省略。

## (二) url组合

> 进入大众点评官网，网址为：http://www.dianping.com. 当把城市切换到北京时，我们观察一下url的变化，https://www.dianping.com/beijing. ，beijing代表城市；当输入query：美食 时，url变化为：https://www.dianping.com/search/keyword/2/0_美食. ，'/search/keyword’代表搜索关键词的路径，2代表城市编号，’0\_美食’代表搜索词；美食页面有多个商家，对其进行翻页，url变化为：http://www.dianping.com/search/keyword/2/0_美食/p2?aid=92020785%2C102284990&cpt=92020785%2C102284990. ，p2代表的'page 2’，也就是第二页，后面的?aid=92020785%2C102284990&cpt=92020785%2C102284990属于query string，可以忽略，一般是用来标记网页自身的一些信息，只要改变“p”后面所带的数字，就能实现翻页的效果。

![image](https://github.com/ShaoQiBNU/python_get_data_from_DaZhongDianPing/blob/master/images/1.png)
![image](https://github.com/ShaoQiBNU/python_get_data_from_DaZhongDianPing/blob/master/images/2.png)
![image](https://github.com/ShaoQiBNU/python_get_data_from_DaZhongDianPing/blob/master/images/3.png)

> 所以如果想搜索任意的一个词，那么在地址栏里按照如下的格式输入即可：
> **协议（http://） + 域名（www.dianping.com）+ 路径（/search/keyword） + 前缀（/0_） + 关键词（美食） + 页数 （/p） + 具体页数**

## (三) 伪装头设置

> 由于网站均有反爬机制，所以为了避免爬取失败，需要添加伪装头headers，具体获取方法如下：
> 页面右击 ——> 检查 ——> 选择NetWork ——> 点击clear ——> 然后重新刷新 ——> 选择第一个，进入，点击Headers，获取参数，如下：

![image](https://github.com/ShaoQiBNU/python_get_data_from_DaZhongDianPing/blob/master/images/4.png)

```python
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
           'Cookie':'_lxsdk_cuid=15eea339434c8-0d2cff6b34e61c-c313760-100200-15eea339434c8; _lxsdk=15eea339434c8-0d2cff6b34e61c-c313760-100200-15eea339434c8; _hc.v=cec4c6d7-039d-1717-70c0-4234813c6e90.1507167802;\
            s_ViewType=1; __mta=218584358.1507168277959.1507176075960.1507176126471.5; JSESSIONID=48C46DCEFE3A390F647F52FED889020D; aburl=1; cy=2; cye=beijing; _lxsdk_s=15eea9307ab-17c-f87-123%7C%7C48',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Host':'www.dianping.com'
    }
```
> 之后调用requests的post函数，即可获取html，此时得到的是一个网页源代码，没有爬取到内容，因此还需要用bs4的BeautifulSoup作进一步解析，如下：
```python
############# get every page html ################
def get_html(url):
    ##### Cookie masquerade
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
        'Cookie':'_lxsdk_cuid=15eea339434c8-0d2cff6b34e61c-c313760-100200-15eea339434c8; _lxsdk=15eea339434c8-0d2cff6b34e61c-c313760-100200-15eea339434c8; _hc.v=cec4c6d7-039d-1717-70c0-4234813c6e90.1507167802;\
            s_ViewType=1; __mta=218584358.1507168277959.1507176075960.1507176126471.5; JSESSIONID=48C46DCEFE3A390F647F52FED889020D; aburl=1; cy=2; cye=beijing; _lxsdk_s=15eea9307ab-17c-f87-123%7C%7C48',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Host':'www.dianping.com'
    }

    ##### sent query and get html from the url
    html=requests.post(url,headers=headers).text

    ##### analysis the html
    soup=BeautifulSoup(html,'lxml')
 
    return soup
```

## (四) 数据爬取
> 通过BeautifulSoup解析得到html页面内容，为了获取商家的相关信息，可以通过标签定位得到信息。具体如下：

```python
############# get aim info ################
def get_aim_info(aim_url,page,score_exchange):

    ##### save all info into a list
    aim_info=[]

    ##### set id 
    id=0

    ##### traverse every page to get info 
    for i in range(1,page+1):

        ##### add page number to the aim_url and get the html
        aim_url_page=aim_url+'/p'+str(i)        
        soup=get_html(aim_url_page)
   
        ##### get aim info such as: name, address, label, score, consumption_person, reviews
        
        for li in soup.find('div',class_="shop-wrap").find('div',id="shop-all-list").ul.find_all('li'):
            
            ##### save info into a dict
            li_dict=[]
            ##### get every item info
            li_info=li.find('div',class_='txt')

            ##### item id
            li_dict.append(id)

            ##### item name
            li_dict.append(li_info.find('div',class_='tit').a.h4.text)

            ##### item link
            li_dict.append(li_info.find('div',class_='tit').a['href'])

            ##### item address
            li_dict.append(li_info.find('div',class_='tag-addr').find('span',class_='addr').text)

            ##### item label
            li_dict.append(li_info.find('div',class_='tag-addr').find('span',class_='tag').text)

            ##### item score
            score=li_info.find('div',class_='comment').span['title']
            if(score in score_exchange):
                li_dict.append(score_exchange[score])
            else:
                li_dict.append('nan')
            ##### item consumption_person
            try:
                li_dict.append(int(re.sub('￥','',li_info.find('div',class_='comment').find('a',class_="mean-price").b.text)))
            except AttributeError:
                li_dict.append('nan')
            ##### item reviews
            try:
                li_dict.append(int(li_info.find('div',class_='comment').find('a',class_='review-num').b.text))
            except AttributeError:
                li_dict.append(0)
            #print(li_dict)

            ##### save the result into the list
            aim_info.append(li_dict)

            id=id+1
```
> 为了自动爬取所有页的数据，设置函数获取最多页数，从而实现自动翻页，代码如下：
```python
############# get maximum page ################
def get_max_page(aim_url):

    ##### set the page=1 and get the html info 
    aim_url_page=aim_url+'/p'+str(1)
    soup=get_html(aim_url_page)

    ##### find the page span
    page=int(soup.find('div',class_='page').find_all('a')[-2].text)

    return page
```

# 三. 代码
```python
# -*- coding:utf-8 -*-  

'''
#Author Shao Qi
########## From dazhongdianping get aim infomation ################

'''

########## import packages ###########
import re
import requests
from bs4 import BeautifulSoup
import json  
import threading  
import requests  
import pandas as pd



############# get every page html ################
def get_html(url):
    ##### Cookie masquerade
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36',
        'Cookie':'_lxsdk_cuid=15eea339434c8-0d2cff6b34e61c-c313760-100200-15eea339434c8; _lxsdk=15eea339434c8-0d2cff6b34e61c-c313760-100200-15eea339434c8; _hc.v=cec4c6d7-039d-1717-70c0-4234813c6e90.1507167802;\
            s_ViewType=1; __mta=218584358.1507168277959.1507176075960.1507176126471.5; JSESSIONID=48C46DCEFE3A390F647F52FED889020D; aburl=1; cy=2; cye=beijing; _lxsdk_s=15eea9307ab-17c-f87-123%7C%7C48',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Host':'www.dianping.com'
    }

    ##### sent query and get html from the url
    html=requests.post(url,headers=headers).text

    ##### analysis the html
    soup=BeautifulSoup(html,'lxml')
 
    return soup

############# get maximum page ################
def get_max_page(aim_url):

    ##### set the page=1 and get the html info 
    aim_url_page=aim_url+'/p'+str(1)
    soup=get_html(aim_url_page)

    ##### find the page span
    page=int(soup.find('div',class_='page').find_all('a')[-2].text)

    return page

############# get aim info ################
def get_aim_info(aim_url,page,score_exchange):

    ##### save all info into a list
    aim_info=[]

    ##### set id 
    id=0

    ##### traverse every page to get info 
    for i in range(1,page+1):

        ##### add page number to the aim_url and get the html
        aim_url_page=aim_url+'/p'+str(i)        
        soup=get_html(aim_url_page)
   
        ##### get aim info such as: name, address, label, score, consumption_person, reviews
        
        for li in soup.find('div',class_="shop-wrap").find('div',id="shop-all-list").ul.find_all('li'):
            
            ##### save info into a dict
            li_dict=[]
            ##### get every item info
            li_info=li.find('div',class_='txt')

            ##### item id
            li_dict.append(id)

            ##### item name
            li_dict.append(li_info.find('div',class_='tit').a.h4.text)

            ##### item link
            li_dict.append(li_info.find('div',class_='tit').a['href'])

            ##### item address
            li_dict.append(li_info.find('div',class_='tag-addr').find('span',class_='addr').text)

            ##### item label
            li_dict.append(li_info.find('div',class_='tag-addr').find('span',class_='tag').text)

            ##### item score
            score=li_info.find('div',class_='comment').span['title']
            if(score in score_exchange):
                li_dict.append(score_exchange[score])
            else:
                li_dict.append('nan')
            ##### item consumption_person
            try:
                li_dict.append(int(re.sub('￥','',li_info.find('div',class_='comment').find('a',class_="mean-price").b.text)))
            except AttributeError:
                li_dict.append('nan')
            ##### item reviews
            try:
                li_dict.append(int(li_info.find('div',class_='comment').find('a',class_='review-num').b.text))
            except AttributeError:
                li_dict.append(0)
            #print(li_dict)

            ##### save the result into the list
            aim_info.append(li_dict)

            id=id+1

    ##### export the list into a csv
    features=['ID','name','link','address', 'label', 'score', 'consumption_person', 'reviews']
    file=pd.DataFrame(columns=features,data=aim_info)
    file.to_csv("C:\\Users\\shaoqi_i\\Desktop\\food.csv",encoding='utf-8',index=False)


if __name__=='__main__':
    
    ##### host url
    basic_url=r"http://www.dianping.com"

    ##### key word
    key_word=r'美食' 

    ##### city number: 2 is Beijing
    city_num=str(2)

    ##### aim url
    aim_url=basic_url+'/search/keyword/'+city_num+'/0_'+key_word
    #aim_url=r'https://www.dianping.com/search/keyword/2/0_火锅'

    ##### maximum page
    max_page=get_max_page(aim_url)

    ##### score exchange dict
    score_exchange={'五星商户':10,'准五星商户':9,'四星商户':8,'准四星商户':7,'三星商户':6,'准三星商户':5,'二星商户':4,'准二星商户':3,'一星商户':2,'该商户暂无星级':1}

    ##### start get aim info
    get_aim_info(aim_url,max_page,score_exchange)
    
    print("ok")
```
