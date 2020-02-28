

# coding: utf-8

from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import re
import uuid
import lxml.html
import requests
import time
import datetime
import urllib.parse
import traceback
from pprint import pprint
import random
import hashlib
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
   
        "action":"edit",  # 默认free杂谈，博客板块
        "attach": [],#默认空
        "cover_height": "",#发文正文，html数据
        "cover_pic":"",  #文章来源url， 默认:选填 http://
        "cover_width":"",#标题
        "deyihao":0,#是否申明原创
        "draft":0,
        "fid":taskData["categoryId"],
        "hidereply":0,
        "tags":taskData.get("tags",[]),
        "pcip":"",#61.157.64.127
        "pid":"",
        "readperm":0,
        "review":True,
        "seccode":"",
        "sortid":0,
        "allownoticeauthor":1,
        "stick":0,
        "subject":taskData["title"],
        "tid":0,
        "topicid":taskData.get("topicId",""),
        "typeid":0,
        "types":[],
        }
    uidStr=GetSecHash(taskData["cookie"],params);
    if(uidStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=uidStr;
        return result_data;
   

    pubResult=PublishArticle(taskData["cookie"],taskData["content"],params);
    if(pubResult!=None):
        result_data["code"]=-1;
        result_data["msg"]=pubResult;
        return result_data;

    pubStr=Publish(taskData["cookie"],params);
    if(pubStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=pubStr;
        return result_data;
    return result_data

#正文处理
def PublishArticle(cookieStr,content,params):
    try:
        htmlObj= lxml.html.fromstring(content);
        imgs=htmlObj.xpath("//img")
        if(imgs):
            for img in imgs:
                imgUrl=img.get("src")
                if(imgUrl):
                    imgUrl=img.get("data-src")
                    
                imgDict={}
                imgRe=UpLoadImg(cookieStr,imgUrl,params["categoryId"],imgDict);
                imgObj=imgDict.get("imgObj",{})
                reImgUrl=imgObj.get("url")
                if(imgRe or not reImgUrl):
                    return "正文图片上传失败:"+imgRe;
                img.set("src",reImgUrl)
                img.set("data-src","")
                img.set("style","max-width:720px")
                img.set("data-review",str(imgObj.get("review","true")))
                img.set("width",str(imgObj.get("width","720")))
        params["message"]=lxml.html.tostring(htmlObj,encoding="utf8").decode("utf8");
        return None;
        
    except:
        return traceback.format_exc();


#上传图片，以图片后缀结尾的url通过平台直接转，否则先下载图片再上传
def UpLoadImg(cookieStr,imgUrl,fid,returnDict):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie':cookieStr,
        }
        boundaryStr='----WebKitFormBoundaryCihPuQpeVoB2HmvB'
        #慈湖为直接url转换，改平台不支持
        if(1==2):
            multipart_encoder = MultipartEncoder(
            fields={
            "source": "article",
            "url": imgUrl,                     
                },
            boundary=boundaryStr
            )

            header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
            result=http.post("http://www.deyi.com/pc/upload/ctrl?action=image&encode=utf-8&fid=",headers=header ,data=multipart_encoder, verify = False);
            if(not result):
                return "上传转换图片失败";
            jsonObj=result.json();
            if(jsonObj.get("error")):
                return "删除更换转换图片失败:"+jsonObj.get("error").get("message");
            returnDict["imgObj"]=jsonObj;
            return None;
        #以下为先下载再当着本地上传，
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
            "id": "WU_FILE_0",
            "name": "1."+imgExtType.split('/')[1],          
            "type": imgExtType,
            "lastModifiedDate": datetime.datetime.utcnow(),
            "size":len(imgData.content),
            "file": (
            "1."+imgExtType.split('/')[1], imgData.content, imgExtType)
        },
        boundary=boundaryStr
    )
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'X_Requested_With':'XMLHttpRequest',
        'Referer':'http://www.deyi.com/v2/editor/js/ue/dialogs/image/image.html',
        'Origin':'http://www.deyi.com',
        'Cookie':cookieStr,
        }
        header["Content-Type"]="multipart/form-data; boundary="+boundaryStr;
        result=http.post("http://www.deyi.com/pc/upload/ctrl?action=image&encode=utf-8&fid="+str(fid),headers=header ,data=multipart_encoder, verify = False);
        if(not result or not result.text):
            return "上传图片失败";
        jsonRe=result.json();
        if(jsonRe):
            if(jsonRe.get("msg")=="ok" and jsonRe.get("data")):
                paramDic["imgObj"]=jsonRe["data"]
                return None
            return jsonRe.get("msg","上传图片失败")
            
        else:
            return "图片上传失败";
        
    except:
        return "图片上传失败:"+traceback.format_exc();
    
#保存草稿，暂时未实现
def SaveDraft(cookieStr,params,returnDict,articleId=None):
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
    
def Publish(cookieStr,params):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer':'http://www.deyi.com/v2/forum-post-action-newthread-fid-'+str(params["fid"])+'.html' ,
        'Origin':'http://www.deyi.com',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With':'XMLHttpRequest',
        'Cookie':cookieStr,
        }
        postJObj=json.dumps(params,ensure_ascii=False)
        result=http.put("http://www.deyi.com/pc/editor/post",data=postJObj,headers=header,verify=False)
        if(result):
            reJobj=result.json()
            if(reJobj and reJobj.get("msg")!="ok"):
                return "发布失败:"+reJobj.get("msg");
            if(reJobj and reJobj.get("data",{}).get("backurl")):
                return None;
            return result;
        return "发布失败:"+str(result.status_code)
        
    except:
        return "发布失败:"+traceback.format_exc();

def GetSecHash(cookieStr,params):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie':cookieStr,
    }
        result=http.get("http://www.deyi.com/v2/forum-post-action-newthread-fid-"+str(params.get("fid",""))+".html",headers=header , verify = False);
        if(not result):
            return "获取sechash失败"
        useridObj=re.search('data-sechash=".*"',result.text);
        if(useridObj):
            useridStr=useridObj.group(0).split('"')[1];
            params["sechash"]=useridStr;
            return None;
        else:
            return "未找到sechash信息";
    except:
        return "获取sechash信息失败:"+traceback.format_exc();

def python_control(all_params):
    result_data=dotask(all_params);
    return result_data


def main_control(params, logger=None):
    return python_control(params)


if __name__ == '__main__':
    #m= GetFingerData("我是你哈哈","12133212");
    #print(m)
    #UpLoadImg("https://p3-dy.byteimg.com/img/tos-cn-p-0015/f0b4742d707546dfbc6233052220c7b2~c5_300x400.jpeg?from=2563711402_large","__cid=82; Hm_lvt_bc5755e0609123f78d0e816bf7dee255=1581387037; __guid=2102473600; __guid2=2102473600; __auc=ced3726117032033e3b3dd87e38; ADVC=382ea19dcb051f; ADVS=382ea19dcb051f; ASL=18303,0000k,3d9d403c; vk=b5cb678417bdf68d; deid=dd1e1fc3dc47d4ee31fcb4fa15ad8b69; sso=r=1221829937&sid=&wsid=E14F3D342F7E6533BCC7D3B07A885B55; user=w=gplwzz&id=141938209&f=1; temp=k=293448531&s=&t=1581387191&b=3ab2dc65241fe5e218cd9f3d6ae9a8f2&ct=1581387191&et=-1; right=web4=n&portal=n; temp4=rm=; u_tip=; bc_ids_m=sx; vip=293448531%3D0; bc_ids_w=th; bc_exp=0.2; JSESSIONID=abcw4T4odMWRb_Jx7lYax; __asc=f12d442e1703237bd45eb80feee; __ptime=1581390478768; Hm_lpvt_bc5755e0609123f78d0e816bf7dee255=1581390479; time=ct=1581390856.175; __u_a=v2.3.67; ty_msg=1581391482717_141938209_0_0_0_0_0_0_0_0_0_0_0_0; bbs_msg=1581391482760_141938209_0_0_0_0");
    taskData= {
   
        "cookie": "GW51_2132_saltkey=a5nhLTSH; GW51_2132_lastvisit=1581986518; UM_distinctid=17055f589c012a-0a0ccd3a634566-313f69-100200-17055f589c11a3; GW51_2132_atarget=1; GW51_2132_connect_is_bind=0; GW51_2132_editormode_e=1; GW51_2132_smile=1D1; _d_id=7de5ef6e6cf148860d095afeec8573; GW51_2132_auth=544feHMck4EhkQEH0B7bz4SuBRBgfyS5aRztLipus0PgzfRIC9nEkcFXr9d1Hr5NTgapNGa7lr1vmac85Ar10dRhcg; GW51_2132_lastcheckfeed=33152%7C1582011489; GW51_2132_nofavfid=1; GW51_2132_visitedfid=2D37D88; GW51_2132_ulastactivity=12ce1msR%2BT6TWVT5m46nGY5yk0OwdTxKv2Yr%2FV4XhtC62pBZyvnS; GW51_2132_forum_lastvisit=D_88_1581992967D_37_1581992981D_2_1582013154; GW51_2132_viewid=tid_414558; GW51_2132_sid=Zhulzk; GW51_2132_lip=61.157.64.127%2C1582012351; CNZZDATA4508812=cnzz_eid%3D884414251-1581990119-%26ntime%3D1582017286; GW51_2132_st_t=33152%7C1582020807%7Cdd20fce801340da062c1b82c032b7cfd; GW51_2132_lastact=1582021508%09forum.php%09relatekw",  # 默认空
        "categoryId": 2,#板块分类id
        "content": '<p>在人际交往中，女人往往比男人聪明。</p><p>一个女人，经历的男人多了，也就积累了一身的本领。不管是交男朋友还是嫁人，她的眼光都会很敏锐，能找到最适合她的人。</p><p><img data-src="http://static.1sapp.com/qupost/images/2020/02/14/1581670782986027533.jpg" data-size="1024,999" src="http://static.1sapp.com/qupost/images/2020/02/14/1581670782986027533.jpg"><span></span></p><p>不仅眼光准，而且套路深。因为经历多了，往往都有着深埋心底的情伤，被人伤得够深，也就积累了一身厚厚的铠甲，百毒不侵。再和人交往时，不管身边的人对他再好，她也很难再付出深情。</p><p>￼这样的女人，不再用“心”去谈一场恋爱，而是用“套路”去玩弄男人的情感。对那些想要认认真真谈一场正经恋恋，正经八百奔着往结婚去的老实男人来说，遇上这样的女人，根本没有招架之力。</p><p>等到她享受了你的卑微、用心和供养，等到她某天突然对你厌倦的时候，她会决绝地和你分手，一点点念想都不会给你。</p><p>对老实男人来说，要想避免受到伤害，就要有识人辨人的能力。</p>',#发文正文，html数据
        "title":'抢购商品的技巧',#标题
       
        }
 
    
    #PublishArticle(taskData["cookie"],taskData);
    pprint(main_control(taskData))














