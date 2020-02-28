

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
   
        "params.item":taskData.get("category","free"),  # 默认free杂谈，博客板块
        "params.subItem": "",#默认空

        "params.content": taskData["content"],#发文正文，html数据
        "params.action": "",  #文章来源url， 默认:选填 http://
      
        "params.title":taskData.get("title",""),#标题
      
        "parmas.bScore":"true" if(taskData.get("isOrignal",1)==1) else "false",#是否申明原创
        #"parmas.uuid":"",
        }
    uidStr=GetUserId(taskData["cookie"],params);
    if(uidStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=uidStr;
        return result_data;
    uuidStr=GetUUId(taskData["cookie"],params);
    if(uuidStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=uuidStr;
        return result_data;
    params["params.action"]=GetFingerData(taskData["content"],params["params.userid"])
    pubResult=PublishArticle(taskData["cookie"],params);
    if(pubResult!=None):
        result_data["code"]=-1;
        result_data["msg"]=pubResult;
        return result_data;
    return result_data

#发布
def PublishArticle(cookieStr,params):
    try:
        if(params.get("params.userid",None)):
            params.pop("params.userid");
        http=GetSession();
        header = {
        # 'User-Agent': WEB_USERAGRNT,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Type':'application/x-www-form-urlencoded',
        'Referer':'http://bbs.tianya.cn/compose.jsp',
        'Origin':'http://bbs.tianya.cn',
        'Cookie':cookieStr,
    } 
        content=params["params.content"];
        imgUrls=re.findall("http[s]{0,2}://[0-9a-zA-Z_\.\*\?~!@#\$%&\(\)\+-=\}\{\]\[';\":,><\|]{5,}",content)
        if(imgUrls):
            for img in imgUrls:
                imgDic={"imgUrl":None}
                imgUpResult=UpLoadImg(img,cookieStr,imgDic)
                if( imgUpResult):
                    return imgUpResult;
                else:
                    content=content.replace(img,imgDic["imgUrl"])

                params["params.content"]=content;
        result=http.post("http://bbs.tianya.cn/api?method=bbs.ice.compose",data=params, headers=header , verify = False).json();
        
        if(result and result.get("success","1")=="0"):
            return None;
        else:
            return "发布失败:"+ result.get("message") if result else None;
        
    except:
        return traceback.format_exc();

#获取action指纹数据,此处目前只适用了复制粘贴操作类型的指纹，如要根据内容计算指纹需要将内容转换为所有的按键码，比较麻烦
def GetFingerData(content,uid):
    fS=random.randint(2,6);
    fT=int(float(time.time())*1000)
    fE=random.randint(3021,96287)
    fAll="f"+str(fS)+"."+str(fT)+"."+str(fE)

    pS=random.randint(2,8);
    pT=fT;
    pE=pS*random.randint(632,967)
    pAll="p"+str(pS)+"."+str(pT)+"."+str(pE)

    bS=random.randint(3,6);
    bT=random.randint(16,18);
    bE=bS*random.randint(632,967)
    bAll="b"+str(bS)+"."+str(bT)+"."+str(bE)
    fingAll=fAll+ ",,,,,,,,,,,,,,"+pAll+","+bAll;
    c = content[0:100];
    c = re.sub("/[^a-z|A-Z|\d|\u4E00-\uFA29]/g","", c,flags=re.I)
    A =0;
    if( len(c) <= 0):
        A=0;
    else:
        l=len(c)
        A=random.randint(0,l-1);
    md5Str1=(fingAll+uid+str(A)).encode("utf8")
    md51=hashlib.md5(md5Str1).hexdigest()
    md5Str2=str(c[A:A+1]).encode("utf8")
    md52=hashlib.md5(md5Str2).hexdigest()
    #浏览器信息，需要手机一批做随机用
    all=fingAll+ "|"+md51+"|"+md52+"|Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36|v2.3.1";
    return all
#上传图片，以图片后缀结尾的url通过平台直接转，否则先下载图片再上传
def UpLoadImg(imgUrl,cookieStr,paramDic):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer':'http://bbs.tianya.cn/compose.jsp',
        'Cookie':cookieStr,
    }

        imgExt=imgUrl[len(imgUrl)-6:].lower();
        rem=re.search("\.jpeg|\.png|\.bmp|\.jpg|\.png",imgExt)
        if(rem):
            result=http.get("http://photo.tianya.cn/photo?act=uploadUrlImage&var=data&imageUrl="+imgUrl+"&app=bbs&_="+str(int(time.time)),headers=header , verify = False).text;
            if(not result):
                return "上传转换图片失败";
            result=re.search("\{.*\}",result)
            if(result):
                return "上传转换图片失败";
            jsonObj=json.loads(result);
            paramDic["imgUrl"]=jsonObj["data"]["mUrl"]
            return None;
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
        boundaryStr='----WebKitFormBoundaryCihPuQpeVoB2HmvB'
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

#获取用户uuid，发文是需要此参数
def GetUUId(cookieStr,params):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer':'http://bbs.tianya.cn/my_compose_list.jsp',
        'Cookie':cookieStr,
    }
        result=http.get("http://bbs.tianya.cn/compose.jsp",headers=header , verify = False).text;
        useridObj=re.search('name="uuid"[\s]{0,}value=".*"',result);
        if(useridObj):
            useridStr=useridObj.group(0).split('"')[3];
            params["parmas.uuid"]=useridStr;
            return None;
        else:
            return "未找到UUID信息";
    except:
        return "获取UUID失败"+traceback.format_exc();
#获取用户id，指纹是需要此参数
def GetUserId(cookieStr,params):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Referer':'http://bbs.tianya.cn/compose.jsp',
        'Cookie':cookieStr,
    }
        result=http.get("http://www.tianya.cn/api/tw?var=msgObj&method=messagecount.ice.select&params.userId=&_="+str(int(time.time())*1000),headers=header , verify = False).text;
        useridObj=re.search('"userId":[0-9a-zA-Z]{3,}',result);
        if(useridObj):
            useridStr=useridObj.group(0).split(':')[1];
            params["params.userid"]=useridStr;
            return None;
        else:
            return "未找到用户信息";
    except:
        return "获取用户信息失败:"+traceback.format_exc();

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
   
        "cookie": "__cid=82; Hm_lvt_bc5755e0609123f78d0e816bf7dee255=1581387037; __guid=2102473600; __guid2=2102473600; __auc=ced3726117032033e3b3dd87e38; ADVC=382ea19dcb051f; ADVS=382ea19dcb051f; vk=b5cb678417bdf68d; deid=dd1e1fc3dc47d4ee31fcb4fa15ad8b69; sso=r=1221829937&sid=&wsid=E14F3D342F7E6533BCC7D3B07A885B55; user=w=gplwzz&id=141938209&f=1; temp=k=293448531&s=&t=1581387191&b=3ab2dc65241fe5e218cd9f3d6ae9a8f2&ct=1581387191&et=-1; right=web4=n&portal=n; temp4=rm=; u_tip=; bc_ids_m=sx; tianyaATC=tianya,9930109,26186,28395,1581391712358,bbs.tianya.cn%2Flist-free-1.shtml; ASL=18304,000kj,3d9d403c3d9d403c; vip=293448531%3D0; bc_ids_w=tl; bc_exp=0.2; __visit=wpopa%3D2122; tianya1=12980,1581498168,1,86400; __asc=167a023317038a2fa8a1cefabfe; time=ct=1581498306.948; __ptime=1581498307715; Hm_lpvt_bc5755e0609123f78d0e816bf7dee255=1581498308; __u_a=v2.3.8; ty_msg=1581498593724_141938209_0_0_0_0_0_0_0_0_0_0_0_0; bbs_msg=1581498593736_141938209_0_0_0_0",  # 默认空
        "category": "free",#板块分类
        "content": '昨天看到网上有人总结的“宅在家里的日常”，母亲那一栏多是“骂老公，骂孩子”，父亲和孩子那一栏多是“被骂”，下面很多网友的评论也很可乐\r\nhttp://i1.go2yd.com/image.php?url=0ObzuIiohE\r\n用一种娇嗔的语气说：“不管我在家里做什么都会被骂，感觉我跟爸妈的关系已经到达临界点了！',#发文正文，html数据
        "title":'为什么很多儿媳不愿意跟婆婆一起住？看这对夫妻，堪称教科书',#标题
        "isOrignal":1,#是否申明原创
        #"params.content": '女人在不同阶段所想要的爱情是不https://p3-dy.byteimg.com/img/tos-cn-p-0015/f0b4742d707546dfbc6233052220c7b2~c5_300x400.jpeg?from=2563711402_large一样的。当她们在25岁26岁的时候想要那种浪漫和美丽的爱情，幻想成为偶像剧的女主角。\r\n30多岁有孩子的时候，爱情则是追求稳定依靠，而到了40多岁的年纪就是更多地考虑孩子的未来生活了。',#发文正文，html数据
        
        }
    #PublishArticle(taskData["cookie"],taskData);
    pprint(main_control(taskData))












