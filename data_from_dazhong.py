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

