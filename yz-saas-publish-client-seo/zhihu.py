

# coding: utf-8
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import re
import uuid
import requests
import time
import datetime
import urllib.parse
import traceback
from pprint import pprint
import random
import hashlib
import lxml.html
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

        }
    if(taskData.get("taskType")=="article"):
        articleId=None
        article=Article();
        #封面
        if(taskData.get("coverUrl")):
            imgDict={}
            imgRe=article.UpLoadImg(taskData["cookie"],taskData["coverUrl"],imgDict)
            if(imgRe):
                result_data["code"]=-1;
                result_data["msg"]=imgRe;
                return result_data;
            imgUrlConverted=imgDict.get("imgObj").get("src")
            saveJObject={}
            saveJObject["delta_time"]=0;
            saveJObject["isTitleImageFullScreen"]=False;
            saveJObject["titleImage"]=imgUrlConverted;
            reDict={}
            saveRe=article.SaveDraft(taskData["cookie"],json.dumps(saveJObject,ensure_ascii=False),reDict,articleId);
        if(saveRe):
            result_data["code"]=-1;
            result_data["msg"]=saveRe;
            return result_data;
        articleId=reDict.get("articleObj").get("id")
        #标题
        if(taskData.get("title")):        
            saveJObject={}
            saveJObject["delta_time"]=1;
            saveJObject["title"]=taskData.get("title");
            reDict={}
            saveRe=article.SaveDraft(taskData["cookie"],json.dumps(saveJObject,ensure_ascii=False),reDict,articleId);
            if(saveRe):
                result_data["code"]=-1;
                result_data["msg"]=saveRe;
                return result_data;
            
            if(not articleId and not reDict):
                result_data["code"]=-1;
                result_data["msg"]="保存标题失败";
                return result_data;
            if(not articleId and reDict):
                articleId=reDict.get("articleObj").get("id")
        else:
            result_data["code"]=-1;
            result_data["msg"]="标题不能为空";
            return result_data;
        if(not taskData.get("content")):
            result_data["code"]=-1;
            result_data["msg"]="正文不能为空";
            return result_data;
        #内容
        contentStr=article.PublishArticle(taskData["cookie"],taskData["content"],articleId);
        if(contentStr!=None):
            result_data["code"]=-1;
            result_data["msg"]=contentStr;
            return result_data;
        #推荐标签
        tagStr=article.GetRecommendTag(taskData["cookie"],articleId);
        if(tagStr!=None):
            result_data["code"]=-1;
            result_data["msg"]=tagStr;
            return result_data;
        #发布
        publishStr=article.Publish(taskData["cookie"],articleId,taskData.get("whoCanComment","anyone"));
        if(publishStr!=None):
            result_data["code"]=-1;
            result_data["msg"]=publishStr;
            return result_data;
        return result_data
    elif(taskData.get("taskType")=="question"):
        if(not taskData.get("title")):
            result_data["code"]=-1;
            result_data["msg"]="标题不能为空";
            return result_data;
        question=Question();
        if(taskData.get("content")):
            reContent={};
            conStr= question.PublishArticle(taskData["cookie"],taskData["content"],reContent);
            if(conStr or not reContent):
                result_data["code"]=-1;
                result_data["msg"]=conStr;
                return result_data;
            taskData["content"]=reContent.get("content","")
        publishStr=question.Publish(taskData);
        if(publishStr):
            result_data["code"]=-1;
            result_data["msg"]=publishStr;
            return result_data;
    elif(taskData.get("taskType")=="reanswer"):
        if(not taskData.get("content")):
            result_data["code"]=-1;
            result_data["msg"]="内容不能为空";
            return result_data;
        if(not taskData.get("answerId")):
            result_data["code"]=-1;
            result_data["msg"]="问题id不能为空";
            return result_data;
        anonymous=False;
        reAnswer=ReAnswer();
        if(taskData.get("anonymous")==1):
            anonymous=True;
        reAnswer.Switch(taskData["cookie"],taskData["answerId"],anonymous);
        
        reContent={};
        conStr=reAnswer.PublishArticle(taskData["cookie"],taskData["content"],reContent,taskData["answerId"]);
        if(conStr):
            result_data["code"]=-1;
            result_data["msg"]=conStr;
            return result_data;
        pubDict={
            "comment_permission":taskData.get("whoCanComment","all"),
            "content":reContent["content"],
            "reshipment_settings":"allowed",
            "reward_setting":{
                "can_reward":False,
                },
            }
        pubReDict={};
        pubStr=reAnswer.Publish(taskData["cookie"],pubDict,pubReDict,taskData["answerId"])
        if(pubStr or not pubReDict):
            result_data["code"]=-1;
            result_data["msg"]=pubStr;
            return result_data;
        reId=pubReDict.get("articleObj",{}).get("id");
    return result_data;
class Article(object):
    #正文处理
    def PublishArticle(self,cookieStr,content,articleId):
        try:
            htmlObj= lxml.html.fromstring(content);
            imgs=htmlObj.xpath("//img")
            if(imgs):
                for img in imgs:
                    imgUrl=img.get("src")
                    if(imgUrl):
                        imgUrl=img.get("data-src")
                        
                    imgDict={}
                    imgRe=self.UpLoadImg(cookieStr,imgUrl,imgDict);
                    imgObj=imgDict.get("imgObj",{})
                    reImgUrl=imgObj.get("src")
                    if(imgRe or not reImgUrl):
                        return "正文图片上传失败:"+imgRe;
                    img.set("src",reImgUrl)
                    img.set("data-src","")
                    img.set("data-size","normal")
                    img.set("data-rawwidth",str(imgObj.get("data-rawwidth","")))
                    img.set("data-rawheight",str(imgObj.get("data-rawheight","")))
                    img.set("data-watermark",str(imgObj.get("watermark","")))
                    img.set("data-original-src",str(imgObj.get("original_src","")))
                    img.set("data-watermark-src",str(imgObj.get("watermark_src","")))
                    img.set("data-private-watermark-src",str(imgObj.get("private_watermark_src","")))
                        
            saveJObject={}
            saveJObject["delta_time"]=1;
            saveJObject["content"]=lxml.html.tostring(htmlObj,encoding="utf8").decode("utf8");
            reDict={}
            saveRe=self.SaveDraft(cookieStr,json.dumps(saveJObject,ensure_ascii=False),reDict,articleId);
            if(saveRe):
                return "保存内容失败:"+saveRe;
            
            return None;
            
        except:
            return traceback.format_exc();
    
    
    #上传图片，以图片后缀结尾的url通过平台直接转，否则先下载图片再上传
    def UpLoadImg(self, cookieStr,imgUrl,returnDict):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://zhuanlan.zhihu.com/write',
            'Cookie':cookieStr,
            }
            boundaryStr='----WebKitFormBoundaryCihPuQpeVoB2HmvB'
            if(1==1):
                multipart_encoder = MultipartEncoder(
                fields={
                "source": "article",
                "url": imgUrl,                     
                    },
                boundary=boundaryStr
                )

                header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
                result=http.post("https://zhuanlan.zhihu.com/api/uploaded_images",headers=header ,data=multipart_encoder, verify = False);
                if(not result):
                    return "上传转换图片失败";
                jsonObj=result.json();
                if(jsonObj.get("error")):
                    return "删除更换转换图片失败:"+jsonObj.get("error").get("message");
                returnDict["imgObj"]=jsonObj;
                return None;
            #以下为先下载再当着本地上传，流程为申请上传参数，根据参数构造上传数据及头部-->因没有上传本地文件需求，赞不实现
            imgData=http.get(imgUrl,headers=header , verify = False);
            if(not imgData):
                return "下载图片失败";
            rem=re.search("\.jpeg|\.png|\.bmp|\.jpg|\.png",imgUrl.lower())
            imgExtType=None
            if(rem):
                imgExtType="image/"+rem.group(0).replace(".","");
            else:
                imgExtType=imgData.headers.get("Content-Type","")
            if(not re.search("image/",imgExtType)):
                imgExtType="image/jpeg";
            
            multipart_encoder = MultipartEncoder(
            fields={
                "watermark": "1",
                "app": "bbs",          
                "file": (
                "12.jpeg", imgData.content, imgExtType)
            },
            boundary=boundaryStr
        )

            header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
            result=http.post("http://photo.tianya.cn/photo?act=uploadphoto",headers=header ,data=multipart_encoder, verify = False);
            jsonRe=re.search("<body>.*</body>",result.text);
            if(jsonRe):
                jsonStr=jsonRe.group(0);
                jsonStr=jsonStr[6:len(jsonStr)-7];
                jsonObj=json.loads(jsonStr)
                if(not jsonObj.get("data").get("photo")):
                    return jsonObj.get("error","上传图片失败")
                paramDic["imgUrl"]=jsonObj["data"]["photo"][0]["mediumurl"]
                return None
            else:
                return "图片上传失败";
            
        except:
            return "图片上传失败:"+traceback.format_exc();
        
    #保存草稿，第一次保存的时候回生成文章id及其他参数
    def SaveDraft(self,cookieStr,params,returnDict,articleId=None):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://zhuanlan.zhihu.com/p/'+str(articleId)+'/edit' if articleId else "https://zhuanlan.zhihu.com/write",
            'Cookie':cookieStr,
            'content-type':'application/json',
            }
            saveUrl="https://zhuanlan.zhihu.com/api/articles/"+str(articleId)+"/draft" if articleId else "https://zhuanlan.zhihu.com/api/articles/drafts"
            result=None
            if(articleId):
                result= http.patch(saveUrl,headers=header ,data=params, verify = False);
            else:
                result=http.post(saveUrl,headers=header ,data=params, verify = False);
            if(result.status_code==200 and not result.text):
                return None;
           
            if(result.status_code==200 and result.text):
                reJobj=result.json()
                if(reJobj and reJobj.get("error")):
                    return "保存失败:"+reJobj.get("error").get("message");
                returnDict["articleObj"]=reJobj;
                return None;
            return "保存失败:"+str(result.status_code)+ result.text;
            
        except:
            return "保存草稿失败:"+traceback.format_exc();
        
    #获取推荐的标签,并加到当前文章下，以利于文章推荐和用户搜索，此步骤必须在保存草稿之后
    def GetRecommendTag(self,cookieStr,articleId):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Access-Control-Request-Headers':'x-ab-param,x-requested-with',
            'Access-Control-Request-Method':'GET',
            'Referer':'https://zhuanlan.zhihu.com/p/'+str(articleId)+'/edit' ,
            'Origin':'https://zhuanlan.zhihu.com',
            'Sec-Fetch-Mode':'cors',
            'Sec-Fetch-Site':'same-site',
            }
            saveUrl="https://www.zhihu.com/api/v4/articles/"+str(articleId)+"/recommend_topics";
            http.options(saveUrl,headers=header,verify=False)
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://zhuanlan.zhihu.com/p/'+str(articleId)+'/edit' ,
            'Origin':'https://zhuanlan.zhihu.com',
            'Sec-Fetch-Mode':'cors',
            'Sec-Fetch-Site':'same-site',
            'Cookie':cookieStr,
            }
            result=http.get(saveUrl,headers=header, verify = False);
            if(result):
                jsonObj=result.json();
                header["Content-type"]="application/json";
                for item in jsonObj["data"]:
                    http.post("https://zhuanlan.zhihu.com/api/articles/"+str(articleId)+"/topics",headers=header,data=json.dumps( item,ensure_ascii=False),verify=False);
            
            return None;
            
        except:
            return "获取推荐标签失败:"+traceback.format_exc();
    #发布
    def Publish(self,cookieStr,articleId,comment='anyone'):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://zhuanlan.zhihu.com/p/'+str(articleId)+'/edit' ,
            'Origin':'https://zhuanlan.zhihu.com',
            'Sec-Fetch-Mode':'cors',
            'Sec-Fetch-Site':'same-site',
            'content-type':'application/json',
            'Cookie':cookieStr,
            }
            postDict={
            "column":None,
            "commentPermission":comment
                }
            postJObj=json.dumps(postDict,ensure_ascii=False)
            result=http.put("https://zhuanlan.zhihu.com/api/articles/"+str(articleId)+"/publish",data=postJObj,headers=header,verify=False)
            if(result):
                reJobj=result.json()
                if(reJobj and reJobj.get("error")):
                    return "发布失败:"+reJobj.get("error",{}).get("message");
                if(reJobj and reJobj.get("content")):
                    return None;
                return result;
            return "发布失败:"+str(result.status_code)
            
        except:
            return "发布失败:"+traceback.format_exc();

class Question(object):
    #发布
    def Publish(self,taskData):
        try:
            cookieStr=taskData.get("cookie");
            postDict={
            "type":0,
            "title":taskData.get("title",""),
            "detail":taskData.get("content",""),
            "is_anonymous": True if taskData.get("anonymous")==1 else False,
            "topic_url_tokens":"",
             }
            if taskData.get("anonymous")!=1:
                postDict.pop("is_anonymous");
            arrayIds=[];
            recTag=self.GetRecommendTag(cookieStr,postDict["title"],arrayIds);
            if(arrayIds):
                postDict["topic_url_tokens"]=arrayIds;
            
            postStr=self.Encrypt(json.dumps(postDict,ensure_ascii=False));

            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://www.zhihu.com/creator' ,
            'Origin':'https://zhuanlan.zhihu.com',
            'Sec-Fetch-Mode':'cors',
            'Sec-Fetch-Site':'same-site',
            'content-type':'application/json',
            'Cookie':cookieStr,
            }

            result=http.post("https://www.zhihu.com/api/v4/questions",data=postStr,headers=header,verify=False)
            if(result):
                reJobj=result.json()
                if(reJobj and reJobj.get("error")):
                    return "发布失败:"+reJobj.get("error",{}).get("message");
                if(reJobj and reJobj.get("title")):
                    return None;
                return result;
            return "发布失败:"+str(result.status_code)
        except:
            return "发布失败"+traceback.format_exc();
    #加密，加密算法，未实现，预计通过执行js来获取结果
    def Encrypt(self,textStr):
        return "";
    #正文处理
    def PublishArticle(self,cookieStr,content,returnDict):
        try:
            htmlObj= lxml.html.fromstring(content);
            imgs=htmlObj.xpath("//img")
            if(imgs):
                for img in imgs:
                    imgUrl=img.get("src")
                    if(not imgUrl):
                        imgUrl=img.get("data-src")
                        
                    imgDict={}
                    imgRe=self.UpLoadImg(cookieStr,imgUrl,imgDict);
                    imgObj=imgDict.get("imgObj",{})
                    reImgUrl=imgObj.get("src")
                    if(imgRe or not reImgUrl):
                        return "正文图片上传失败:"+imgRe;
                    img.set("src",reImgUrl)
                    img.set("data-src","")
                    img.set("data-caption","")
                    img.set("data-size","normal")
                    img.set("data-rawwidth",str(imgObj.get("data-rawwidth","")))
                    img.set("data-rawheight",str(imgObj.get("data-rawheight","")))
                    img.set("data-watermark",str(imgObj.get("watermark","")))
                    img.set("data-original-src",str(imgObj.get("original_src","")))
                    img.set("data-watermark-src",str(imgObj.get("watermark_src","")))
                    img.set("data-private-watermark-src",str(imgObj.get("private_watermark_src","")))

            returnDict["content"]=lxml.html.tostring(htmlObj,encoding="utf8").decode("utf8");
            
            return None;
            
        except:
            return traceback.format_exc();
     #上传图片，以图片后缀结尾的url通过平台直接转，否则先下载图片再上传(目前不需要本地上传)
    def UpLoadImg(self, cookieStr,imgUrl,returnDict):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://www.zhihu.com/people/',
            'Cookie':cookieStr,
            }
            boundaryStr='----WebKitFormBoundaryCihPuQpeVoB2HmvB'
            if(1==1):
                multipart_encoder = MultipartEncoder(
                fields={
                "url": imgUrl,                     
                    },
                boundary=boundaryStr
                )

                header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
                result=http.post("https://www.zhihu.com/api/v4/uploaded_images",headers=header ,data=multipart_encoder, verify = False);
                if(not result):
                    return "上传转换图片失败";
                jsonObj=result.json();
                if(jsonObj.get("error")):
                    return "删除更换转换图片失败:"+jsonObj.get("error").get("message");
                returnDict["imgObj"]=jsonObj;
                return None;
            #以下为先下载再当着本地上传，流程为申请上传参数，根据参数构造上传数据及头部-->因没有上传本地文件需求，赞不实现
            imgData=http.get(imgUrl,headers=header , verify = False);
            if(not imgData):
                return "下载图片失败";
            rem=re.search("\.jpeg|\.png|\.bmp|\.jpg|\.png",imgUrl.lower())
            imgExtType=None
            if(rem):
                imgExtType="image/"+rem.group(0).replace(".","");
            else:
                imgExtType=imgData.headers.get("Content-Type","")
            if(not re.search("image/",imgExtType)):
                imgExtType="image/jpeg";
            
            multipart_encoder = MultipartEncoder(
            fields={
                "watermark": "1",
                "app": "bbs",          
                "file": (
                "12.jpeg", imgData.content, imgExtType)
            },
            boundary=boundaryStr
        )

            header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
            result=http.post("http://photo.tianya.cn/photo?act=uploadphoto",headers=header ,data=multipart_encoder, verify = False);
            jsonRe=re.search("<body>.*</body>",result.text);
            if(jsonRe):
                jsonStr=jsonRe.group(0);
                jsonStr=jsonStr[6:len(jsonStr)-7];
                jsonObj=json.loads(jsonStr)
                if(not jsonObj.get("data").get("photo")):
                    return jsonObj.get("error","上传图片失败")
                paramDic["imgUrl"]=jsonObj["data"]["photo"][0]["mediumurl"]
                return None
            else:
                return "图片上传失败";
            
        except:
            return "图片上传失败:"+traceback.format_exc();

    #获取推荐标签
    def GetRecommendTag(self,cookieStr,textStr,arrayIds):
       try:
           http=GetSession();
           saveUrl="https://www.zhihu.com/api/v4/recommendations/match-topics?";
           urlParams={
               "text":textStr,
               "type":"question"
               }
           header = {
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
           'Accept': '*',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.9',
           'x-requested-with': 'fetch',
           'Referer':'https://www.zhihu.com/people/' ,
           'Origin':'https://zhuanlan.zhihu.com',
           'Sec-Fetch-Mode':'cors',
           'Sec-Fetch-Site':'same-site',
           'Cookie':cookieStr,
           }
           result=http.get(saveUrl,headers=header,params=urlParams, verify = False);
           if(result):
               jsonObj=result.json();
               for item in jsonObj["data"]:
                   arrayIds.append(item.get("id",""));
                   
           
           return None;
           
       except:
            return "获取推荐标签失败:"+traceback.format_exc();

class ReAnswer(object):
    #正文处理
    def PublishArticle(self,cookieStr,content,returnDict,articleId):
        try:
            htmlObj= lxml.html.fromstring(content);
            imgs=htmlObj.xpath("//img")
            if(imgs):
                for img in imgs:
                    imgUrl=img.get("src")
                    if(imgUrl):
                        imgUrl=img.get("data-src")
                        
                    imgDict={}
                    imgRe=self.UpLoadImg(cookieStr,imgUrl,imgDict,articleId);
                    imgObj=imgDict.get("imgObj",{})
                    reImgUrl=imgObj.get("src")
                    if(imgRe or not reImgUrl):
                        return "正文图片上传失败:"+imgRe;
                    img.set("src",reImgUrl)
                    img.set("data-src","")
                    img.set("data-caption","")
                    img.set("data-size","normal")
                    img.set("data-rawwidth",str(imgObj.get("data-rawwidth","")))
                    img.set("data-rawheight",str(imgObj.get("data-rawheight","")))
                    img.set("data-watermark",str(imgObj.get("watermark","")))
                    img.set("data-original-src",str(imgObj.get("original_src","")))
                    img.set("data-watermark-src",str(imgObj.get("watermark_src","")))
                    img.set("data-private-watermark-src",str(imgObj.get("private_watermark_src","")))

            returnDict["content"]=lxml.html.tostring(htmlObj,encoding="utf8").decode("utf8");
            
            return None;
            
        except:
            return traceback.format_exc();

    #上传图片，以图片后缀结尾的url通过平台直接转，否则先下载图片再上传
    def UpLoadImg(self, cookieStr,imgUrl,returnDict,articleId):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://www.zhihu.com/question/'+str(articleId),
            'Cookie':cookieStr,
            }
            boundaryStr='----WebKitFormBoundaryCihPuQpeVoB2HmvB'
            if(1==1):
                multipart_encoder = MultipartEncoder(
                fields={
                "source": "answer",
                "url": imgUrl,                     
                    },
                boundary=boundaryStr
                )

                header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
                result=http.post("https://zhuanlan.zhihu.com/api/uploaded_images",headers=header ,data=multipart_encoder, verify = False);
                if(not result):
                    return "上传转换图片失败";
                jsonObj=result.json();
                if(jsonObj.get("error")):
                    return "删除更换转换图片失败:"+jsonObj.get("error").get("message");
                returnDict["imgObj"]=jsonObj;
                return None;
            #以下为先下载再当着本地上传，流程为申请上传参数，根据参数构造上传数据及头部-->因没有上传本地文件需求，赞不实现
            imgData=http.get(imgUrl,headers=header , verify = False);
            if(not imgData):
                return "下载图片失败";
            rem=re.search("\.jpeg|\.png|\.bmp|\.jpg|\.png",imgUrl.lower())
            imgExtType=None
            if(rem):
                imgExtType="image/"+rem.group(0).replace(".","");
            else:
                imgExtType=imgData.headers.get("Content-Type","")
            if(not re.search("image/",imgExtType)):
                imgExtType="image/jpeg";
            
            multipart_encoder = MultipartEncoder(
            fields={
                "watermark": "1",
                "app": "bbs",          
                "file": (
                "12.jpeg", imgData.content, imgExtType)
            },
            boundary=boundaryStr
        )

            header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
            result=http.post("http://photo.tianya.cn/photo?act=uploadphoto",headers=header ,data=multipart_encoder, verify = False);
            jsonRe=re.search("<body>.*</body>",result.text);
            if(jsonRe):
                jsonStr=jsonRe.group(0);
                jsonStr=jsonStr[6:len(jsonStr)-7];
                jsonObj=json.loads(jsonStr)
                if(not jsonObj.get("data").get("photo")):
                    return jsonObj.get("error","上传图片失败")
                paramDic["imgUrl"]=jsonObj["data"]["photo"][0]["mediumurl"]
                return None
            else:
                return "图片上传失败";
            
        except:
            return "图片上传失败:"+traceback.format_exc();
    #切换匿名 与 实名 回答
    def Switch(self,cookieStr,articleId,hidden):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://www.zhihu.com/question/'+str(articleId),# if articleId else "https://zhuanlan.zhihu.com/write",
            'Cookie':cookieStr,
            }
            saveUrl="https://www.zhihu.com/api/v4/questions/"+str(articleId)+"/anonyms"
            if(hidden):
                result=http.post(saveUrl,headers=header , verify = False);
            else:
                result= http.delete(saveUrl,headers=header,verify=False);

            if(result.status_code==200 and not result.text):
                return None;
            return "切换身份失败"+str(result.status_code)+ result.text;
            
        except:
            return "切换身份失败:"+traceback.format_exc();
    #提交
    def Publish(self,cookieStr,params,returnDict,articleId):
        try:
            http=GetSession();
            header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
            'Accept': '*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'x-requested-with': 'fetch',
            'Referer':'https://www.zhihu.com/question/'+str(articleId),# if articleId else "https://zhuanlan.zhihu.com/write",
            'Cookie':cookieStr,
            'content-type':'application/json',
            }
            saveUrl="https://www.zhihu.com/api/v4/questions/"+str(articleId)+"/answers?include=paid_info%2Cpaid_info_content%2Cadmin_closed_comment%2Creward_info%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cvoting%2Cis_thanked%2Cis_author%2Cis_nothelp%2Cis_recognized%2Cis_labeled%3Bmark_infos%5B*%5D.url%3Bauthor.badge%5B*%5D.topics"
            result=http.post(saveUrl,headers=header ,data=json.dumps( params,ensure_ascii=False), verify = False);

            if(result.status_code==200 and result.text):
                reJobj=result.json()
                if(reJobj and reJobj.get("error")):
                    return "发布失败:"+reJobj.get("error").get("message");
                returnDict["articleObj"]=reJobj;
                return None;
            return "发布失败"+str(result.status_code)+ result.text;
            
        except:
            return "发布失败:"+traceback.format_exc();
def python_control(all_params):
    result_data=dotask(all_params);
    return result_data


def main_control(params, logger=None):
    return python_control(params)


if __name__ == '__main__':
    ar=[123,456,789]
    dic={
        "title":"test",
        "content":"asdasdasd"
         }
    dic["d"]=ar;

    job=json.dumps(dic)
    #m= SaveDraft('_zap=18560fde-0a8d-4dd7-9f40-798dfe59e46c; d_c0="AJAkFHUllBCPTmDGhT1LrZH8ZxYGMs5GjQw=|1577599838"; _xsrf=AVqb34zOezKjnS3KdnDnP6tNNtw0gLBG; l_n_c=1; q_c1=e4f96f28e37f45cbb9576c4889835fe6|1581556565000|1581556565000; r_cap_id="Y2QzMWMxN2QwOTM2NDFkNjkzM2E2YzI0ODZiNjIzZWM=|1581556564|623976a15a68b25f82694f8d5aa2c682906c2299"; cap_id="OTgzYjY2NTVjODg5NGY3MzgwY2RkZDM1OTgyMjQ4ZWU=|1581556564|292bc32c24565d8ca33aee996601d2d52c65445b"; l_cap_id="MDZkMjdmN2Y4N2QwNGFlMGE5NzdjOWYxMTg3Mjg1OTI=|1581556564|a5e825d63abcbe814212eb780213176643eaa3a6"; n_c=1; __utma=51854390.1914165576.1581556567.1581556567.1581556567.1; __utmc=51854390; __utmz=51854390.1581556567.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1580633060,1580798743,1581391324,1581556580; capsion_ticket="2|1:0|10:1581558238|14:capsion_ticket|44:ZWYwNjU3ZWRmN2RkNDAyMGEwNTdiYjI3YjExOTA1Njg=|0788a8b44dbcf76b30aa45bf92a28288ea6c74b0166ff6c7ec966699e02c500b"; z_c0="2|1:0|10:1581558266|4:z_c0|92:Mi4xbHlfNEFnQUFBQUFBa0NRVWRTV1VFQ1lBQUFCZ0FsVk4tdmN4WHdCcFhrS2ZQXzJrUFBmdlRZRGM5SjZNRnB1Rk1B|9d833807551d9ed1f739cdd3009e3f340465c6abe1daccee717fdb67a58b7560"; __utmv=51854390.100--|2=registration_date=20160502=1^3=entry_date=20160502=1; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1581563297; KLBRSID=e42bab774ac0012482937540873c03cf|1581564519|1581563303',job);
    #print(m)
    #UpLoadImg("https://p3-dy.byteimg.com/img/tos-cn-p-0015/f0b4742d707546dfbc6233052220c7b2~c5_300x400.jpeg?from=2563711402_large","__cid=82; Hm_lvt_bc5755e0609123f78d0e816bf7dee255=1581387037; __guid=2102473600; __guid2=2102473600; __auc=ced3726117032033e3b3dd87e38; ADVC=382ea19dcb051f; ADVS=382ea19dcb051f; ASL=18303,0000k,3d9d403c; vk=b5cb678417bdf68d; deid=dd1e1fc3dc47d4ee31fcb4fa15ad8b69; sso=r=1221829937&sid=&wsid=E14F3D342F7E6533BCC7D3B07A885B55; user=w=gplwzz&id=141938209&f=1; temp=k=293448531&s=&t=1581387191&b=3ab2dc65241fe5e218cd9f3d6ae9a8f2&ct=1581387191&et=-1; right=web4=n&portal=n; temp4=rm=; u_tip=; bc_ids_m=sx; vip=293448531%3D0; bc_ids_w=th; bc_exp=0.2; JSESSIONID=abcw4T4odMWRb_Jx7lYax; __asc=f12d442e1703237bd45eb80feee; __ptime=1581390478768; Hm_lpvt_bc5755e0609123f78d0e816bf7dee255=1581390479; time=ct=1581390856.175; __u_a=v2.3.67; ty_msg=1581391482717_141938209_0_0_0_0_0_0_0_0_0_0_0_0; bbs_msg=1581391482760_141938209_0_0_0_0");
    taskData= {
   
        "cookie": '_zap=18560fde-0a8d-4dd7-9f40-798dfe59e46c; d_c0="AJAkFHUllBCPTmDGhT1LrZH8ZxYGMs5GjQw=|1577599838"; _xsrf=AVqb34zOezKjnS3KdnDnP6tNNtw0gLBG; q_c1=e4f96f28e37f45cbb9576c4889835fe6|1581556565000|1581556565000; r_cap_id="Y2QzMWMxN2QwOTM2NDFkNjkzM2E2YzI0ODZiNjIzZWM=|1581556564|623976a15a68b25f82694f8d5aa2c682906c2299"; cap_id="OTgzYjY2NTVjODg5NGY3MzgwY2RkZDM1OTgyMjQ4ZWU=|1581556564|292bc32c24565d8ca33aee996601d2d52c65445b"; l_cap_id="MDZkMjdmN2Y4N2QwNGFlMGE5NzdjOWYxMTg3Mjg1OTI=|1581556564|a5e825d63abcbe814212eb780213176643eaa3a6"; __utmz=51854390.1581556567.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); capsion_ticket="2|1:0|10:1581558238|14:capsion_ticket|44:ZWYwNjU3ZWRmN2RkNDAyMGEwNTdiYjI3YjExOTA1Njg=|0788a8b44dbcf76b30aa45bf92a28288ea6c74b0166ff6c7ec966699e02c500b"; z_c0="2|1:0|10:1581558266|4:z_c0|92:Mi4xbHlfNEFnQUFBQUFBa0NRVWRTV1VFQ1lBQUFCZ0FsVk4tdmN4WHdCcFhrS2ZQXzJrUFBmdlRZRGM5SjZNRnB1Rk1B|9d833807551d9ed1f739cdd3009e3f340465c6abe1daccee717fdb67a58b7560"; __utmv=51854390.100--|2=registration_date=20160502=1^3=entry_date=20160502=1; __utmc=51854390; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1581391324,1581556580,1581596336,1581643595; __utma=51854390.1914165576.1581556567.1581643589.1581647630.3; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1581656998; tst=r; KLBRSID=e42bab774ac0012482937540873c03cf|1581657001|1581643587',  # 默认空
        "coverUrl": "http://static.1sapp.com/qupost/images/2020/02/14/1581656418300483366water.jpg",#封面图
        "content": '<p><span>小静的悲哀</span></p><p>小静与老公在大学时便相识相爱。两人最后也幸福地走到了一起。</p><p>但在结婚前，小静和老公在校外同居，短短2年流产了4次。</p><p>难道两人不知道避孕吗？</p><p>知道。</p><p>但小静和老公都相信前7后8的说法，即使用这种方法避孕失败，也认为行房的时期太靠近“排卵期”了，所以一次次地“以身犯险”。</p><p>小静因流产过多，婚后想要孩子时，反而要不上了。婆婆没少给小静白眼……为此夫妻俩争吵不断、互相指责。<img data-src="http://static.1sapp.com/qupost/images/2020/02/14/1581656406949116658water.jpg" data-size="1500,1000" alt="避孕1.jpg" src="http://static.1sapp.com/qupost/images/2020/02/14/1581656406949116658water.jpg"></p><p><span>怪谁？</span></p><p>这两人都有责任。但小静老公要负主要责任。</p><p><span>性生活出了“翻车”事故，受伤最大的是女性。</span>因为人流不只是把胚胎连根拔起，还要带走胎盘，清理那些为怀孕增厚的子宫内膜。也就“刮宫”。</p><p>如果刮宫次数多，子宫就变成“贫瘠的沙漠”，将来如何孕育出健康宝宝？</p><p>男人要对自己的女人负责，就要采取更安全的避孕方式。</p><p>或许你深信“前7后8”，也采取了这种方式，女生也同意了。但出事后，你就要反思了。而不是给自己找理由，再次“冒险”。</p><p><span>目前来说最安全的避孕方式就是“性生活时使用避孕套”。而且还可以防止性病。防止不必要的感染。</span></p><p>现代社会对女性没有那么多的贞洁限制，<span>但让对方使用“避孕套”必须成为你的“底线”。</span>这才是对自己身体负责的态度。<img data-src="http://static.1sapp.com/qupost/images/2020/02/14/1581656418300483366water.jpg" data-size="1500,1000" alt="避孕2.jpg" src="http://static.1sapp.com/qupost/images/2020/02/14/1581656418300483366water.jpg"></p><p><span>前</span><span>7</span><span>后</span><span>8</span><span>不靠谱</span></p><p>咱先说说什么是“前7后8”。通俗的说法是，月经前7天和月经后8天，这段时间中没有安全措施的性生活是“安全的”。</p><p>许多人也相信这种说法，并尝试。但不幸的是这种方式导致了许多女性的意外怀孕。</p><p>据统计这种方式避孕的失败率高达20-30%。</p><p>千万不要有侥幸心理。卵子排出后能在体内存活1-2天，而精子在阴道中可存活3-5天。</p><p>“两个小东西”互相等待，它们是非常有耐心的。况且有些女性的月经并不规律，故，排卵也不规律。有的女性甚至一个月份时间排两个卵子……</p><p>所以，千万不要用这种方式避孕！<img data-src="http://static.1sapp.com/qupost/images/2020/02/14/1581656452995099359water.jpg" data-size="1500,1000" alt="避孕3.jpg" src="http://static.1sapp.com/qupost/images/2020/02/14/1581656452995099359water.jpg"></p><p><span>不要心存侥幸</span></p><p>意外怀孕对女性是非常不划算的。如果暂时没有生育计划，一定要用安全套避孕。</p><p>像安全期避孕、体外排精、紧急避孕药等都是妇科医生强烈不建议的。体外排精比安全期避孕更容易失败，紧急避孕药有副作用。再次强调：不要心存侥幸。</p><p>无论男女，都要记得：女性的生育资源有限。做一次人流提升一次不育的风险。</p><p><span>好好保护自己，保护对方，是爱情中的底线。</span><span> </span></p>',#发文正文，html数据
        "title":'小心流产的伤害，“前7后8”根本不靠谱，无生育计划请安全避孕',#标题
        "whoCanComment":"anyone",
        "taskType":"article",
        }
    taskDataA= {
   
        "cookie": '_zap=18560fde-0a8d-4dd7-9f40-798dfe59e46c; d_c0="AJAkFHUllBCPTmDGhT1LrZH8ZxYGMs5GjQw=|1577599838"; _xsrf=AVqb34zOezKjnS3KdnDnP6tNNtw0gLBG; q_c1=e4f96f28e37f45cbb9576c4889835fe6|1581556565000|1581556565000; r_cap_id="Y2QzMWMxN2QwOTM2NDFkNjkzM2E2YzI0ODZiNjIzZWM=|1581556564|623976a15a68b25f82694f8d5aa2c682906c2299"; cap_id="OTgzYjY2NTVjODg5NGY3MzgwY2RkZDM1OTgyMjQ4ZWU=|1581556564|292bc32c24565d8ca33aee996601d2d52c65445b"; l_cap_id="MDZkMjdmN2Y4N2QwNGFlMGE5NzdjOWYxMTg3Mjg1OTI=|1581556564|a5e825d63abcbe814212eb780213176643eaa3a6"; __utmz=51854390.1581556567.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); capsion_ticket="2|1:0|10:1581558238|14:capsion_ticket|44:ZWYwNjU3ZWRmN2RkNDAyMGEwNTdiYjI3YjExOTA1Njg=|0788a8b44dbcf76b30aa45bf92a28288ea6c74b0166ff6c7ec966699e02c500b"; z_c0="2|1:0|10:1581558266|4:z_c0|92:Mi4xbHlfNEFnQUFBQUFBa0NRVWRTV1VFQ1lBQUFCZ0FsVk4tdmN4WHdCcFhrS2ZQXzJrUFBmdlRZRGM5SjZNRnB1Rk1B|9d833807551d9ed1f739cdd3009e3f340465c6abe1daccee717fdb67a58b7560"; __utmv=51854390.100--|2=registration_date=20160502=1^3=entry_date=20160502=1; __utma=51854390.1914165576.1581556567.1581643589.1581647630.3; tst=r; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1581556580,1581596336,1581643595,1581940455; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1581940753; KLBRSID=0a401b23e8a71b70de2f4b37f5b4e379|1581941063|1581940452',  # 默认空
        "content": '',#发文正文，html数据  <p>比如好多技术人员看不惯微软，但是干不掉别个</p><img src="https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1581951104955&di=4cb93b41e9c44f730f347e414761be3c&imgtype=jpg&src=http%3A%2F%2Fimg1.imgtn.bdimg.com%2Fit%2Fu%3D2518660666%2C645688966%26fm%3D214%26gp%3D0.jpg"></img>
        "title":'怎样拥有别人看不惯自己而别人又干不掉自己的技术？',#标题
        "anonymous":1,#匿名提问
        "taskType":"question",
        }
    taskDataR= {
   
        "cookie": '_zap=18560fde-0a8d-4dd7-9f40-798dfe59e46c; d_c0="AJAkFHUllBCPTmDGhT1LrZH8ZxYGMs5GjQw=|1577599838"; _xsrf=AVqb34zOezKjnS3KdnDnP6tNNtw0gLBG; q_c1=e4f96f28e37f45cbb9576c4889835fe6|1581556565000|1581556565000; r_cap_id="Y2QzMWMxN2QwOTM2NDFkNjkzM2E2YzI0ODZiNjIzZWM=|1581556564|623976a15a68b25f82694f8d5aa2c682906c2299"; cap_id="OTgzYjY2NTVjODg5NGY3MzgwY2RkZDM1OTgyMjQ4ZWU=|1581556564|292bc32c24565d8ca33aee996601d2d52c65445b"; l_cap_id="MDZkMjdmN2Y4N2QwNGFlMGE5NzdjOWYxMTg3Mjg1OTI=|1581556564|a5e825d63abcbe814212eb780213176643eaa3a6"; __utmz=51854390.1581556567.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); capsion_ticket="2|1:0|10:1581558238|14:capsion_ticket|44:ZWYwNjU3ZWRmN2RkNDAyMGEwNTdiYjI3YjExOTA1Njg=|0788a8b44dbcf76b30aa45bf92a28288ea6c74b0166ff6c7ec966699e02c500b"; z_c0="2|1:0|10:1581558266|4:z_c0|92:Mi4xbHlfNEFnQUFBQUFBa0NRVWRTV1VFQ1lBQUFCZ0FsVk4tdmN4WHdCcFhrS2ZQXzJrUFBmdlRZRGM5SjZNRnB1Rk1B|9d833807551d9ed1f739cdd3009e3f340465c6abe1daccee717fdb67a58b7560"; __utmv=51854390.100--|2=registration_date=20160502=1^3=entry_date=20160502=1; __utmc=51854390; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1581391324,1581556580,1581596336,1581643595; __utma=51854390.1914165576.1581556567.1581643589.1581647630.3; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1581656998; tst=r; KLBRSID=e42bab774ac0012482937540873c03cf|1581657001|1581643587',  # 默认空
        "content": '<p>在人际交往中，女人往往比男人聪明。</p><p>一个女人，经历的男人多了，也就积累了一身的本领。不管是交男朋友还是嫁人，她的眼光都会很敏锐，能找到最适合她的人。</p><p><img data-src="http://static.1sapp.com/qupost/images/2020/02/14/1581670782986027533.jpg" data-size="1024,999" src="http://static.1sapp.com/qupost/images/2020/02/14/1581670782986027533.jpg"><span></span></p><p>不仅眼光准，而且套路深。因为经历多了，往往都有着深埋心底的情伤，被人伤得够深，也就积累了一身厚厚的铠甲，百毒不侵。再和人交往时，不管身边的人对他再好，她也很难再付出深情。</p><p>￼这样的女人，不再用“心”去谈一场恋爱，而是用“套路”去玩弄男人的情感。对那些想要认认真真谈一场正经恋恋，正经八百奔着往结婚去的老实男人来说，遇上这样的女人，根本没有招架之力。</p><p>等到她享受了你的卑微、用心和供养，等到她某天突然对你厌倦的时候，她会决绝地和你分手，一点点念想都不会给你。</p><p>对老实男人来说，要想避免受到伤害，就要有识人辨人的能力。</p>',#发文正文，html数据
        "anonymous":1,#匿名回答
        "taskType":"reanswer",
        "answerId":"66248534"
        }
    # PublishArticle("123",taskData["content"],"123");
    #PublishArticle(taskData["cookie"],taskData);
    pprint(main_control(taskDataA))












