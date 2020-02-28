

# coding: utf-8

import json
import re
import uuid
import requests
import time
import datetime
import urllib.parse
import traceback
from pprint import pprint


def GetSession():
    rseesion=requests.session()
    rseesion.cookies= requests.cookies.RequestsCookieJar()
    return rseesion

def dotask(taskData):
    
    result_data = {
        'code': '0',
        'msg': '',
      
    }
    #发布参数
    params = {
   
        "__EVENTTARGET": "",  # 默认空
        "__EVENTARGUMENT": "",#默认空
        "__VIEWSTATE": "",#在新建文章页面获取
        "__VIEWSTATEGENERATOR": '',#在新建文章页面获取
        "content": taskData["content"],#发文正文，html数据
        "TextBox1": taskData.get("sourceUrl",""),  #文章来源url， 默认:选填 http://
        "txtAbstract": taskData.get("desc",""),#文章简要描述
        "Button4.x": 0,
        "Button4.y": 0,
        "Hidden2":-1000,
        "Hidden4":taskData.get("private",0),#私有还是公开
        "HiddenDraft":"",
        "HiddenBlackUser":"",
        "hidtitle":taskData.get("title",""),#标题
        "Tags":taskData.get("tags",""),#标签，英文逗号隔开，最多3个
        "hidorignal":taskData.get("isOrignal",0),#是否申明原创
        "isValideOK":0,#
        "isValideUser":1,
        "activity":"",
        "currUserID":"",#当前用户id
        "editorValue":taskData["content"],#发文正文html
        }
    uidStr=GetUserId(taskData["cookie"],params);
    if(uidStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=uidStr;
        return result_data;
    viewStr=GetViewState(taskData["cookie"],params);
    if(viewStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=viewStr;
        return result_data;
    pubResult=PublishArticle(taskData["cookie"],params);
    if(pubResult!=None):
        result_data["code"]=-1;
        result_data["msg"]=pubResult;
        return result_data;
    return result_data

#发布
def PublishArticle(cookieStr,params):
    try:
        http=GetSession();
        header = {
        # 'User-Agent': WEB_USERAGRNT,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type':'application/x-www-form-urlencoded',
        'Referer':'http://www.360doc.com/edit/writeartnew.aspx',
        'Origin':'http://www.360doc.com',
        'Cookie':cookieStr,
    } 
        result=http.post("http://www.360doc.com/edit/writeartnew.aspx",data=params, headers=header , verify = False).text;
        
        if(result.startswith("<script>if")):
            return None;
        else:
            return "发布失败";
        
    except:
        return traceback.format_exc();

#获取范围参数viewstateXXX，发文需要
def GetViewState(cookieStr,params):
    try:
        http=GetSession();
        header = {
        # 'User-Agent': WEB_USERAGRNT,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie':cookieStr,
    }
        result=http.get("http://www.360doc.com/edit/writeartnew.aspx",headers=header , verify = False).text;
        viewState=re.search('id="__VIEWSTATE"[\s]{0,}value=".*"',result)
        if(viewState):
            viewStateStr=viewState.group(0);
            params["__VIEWSTATE"]=viewStateStr.split('"')[3];
        else:
            return "未找到viewstate";
        viewStateGenId=re.search('id="__VIEWSTATEGENERATOR"[\s]{0,}value="[0-9a-zA-Z]{3,}"',result);
        if(viewStateGenId):
            viewStateGenIdStr=viewStateGenId.group(0);
            params["__VIEWSTATEGENERATOR"]=viewStateGenIdStr.split('"')[3];
            return None;
        else:
            return "未找到viewstateGEN";
    except:
        return traceback.format_exc();
    

#获取用户id，发文是需要此参数
def GetUserId(cookieStr,params):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie':cookieStr,
    }
        result=http.get("http://www.360doc.com/myaccount.aspx?app=2",headers=header , verify = False).text;
        useridObj=re.search('id="360docuserid"[\s]{0,}value="[0-9a-zA-Z]{3,}"',result);
        if(useridObj):
            useridStr=useridObj.group(0).split('"')[3];
            params["currUserID"]=useridStr;
            return None;
        else:
            return "未找到用户信息";
    except:
        return traceback.format_exc();
    
    #id="360docuserid" value="68476039"
def python_control(all_params):
    result_data=dotask(all_params);
    return result_data


def main_control(params, logger=None):
    return python_control(params)


if __name__ == '__main__':
    
    
    taskData= {
   
        "cookie": "__gads=Test; BDTUJIAID=0d7bc063de4547a2091556385badd9b9; yuanChuang_banner=1; bookvip_banner=1; 360doc12=360doc; 360docnft1=1; 360docnft2=1; 360docAccountYD=1; 360doc13_68476039=1; 360doc14_68476039=1; car=0; 360doc2=ndGdt6RSxdANad1kFplyZYCspcdZ9zdI1brRdMmWk0Uy9AaKjnHEWmm6eTstF+lr; 360doc1=rz1YyBJF7EOeXIqHwMsbB+RuDKA6H4WEQKSDUJKSPpBpnGjPVsGVfUhMt0oz1TOu; 360doc3=40bEPRtUYJiE92nQFkcD7Z7U3+a4joqA2fWnYR7UY0EgyFqVCRWuvmzpLkNX/T2I; lastlogintype=2; 360doc6=1; LoginName=13882063847; 360doc4_68476039=890898449,890896075; Hm_lvt_d86954201130d615136257dde062a503=1580976112,1581299363,1581326078; Hm_lpvt_d86954201130d615136257dde062a503=1581326214; 360doc21_68476039=%7B%22status%22%3A%221%22%2C%22msg%22%3A%7B%22msgcount%22%3A%221%22%2C%22sysmsgcount%22%3A%220%22%2C%22syscount%22%3A%220%22%2C%22flowercount%22%3A%220%22%2C%22gzcount%22%3A%220%22%2C%22gzreplycount%22%3A%220%22%2C%22gzresavecount%22%3A%220%22%2C%22wpcount%22%3A%220%22%2C%22resaveartcount%22%3A%220%22%2C%22chatcount%22%3A%220%22%2C%22rewardcount%22%3A%220%22%7D%7D",  # 默认空
        "sourceUrl": "",#默认空
        "content": '<img src="http://p1.pstatp.com/large/pgc-image/Rq3aqaF50dijL3" img_width="750" img_height="422" alt="逢车必检！返程高峰来临 深夜上海道口“忙而不乱”" inline="0"><h1 toutiao-origin="h1">逢车必检！返程高峰来临 深夜上海道口“忙而不乱”</h1><p>看看新闻Knews综合</p><p>2020-02-10 08:39</p><p>返程高峰来临，位于上海、江苏交界的G15沈海高速朱桥检查站昨晚（2月9日）进入上海的车流量较大，11条入沪车道全部开放，排队车辆一度拥堵5公里。现场民警依次引导车辆进入检查点，再由志愿者对司乘逐个进行体温测量，过程井然有序，配合默契，一辆车从进入到驶出平均耗时2至3分钟。</p><p>据了解，G15沈海高速朱桥检查站的入沪车流近日总体保持平稳，所有通过人员都必须接受体温检测，并填写健康信息登记表。</p><img src="http://p1.pstatp.com/large/pgc-image/Rq3aqazG65FJG7" img_width="1266" img_height="644" alt="逢车必检！返程高峰来临 深夜上海道口“忙而不乱”" inline="0"><p>民警顾坚革说：“这两天是上海市的返程高峰，从2月10日开始，工业企业必须要复工了。我们在原有的前两天9个车道的基础上，开辟了两个车道，包括其中一个绿色通道，返程高峰多数情况可以得到一个大的改善。”</p>',#发文正文，html数据
        "desc": '返程高峰',  #文章来源url， 默认:选填 http://
        "private":0,#私有还是公开
        "title":'逢车必检！返程高峰来临 深夜上海道口“忙而不乱”',#标题
        "Tags":'返程,上海',#标签，英文逗号隔开，最多3个
        "isOrignal":0,#是否申明原创
 
        "editorValue":'<img src="http://p1.pstatp.com/large/pgc-image/Rq3aqaF50dijL3" img_width="750" img_height="422" alt="逢车必检！返程高峰来临 深夜上海道口“忙而不乱”" inline="0"><h1 toutiao-origin="h1">逢车必检！返程高峰来临 深夜上海道口“忙而不乱”</h1><p>看看新闻Knews综合</p><p>2020-02-10 08:39</p><p>返程高峰来临，位于上海、江苏交界的G15沈海高速朱桥检查站昨晚（2月9日）进入上海的车流量较大，11条入沪车道全部开放，排队车辆一度拥堵5公里。现场民警依次引导车辆进入检查点，再由志愿者对司乘逐个进行体温测量，过程井然有序，配合默契，一辆车从进入到驶出平均耗时2至3分钟。</p><p>据了解，G15沈海高速朱桥检查站的入沪车流近日总体保持平稳，所有通过人员都必须接受体温检测，并填写健康信息登记表。</p><img src="http://p1.pstatp.com/large/pgc-image/Rq3aqazG65FJG7" img_width="1266" img_height="644" alt="逢车必检！返程高峰来临 深夜上海道口“忙而不乱”" inline="0"><p>民警顾坚革说：“这两天是上海市的返程高峰，从2月10日开始，工业企业必须要复工了。我们在原有的前两天9个车道的基础上，开辟了两个车道，包括其中一个绿色通道，返程高峰多数情况可以得到一个大的改善。”</p>',#发文正文html
        }
    pprint(main_control(taskData))











