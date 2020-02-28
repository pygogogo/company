#@Time    :2020/2/24 10:52
#@Author  :wuxinghui
#@FileName: scheduler.py

import requests
import re
import json
from queue import Queue
import threading
import time
from multiprocessing import Process
from main import *

class Produce(Process):
    def __init__(self,task_queue,*args,**kwargs):
        super(Process, self).__init__(*args, **kwargs)
        self.task_queue = task_queue
        self.task_url = "https://api-task.yixiaoer.cn/api/seotask/GetTaskData"
        self.task_data = {
        "deviceNo": "dd7bfac8-c317-44ab-a6c7-6d0dc7694bd0"
        }
        self.task_headers = {
        "content-Type":"application/json"
        }


    def get_task(self):
        response = requests.post(self.task_url, data=json.dumps(self.task_data), headers=self.task_headers)
        print(response.text)
        message = response.json()["Message"]
        #如果没有任务则返回-1，有则返回数据
        if message == "没有任务了":
            return -1
        else:
            user_data = response.json()["Data"]["PublishTaskDetails"]
            return user_data

    def run(self):
        while True:
            user_data = self.get_task()
            #如果没有任务，就休眠10秒钟
            if user_data==-1:
                time.sleep(10)
                continue
            else:
                self.task_queue.put(user_data)

class Comsumer(Process):
    def __init__(self,task_queue ,*args, **kwargs):
        super(Comsumer, self).__init__(*args, **kwargs)
        self.task_queue = task_queue

    def run(self):
        while True:
            user_data = self.task_queue.get()
            if user_data["appid"] == 1:
                pass
            elif user_data["appid"] ==2:
                BaiDuZhiDao(user_data["title"],user_data["content"],user_data["cookie"],user_data("image_url")).run()
            elif user_data["appid"] ==3:
                SouGou(user_data["title"],user_data["content"],user_data["cookie"],user_data["image_url"]).run()
            elif user_data["appid"] ==4:
                pass
            elif user_data["appid"] ==5:
                WuKong(user_data["title"],user_data["content"],user_data["cookie"],user_data["image_url"]).run()
            elif user_data["appid"] ==6:
                SinaAiWen(user_data["title"],user_data["content"],user_data["cookie"],user_data["image_url"]).run()
            elif user_data["appid"] ==7:
                pass
            elif user_data["appid"] ==8:
               WangYiLofter(user_data["title"], user_data["content"], user_data["cookie"],user_data["tag"],user_data["image_url"]).run()
            elif user_data["appid"] ==9:
                pass
            elif user_data["appid"] ==10:
                CTO51(user_data["title"], user_data["content"], user_data["cookie"],user_data["tag"],user_data["image_url"]).run()
            elif user_data["appid"] ==11:
                pass
            elif user_data["appid"] ==12:
               Csdn(user_data["title"], user_data["content"], user_data["cookie"],user_data["tag"], user_data["readType"], user_data["type"],user_data["original_link"],user_data["image_url"]).run()
            elif user_data["appid"] ==13:
               NiuKe(user_data["title"], user_data["content"], user_data["cookie"],user_data["contentType"],user_data["blogType"],user_data["tag"],user_data["isPrivate"],user_data["image_url"]).run()
            elif user_data["appid"] ==14:
                JianShu(user_data["title"], user_data["content"], user_data["cookie"],user_data["image_url"]).run()
            elif user_data["appid"] ==15:
                pass
            elif user_data["appid"] ==16:
                pass
            elif user_data["appid"] ==17:
                BoKeYuan(user_data["title"], user_data["content"], user_data["cookie"],user_data["password"], user_data["tag"],user_data["image_url"]).run()
            elif user_data["appid"] ==18:
                pass
            elif user_data["appid"] ==19:
                pass
            elif user_data["appid"] ==20:
                pass
            elif user_data["appid"] ==21:
                pass
            elif user_data["appid"] ==22:
                pass
            elif user_data["appid"] ==23:
                pass





def main():
    task_queue = Queue(100)
    for i in range(5):
        t = Produce(task_queue)
        t.start()
    for i in range(5):
        t = Comsumer(task_queue)
        t.start()




