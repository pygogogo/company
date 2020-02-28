

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
   
        "posttime":int(time.time()),  # 默认free杂谈，博客板块
        "wysiwyg": 0,#默认空
        "typeid": taskData.get("categoryId",0),#发文正文，html数据
        "subject": taskData.get("title",""),  #文章来源url， 默认:选填 http://
        "checkbox":0,#标题
        "message":taskData.get("content",""),#是否申明原创
        "price":"",
        "tags":"",
        "allownoticeauthor":1,
        "usesig":1,
        "save":"",
        }
    uidStr=GetFormHash(taskData["cookie"],params);
    if(uidStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=uidStr;
        return result_data;
    uuidStr=CheckPostRule(taskData["cookie"],taskData.get("categoryId",0));
    if(uuidStr!=None):
        result_data["code"]=-1;
        result_data["msg"]=uuidStr;
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
        'Referer':'http://bbs.20z.com/forum.php?mod=post&action=newthread&fid=2',
        'Origin':'http://bbs.20z.com',
        'Cookie':cookieStr,
         } 
        content=params.get("message","");
        htmlObj= lxml.html.fromstring(content);
        imgs=htmlObj.xpath("//img")
        if(imgs):
            for img in imgs:
                imgUrl=img.get("src")
                if(not imgUrl):
                    imgUrl=img.get("data-src");
                img.text="[img=550,363]"+imgUrl+"[/img]";

        rootNodeText="\r\n".join( htmlObj.xpath("//text()")).encode("gbk",'ignore')

        title=params.get("subject","").encode("gbk",'ignore')
        titleBianMa=urllib.parse.quote(title)
        params["subject"]=titleBianMa;

        contentBianMa = urllib.parse.quote(rootNoderootNodeText)
        params["message"]=contentBianMa;
        
       

        result=http.post("http://bbs.20z.com/forum.php?mod=post&action=newthread&fid=2&extra=&topicsubmit=yes",data=params, headers=header , verify = False,);
        
        if(result and  "新主题需要审核，您的帖子通过审核后才能显示" in result.text):
            return None;
        else:
            return "发布失败:";
        
        
    except:
        return traceback.format_exc();

#发文前监测是否有权限
def CheckPostRule(cookieStr,categoryId):
    #http://bbs.20z.com/forum.php?mod=ajax&action=checkpostrule&ac=newthread&inajax=yes
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer':'http://bbs.20z.com/forum.php?mod=post&action=newthread&fid='+str(categoryId),
        'Cookie':cookieStr,
    }
        result=http.get("http://bbs.20z.com/forum.php?mod=ajax&action=checkpostrule&ac=newthread&inajax=yes",headers=header , verify = False);
        if(not result):
            return "监测发文权限失败";
        if(result.text and "<root><![CDATA[]]></root>" in result.text):
            return None;
        else:
            return "未找到formhash信息";
    except:
        return "获取formhash信息失败:"+traceback.format_exc();
#获取formid
def GetFormHash(cookieStr,params):
    try:
        http=GetSession();
        header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie':cookieStr,
    }
        result=http.get("http://bbs.20z.com/forum.php?mod=post&action=newthread&fid=2",headers=header , verify = False).text;
        useridObj=re.search('name="formhash"[\s]{0,}value="[0-9a-zA-Z\s]{3,}"',result);
        if(useridObj):
            useridStr=useridObj.group(0).split('"')[3];
            params["formhash"]=useridStr;
            return None;
        else:
            return "未找到formhash信息";
    except:
        return "获取formhash信息失败:"+traceback.format_exc();

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
    lll="在人际交往中，女人往往比男人聪明。一个女人，经历的男人多了，也就积累了一身的本领。不管是交男朋友还是嫁人，她的眼光都会很敏锐，能找到最适合她的人。[img=550,363]http://static.1sapp.com/qupost/images/2020/02/14/1581670782986027533.jpg[/img]不仅眼光准，而且套路深。因为经历多了，往往都有着深埋心底的情伤，被人伤得够深，也就积累了一身厚厚的铠甲，百毒不侵。再和人交往时，不管身边的人对他再好，她也很难再付出深情。￼这样的女人，不再用“心”去谈一场恋爱，而是用“套路”去玩弄男人的情感。对那些想要认认真真谈一场正经恋恋，正经八百奔着往结婚去的老实男人来说，遇上这样的女人，根本没有招架之力。等到她享受了你的卑微、用心和供养，等到她某天突然对你厌倦的时候，她会决绝地和你分手，一点点念想都不会给你。对老实男人来说，要想避免受到伤害，就要有识人辨人的能力。".encode("gbk",'ignore')
    
    #PublishArticle(taskData["cookie"],taskData);
    pprint(main_control(taskData))













