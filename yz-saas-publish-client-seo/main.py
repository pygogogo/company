import requests
import urllib.parse
import json
import re
from lxml import etree
import datetime
import base64




class BaiDuZhiDao(object):
    def __init__(self,title,content,cookie,image_url):
        self.headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    "Cookie":cookie,
        }
        self.upload_url = "https://zhidao.baidu.com/submit/ajax/"
        self.image_url = image_url
        self.title = title
        self.content = content
        self.upload_headers =  {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
        "Accept": "*/*",
        "Origin": "https://zhidao.baidu.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Referer": "https://zhidao.baidu.com/new?word=&ie=GBK&entry=common_header",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,ja;q=0.8",
        "Cookie": cookie,
    }


    def get_tag(self):
        tag_url = "https://zhidao.baidu.com/api/gettag"
        data = {
            'type': '0',
            'title': urllib.parse.quote(self.title),
            'content': urllib.parse.quote(self.content),
            'has_pic': '0',
        }
        response = requests.post(tag_url, data=data, headers=self.headers)
        tag_name = response.json()["data"]["new_tag"][0]["tagname"]
        return tag_name

    def upload_pic(self):
        if len(self.image_url) == 0:
            return
        else:
            result = ""
            for image in self.image_url:
                response = requests.get(image)
                data = {
                    "name": "1.png",
                    "cm": "100672",
                    "id": "WU_FILE_2",
                    "type": "image/png",
                    "lastModifiedDate": "Mon Jan 06 2020 15:17:14 GMT+0800 (中国标准时间)",
                    "size": "170185",
                }
                files = {"image": ('1.png', response.content, 'image/jpeg')}
                res2 = requests.post(self.upload_url, headers=self.upload_headers, data=data, files=files, verify=False)
                final_url = res2.json()["url"]
                final_res = '<p><img src=%s /></p>'%final_url
                result +=final_res
            return result




    def get_stoken(self):
        stoken_url = "https://zhidao.baidu.com/api/loginInfo"
        response = requests.get(stoken_url, headers=self.headers)
        print(response.json()['stoken'])
        stoken = response.json()['stoken']
        return stoken


    def run(self):
        url = "https://zhidao.baidu.com/submit/ajax"
        image_content = self.upload_pic()
        self.content +=image_content
        data = {
            'cm': '100001',
            'title': self.title,  # 问题的标题，用户自定义
            'detail': self.content,  # 问题的内容，用户自定义
            'cid': '74',
            'isAuto': '0',
            'pid': '',
            'wealth': '0',
            'anoy': '0',
            'fix': '',
            'targetEncodeUid': '',
            'businessId': '',
            'fr': '',
            'entry': 'common_header',
            'querytype': '',
            'psquery': '',
            'rich': '1',
            'autofix': '0',
            'sms': '0',
            'pushType': '10',
            'tags': self.get_tag(),  # 这个是问题的分类标签，
            'newTags': self.get_tag(),  # 这个是问题的分类标签，可以通过后面的链接获取
            'utdata': '86,86,108,107,109,109,111,86,110,108,105,105,115,104,105,103,15806941373950',
            # 这个可以写死，应该是一个轨迹之类的东西吧，具体没仔细研究
            'stoken': self.get_stoken()
        }
        response = requests.post(url, data=data, headers=self.headers)
        print(response.text)
        return response.text



class BaiduAsk(object):
    def __init__(self,url,content,cookie):
        self.url = "https://zhidao.baidu.com/submit/ajax/"
        self.index_url = url
        self.content = content
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
            "Cookie":cookie,
        }

    def get_stoken(self):
        stoken_url = "https://zhidao.baidu.com/api/loginInfo"
        response = requests.get(stoken_url, headers=self.headers)
        print(response.json()['stoken'])
        stoken = response.json()['stoken']
        return stoken

    def ask(self):
        qid = re.findall(r"question/(.*)",self.url)[0]
        data ={
            'cm': '100009',
            'qid': qid,  # 问题的id，在网页源代码中获取
            'title': ';wap_question_replyed',
            'feedback': '0',
            'entry': 'uhome_homecenter_recommend',
            'co': '<p data-diagnose-id="6b7a97c70765886524311e2ce765f3a6">%s</p>'%self.content,
            'cite': '',
            'rich': '1',
            'edit': 'new',
            'utdata': '100,65,122,100,123,100,122,100,123,100,122,100,123,100,122,100,124,100,123,100,122,65,121,124,120,122,122,112,65,121,123,126,126,100,127,126,112,15819232033721',
            'stoken': self.get_stoken()
        }
        response = requests.post(self.url, headers=self.headers, data=data)
        print(response.text)
        return response.text





class JianShu(object):
    def __init__(self,title,content,cookie,image_url):
        self.image_url = image_url
        self.title = title
        self.content = content
        self.headers = {
            'accept': 'application/json',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            "referer": "https://www.jianshu.com/writer",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            "cookie": cookie,
            "content-type": "application/json; charset=UTF-8",
        }
    def upload_pic(self):
        if len(self.image_url) == 0:
            return ""
        else:
            result =""
            for image in self.image_url:
                token_url = "https://www.jianshu.com/upload_images/token.json"
                parmas = {
                    "filename": "123.png"
                }
                res = requests.get(token_url, params=parmas, headers=self.headers, verify=False)
                print(res.text)
                token = res.json()["token"]
                key = res.json()["key"]

                upload_url = "https://upload.qiniup.com/"
                res = requests.get(image,verify=False)
                data = {
                    "token": token, "key": key
                }
                files = {"file": ('test.png', res.content, 'image/png')}
                res2 = requests.post(upload_url, headers=self.headers, files=files, data=data, verify=False)
                print(res2.text)
                pic_url = res2.json()["url"]
                url_info = '<div class=\"image-package\"><img class=\"uploaded-img\" src=\"{}?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240\" width=\"auto\" height=\"auto\"><br><div class=\"image-caption\"></div></div>'.format(
                    pic_url)
                result +=url_info
            return result

    def get_articleId(self):
        url = "https://www.jianshu.com/author/notes"
        data = {
            "notebook_id": "31595225",  # 31595226是随笔，31595225是日记
            "title": self.title,  # 文章标题，自定义
            "at_bottom": "true"  # 是否在下方新建文章
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        result = response.json()
        article_id = result["id"]
        return article_id


    def run(self):
        image_info = self.upload_pic()
        article_id = self.get_articleId()
        article_url = "https://www.jianshu.com/author/notes/{}".format(article_id)
        print(article_url)
        data = {"id":article_id,
                "autosave_control": 1,
                "title": self.title,  # 文章标题，用户自定义
                "content": self.content+image_info  # 文章内容，用户自定义
                }
        response = requests.put(article_url, data=json.dumps(data), headers=self.headers)
        return response.text






class SinaAiWen(object):
    def __init__(self,title,content,cookie,image_url):
        self.image_url = image_url
        self.title = title
        self.content = content
        self.headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    "Cookie":cookie,
    "Referer":"https://iask.sina.com.cn/ask.html?q=",
    }

    def upload_pic(self):
        if len(self.image_url)==0:
            return ""
        else:
            picId = ""
            for url in self.image_url:
                res = requests.get(url)
                upload_url = "https://iask.sina.com.cn/question/ajax/fileupload"
                files = {"wenwoImage": ('test.png', res.content, 'form-data', {'Expires': '0'})}
                res2 = requests.post(upload_url, headers=self.headers, files=files)
                picId = res2.json()["id"]
            return picId

    def run(self):
        picId = self.upload_pic()
        url = "https://iask.sina.com.cn/question/askq"
        # url = "https://iask.sina.com.cn/question/askq"
        data = {
        'content': self.content,  #用户自定义
        'syn': 'Y',
        'picId':picId,#图片id
        'source': 'WEIWEN',
        }
        response = requests.post(url, data=data, headers=self.headers)
        print(response.text)
        return response.text


class SinaAsk(object):
    def __init__(self,content,cookie,url):
        self.content = content
        self.index_url = url
        self.url = "https://iask.sina.com.cn/answer/sanswer"
        self.headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    "Cookie":cookie,
    "Referer":"https://iask.sina.com.cn/ask.html?q=",
    }
    def ask(self):
        questionId = re.findall(r"b/(.*?)\.html",self.index_url,re.DOTALL)[0]
        data = {
            "content": self.content,
            "questionId": questionId,
            "anon": "Y", #分享到微博'syn': 'Y',   匿名："anon": "Y"
            "pageType":"question_detail", #表示问题详情页
        }
        response = requests.post(self.url, headers=self.headers, data=data)
        print(response.text)
        return response.text




class WuKong(object):
    def __init__(self,title,content,cookie,image_url):
        self.image_url = image_url
        self.title = title
        self.content = content
        self.headers =  {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            "cookie":cookie,
            "referer": "https://www.wukong.com/"
        }
    def upload_pic(self):
        if len(self.image_url) == 0:
            return -1
        else:
            result = []
            for image in self.image_url:
                upload_url = "https://www.wukong.com/wenda/web/upload/photo/"
                res = requests.get(image,verify=False)
                files = {"upfile": ('test.png', res.content, 'image/png', {'Expires': '0'})}
                res2 = requests.post(upload_url, headers=self.headers, files=files, verify=False)
                print(res2.text)
                final_url= res2.json()["original"]
                result.append(final_url)
            return result

    def run(self):
        result = self.upload_pic()
        if result == -1:
            data = {
                "title": self.title,
                "content": self.content
            }
        else:
            data = [("title", self.title), ("content", self.content)]
            for i in result:
                a = ("pic_list[]", i)
                data.append(a)

        url = "https://www.wukong.com/wenda/web/commit/postquestion/"
        response = requests.post(url,data=data,headers=self.headers)
        print(response.text)



class WuKongAsk(object):
    def __init__(self,content,cookie,url):
        self.index_url = url
        self.content = content
        self.url =  "https://www.wukong.com/wenda/web/commit/postanswer/?origin_source=answer_requesting_recommend&source=question_click_write_answer"
        self.headers =  {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            "cookie":cookie,
            "referer": "https://www.wukong.com/"
        }

    def ask(self):
        qid = re.findall(r"question/(.*?)/",self.index_url,re.DOTALL)[0]
        data = {
        "qid": qid,
        "content": self.content,
        }
        response = requests.post(self.url, data=data, headers=self.headers)
        print(response.text)
        return response.text


class SouGou(object):
    def __init__(self,title,content,cookie,image_url):
        self.image_url = image_url
        self.title = title
        self.content = content
        self.traceId = ""
        self.userId = ""
        self.orig = ""
        self.uid = ""
        self.index_url = "https://wenwen.sogou.com/question/ask"
        self.tag_url = "https://wenwen.sogou.com/wapi/ms/title-tags"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
            "Cookie": cookie,
            "Referer": "https://wenwen.sogou.com/question/ask",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "content-type": "application/json; charset=UTF-8"
        }


    def get_userInfo(self):
        response = requests.get(self.index_url, headers=self.headers)
        userId = re.findall(r"userId: \'(.*?)\'", response.text, re.DOTALL)[0]
        uid = re.findall(r"uid: \'(.*?)\'", response.text, re.DOTALL)[0]
        orig = re.findall(r"orig: (.*?),", response.text, re.DOTALL)[0]
        traceId = re.findall(r"traceId: \'(.*?)\'", response.text, re.DOTALL)[0]
        return userId,uid,orig,traceId

    def get_tag(self):
        self.userId,self.uid,self.orig,self.traceId = self.get_userInfo()
        tag_data = {
            'title': '北京有什么好吃的',
            '_traceId': '%s:3'%self.traceId
        }
        response = requests.get(self.tag_url, params=tag_data, headers=self.headers, verify=False)
        print(response.text)
        list1 = eval(response.text)
        tags=[]
        for i in list1:
            tags.append(i["id"])
        return tags
    def upload_pic(self):
        if len(self.image_url)== 0:
            return []
        else:
            result = []
            for i in self.image_url:
                upload_url = "https://wenwen.sogou.com/submit/qun/upload-pic"
                res = requests.get("https://yz-xiaoke-imgserver.oss-cn-shanghai.aliyuncs.com/edu/python/background/1.jpg")
                files = {"pic": ('test.png', res.content, 'image/png', {'Expires': '0'})}
                res2 = requests.post(upload_url, headers=self.headers, files=files, verify=False)
                print(res2.text)
                fname = res2.json()["fname"]
                fname = "//pic.wenwen.soso.com/p/"+fname
                result.append(fname)
            return result
    def run(self):
        tags = self.get_tag()
        images = self.upload_pic()
        url = "https://wenwen.sogou.com/submit/ms/ask?_traceId={}:6".format(self.traceId)
        data = {"userId":self.userId,
                "clbUid":self.uid,
                "orig":int(self.orig),
                "mobileSmsFlag":"false",
                "content":base64.b64encode((self.content).encode()).decode(),
                 "title":base64.b64encode((self.title).encode()).decode(),
                 "tags":tags,
                 "images":images,
                 "score":"0",
                 "anonymous":"false",
                 "seekHelpUid":"null"
                }
        response = requests.post(url,data=json.dumps(data),headers=self.headers)
        print(response.text)
        return response.text

class SouGouAsk(object):
    def __init__(self,content,cookie,url):
        self.info_url = "https://wenwen.sogou.com/question/ask"
        self.index_url = url
        self.content = content
        self.headers  = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
            "Cookie": cookie,
            "Referer": "https://wenwen.sogou.com/question/ask",
            "accept": "application/json, text/javascript, */*; q=0.01",
            "accept-encoding": "gzip, deflate, br",
            "content-type": "application/json; charset=UTF-8"
        }


    def get_userInfo(self):
        response = requests.get(self.info_url, headers=self.headers)
        userId = re.findall(r"userId: \'(.*?)\'", response.text, re.DOTALL)[0]
        uid = re.findall(r"uid: \'(.*?)\'", response.text, re.DOTALL)[0]
        orig = re.findall(r"orig: (.*?),", response.text, re.DOTALL)[0]
        traceId = re.findall(r"traceId: \'(.*?)\'", response.text, re.DOTALL)[0]
        return userId,uid,orig,traceId


    def ask(self):
        userId,uid,orig,traceId = self.get_userInfo()
        questionId = re.findall(r"question/q(.*?)\.",self.index_url)[0]
        url = "https://wenwen.sogou.com/submit/ms/answer?_traceId={}:14".format(traceId)
        data = {"userId": userId,
                "clbUid": uid,
                "orig": orig,
                "content": base64.b64encode((self.content).encode()).decode(),
                "questionId": questionId,  # 这个可以在传送过来的url中直接获取
                "anonymous": "false"
                }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        print(response.text)
        return response.text




class CTO51(object):
    def __init__(self,title,content,cookie,tag,image_url):
        self.tag=tag
        self.image_url = image_url
        self.title = title
        self.content = content
        self.publish_url = "https://blog.51cto.com/blogger/publish"
        self.did_url = "https://blog.51cto.com/blogger/draft"
        self.headers = {
            "Host": "blog.51cto.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": cookie
        }

    def upload_pic(self):
        if len(self.image_url)==0:
            return ""
        else:
            result = ""
            for image in self.image_url:
                upload_url = "https://upload.51cto.com/index.php?c=upload&m=upimg&orig=b"
                res = requests.get(image,verify=False)
                data = {
                    "sign": "BmCay7vag7CdjmNadmVS2mCMZ5QS0UQW0aCwW7hcJ7hMW",
                    "fileid": "uploadm-2408198449",
                    "chunkSize": "5242880",
                    "id": "WU_FILE_0",
                    "name": "test.png",
                }
                files = {"file": ('test.png', res.content, 'image/png')}
                res2 = requests.post(upload_url, headers=self.headers, files=files, data=data, verify=False)
                pic_url = res2.json()["data"]
                print(res2.text)
                image_info = '![](https://s1.51cto.com/{}?x-oss-process=image/watermark,size_16,text_QDUxQ1RP5Y2a5a6i,color_FFFFFF,t_100,g_se,x_10,y_10,shadow_90,type_ZmFuZ3poZW5naGVpdGk=)'.format(
                    pic_url)
                result +=image_info
            return result

    def get_csrf(self):
        response = requests.get(self.publish_url, headers=self.headers)
        html = etree.HTML(response.text)
        csrf = html.xpath("//meta[@name='csrf-token']/@content")[0]
        new_cookies = response.cookies
        new_cookies = self.headers["Cookie"] + ";" + "_identity=%s" % new_cookies["_identity"]
        self.headers["Cookie"] = new_cookies
        return csrf


    def get_did(self):
        did_data = {
            "_csrf": self.get_csrf(),
            "abstract": "",
            "blog_id": "",
            "blog_type": "",
            "cate_id": "",
            "content": self.content,
            "copy_code": "1",
            "custom_id": "",
            "did": "",
            "is_hide": "0",
            "is_old": "0",
            "pid": "",
            "tag": "",
            "title": self.title
        }
        response = requests.post(self.did_url, headers=self.headers, data=did_data)
        did = response.json()["data"]["did"]
        return did


    def run(self):
        tagInfo = ",".join(self.tag)
        imageInfo = self.upload_pic()
        publish_data = {
            "blog_type": "1",
            "title": self.title,
            "copy_code": "1",
            "content": self.content+imageInfo,
            "pid": "27",
            "cate_id": "44",
            "custom_id": "",
            "tag": tagInfo,
            "abstract": "",
            "is_hide": "0",
            "did": self.get_did(),
            "blog_id": "",
            "is_old": "0",
            "_csrf": self.get_csrf()
        }
        response = requests.post(self.publish_url, headers=self.headers, data=publish_data)
        print(response.text)
        return response.text





class BoKeYuan(object):
    def __init__(self,title,content,cookie,password,tag,image_url):
        self.image_url = image_url
        self.url = "https://i-beta.cnblogs.com/api/posts"
        self.title = title
        self.password = password
        self.tag = tag
        self.content = content
        self.upload_headers = {
                        "Host": "upload.cnblogs.com",
                        "Cookie": cookie,
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
                        "X-File-Name": "10.png",
                        "Origin": "https://i-beta.cnblogs.com"
                }
        self.upload_url = "https://upload.cnblogs.com/imageuploader/processupload?host=common.cnblogs.com&qqfile=10.png"
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Cookie": cookie,
            "Referer": "https://i-beta.cnblogs.com/articles/edit",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            #"X-BLOG-ID": "578564",
            "Host": "i-beta.cnblogs.com",
            "Origin": "https://i-beta.cnblogs.com"
        }

    def upload_pic(self):
        if len(self.image_url)==0:
            return ""
        else:
            result = ""
            for image in self.image_url:
                res = requests.get(image,verify=False)
                files = {"file": ('test.png', res.content, 'image/png')}
                res2 = requests.post(self.upload_url, headers=self.upload_headers, files=files, verify=False)
                pic_url = res2.json()["message"]
                imageInfo = '<img src=\"{}\" alt=\"\" />'.format(pic_url)
                result += imageInfo
            return result
    def get_blogId(self):
        url = "https://i-beta.cnblogs.com/api/user"
        response = requests.get(url,headers=self.headers)
        blogId = response.json()["blogId"]
        self.headers["X-BLOG-ID"] = blogId


    def run(self):
        imageInfo = self.upload_pic()
        publishTime = datetime.datetime.utcnow().isoformat()
        #password如果没有，则为null
        data = '{"id":null,"postType":2,"title":%s,"url":null,"postBody":%s,"categoryIds":null,"inSiteCandidate":false,"inSiteHome":false,"siteCategoryId":null,"blogTeamIds":null,"isPublished":true,"displayOnHomePage":false,"isAllowComments":true,"includeInMainSyndication":true,"isPinned":false,"isOnlyForRegisterUser":false,"isUpdateDateAdded":false,"entryName":null,"description":null,"tags":%s,"password":%s,"datePublished":%s,"isMarkdown":false,"isDraft":true,"autoDesc":null,"changePostType":false,"blogId":0,"author":null,"removeScript":false,"ip":null,"changeCreatedTime":false,"canChangeCreatedTime":false}'%(self.title,self.content+imageInfo,self.tag,self.password,publishTime)
        response = requests.post(self.url, headers=self.headers, data=data.encode(), verify=False)
        print(response.text)
        return response.text





class NiuKe(object):
    def __init__(self,title,content,cookie,contentType,blogType,tag,isPrivate,image_url):
        self.url = "https://blog.nowcoder.net/new?token="
        self.title = title
        self.image_url = image_url
        self.content = content
        self.contentType = contentType
        self.blogType = blogType
        self.tag = tag
        self.isPrivate = isPrivate
        self.headers = {
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie": cookie,
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"
                }
        self.upload_headers = {
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Host": "blog.nowcoder.net",
                "cookie": cookie,
                "referer": "https://blog.nowcoder.net/detail/0",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"
                }
        self.upload_url = "https://blog.nowcoder.net/uploadImage?type=1&watermark=true"

    def upload_pic(self):
        if len(self.image_url) == 0:
            return ""
        else:
            result = ""
            for image in self.image_url:
                res = requests.get(image,verify=False)
                files = {"file": ('test.png', res.content, 'image/png')}
                res2 = requests.post(self.upload_url, headers=self.upload_headers, files=files, verify=False)
                pic_url = res2.json()["url"]
                imageInfo = '<img src={} alt="图片说明" title="图片标题"><br>'.format(pic_url)
                result +=imageInfo
            return result

    def run(self):
        imageInfo = self.upload_pic()
        tags = ",".join(self.tag)
        mdContent = re.findall(r"<p>(.*?)</p>",self.content,re.DOTALL)[0]
        data = {
            "title": self.title,
            "content": self.content+imageInfo,
            "mdContent": mdContent+imageInfo,
            "contentType": self.contentType,  #1为markdown编辑器，0为富文本编辑器
            "blogType": self.blogType,  #博客类型 ，为归档
            "tags":tags,
            "isPrivate": self.isPrivate,  #是否为私密文章
            "entityId": "0",
        }
        response = requests.post(self.url, headers=self.headers, data=data)
        print(response.text)
        return response.text





class WangYiLofter(object):
    def __init__(self,title,content,cookie,tag,image_url):
        self.image_url = image_url
        self.title = title
        self.content = content
        self.tag = tag
        self.cookie = cookie
        self.url = "http://www.lofter.com/blog/tazhendehenxiangnin/new/text/"
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": cookie,
            "Referer": "http://www.lofter.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"
        }

    def upload_pic(self):
        headers = {
            "cookie": self.cookie,
            "Referer": "http://www.lofter.com/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36"
        }
        if len(self.image_url) == 0:
            return ""
        else:
            result = ""
            for image in self.image_url:
                url = "http://www.lofter.com/dwr/call/plaincall/ImageBean.genTokens.dwr"
                data = """callCount=1
                scriptSessionId=${scriptSessionId}187
                httpSessionId=
                c0-scriptName=ImageBean
                c0-methodName=genTokens
                c0-id=0
                c0-param0=string:png
                c0-param1=string:
                c0-param2=string:
                c0-param3=string:
                c0-param4=string:1
                batchId=475873"""
                res = requests.post(url, headers=headers, data=data)

                url_name = re.findall(r"bucketName=\"(.*?)\";", res.text)[0]

                objectInfo = re.findall(r"objectName=\"(.*?)\";", res.text)[0]

                uploadToken = re.findall(r"uploadToken=\"(.*?)\";", res.text)[0]

                # 上传图片
                upload_url = "https://nos.netease.com/{}".format(url_name)
                res = requests.get("https://yz-xiaoke-imgserver.oss-cn-shanghai.aliyuncs.com/edu/python/background/1.jpg",
                                   verify=False)
                data = {
                    "Object": objectInfo, "x-nos-token": uploadToken,
                }
                files = {"file": ('test.png', res.content, 'image/png')}
                res2 = requests.post(upload_url, headers=headers, files=files, data=data, verify=False)
                print(res2.text)
                objectName = res2.json()["objectName"]
                image_tag = '<img src="http://{}.nosdn.127.net/{}?=imageView&amp;thumbnail=500x0&amp;quality=96&amp;stripmeta=0&amp;type=jpg%7Cwatermark&amp;type=2" border="0" hspace="0" vspace="0" smallsrc="http://{}.nosdn.127.net/{}?=imageView&amp;thumbnail=164x164&amp;quality=96&amp;stripmeta=0&amp;type=jpg%7Cwatermark&amp;type=2" /><br />'.format(
                    url_name, objectName, url_name, objectName)
                result +=image_tag
            return result



    def get_userInfo(self):
        url = "http://www.lofter.com/"
        response = requests.get(url,headers=self.headers)
        print(response.text)
        blogId = re.findall(r"blogId:(.*?),", response.text, re.DOTALL)[0]
        blogName = re.findall(r"blogName:(.*?),", response.text, re.DOTALL)[0]
        return blogId,blogName


    def run(self):
        imageInfo = self.upload_pic()
        tags = ",".join(self.tag)
        blogId, blogName = self.get_userInfo()
        data = {
            "blogId": blogId,
            "blogName": blogName,
            "content": self.content+imageInfo,
            "allowView": "0",
            "isPublished": "true",
            "cctype": "0",
            "tag":tags,
            "collectionId": "0",
            "syncSites":"",
            "forbidShare": "0",
            "allowReward": "0",
            "title": self.title,
            "photoInfo": "[]",
            "valCode": "",
        }
        response = requests.post(self.url, headers=self.headers, data=data)
        print(response.text)
        return response.text




class Csdn(object):
    def __init__(self,title,content,cookie,tag,readType,type,original_link,image_url):
        self.image_url = image_url
        self.title = title
        self.content = content
        self.tag = tag
        self.readType =readType
        self.original_link = original_link
        self.type = type
        self.url = "https://blog-console-api.csdn.net/v1/mdeditor/saveArticle"
        self.upload_url = "https://blog-console-api.csdn.net/v1/upload/img?shuiyin=2"
        self.headers = {
                "Host": "blog-console-api.csdn.net",
                "Connection": "keep-alive",
                "Content-Length": "242",
                "Origin": "https://editor.csdn.net",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
                "Content-Type": "application/json",
                "Accept": "*/*",
                "Referer": "https://editor.csdn.net/md",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Cookie": cookie,
                }
        self.upload_headers = {
            "Host": "blog-console-api.csdn.net",
            "Origin": "https://editor.csdn.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://editor.csdn.net/md",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "cookie": cookie
            }
    def upload_pic(self):
        if len(self.image_url)==0:
            return ""
        else:
            result = ""
            for image in self.image_url:
                res = requests.get("https://yz-xiaoke-imgserver.oss-cn-shanghai.aliyuncs.com/edu/python/background/1.jpg",
                                   verify=False)
                files = {"file": ('test.png', res.content, 'image/png')}
                res2 = requests.post(self.upload_url, headers=self.upload_headers, files=files, verify=False)
                pic_url = res2.json()["data"]["url"]
                imageInfo = '![在这里插入图片描述]({})'.format(pic_url)
                result +=imageInfo
            return result

    def run(self):
        imageInfo = self.upload_pic()
        tags = ",".join(self.tag)
        markdowncontent = re.findall(r"<p>(.*?)</p>",self.content,re.DOTALL)[0]+"\n"
        data = {"title":self.title, #标题，用户自定义
        "markdowncontent":markdowncontent+imageInfo,
        "content":self.content+imageInfo, # 内容，用户自定义
        "readType":self.readType, #发布形式 公开：public；私密：private；粉丝可见：needfans；vip可见：needvip
        "tags":tags,  #文章分类标签
        "status":0,
        "categories":"",
        "type":self.type,  #文章类型 原创：original；转载：repost；翻译：translated
        "original_link":self.original_link,   #原文链接
        "authorized_status": "false",
        "not_auto_saved":"1",
        "source":"pc_mdeditor"
        }
        response =requests.post(self.url,headers=self.headers,data = json.dumps(data))
        print(response.text)
        return response.text



