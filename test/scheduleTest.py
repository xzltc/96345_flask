# -*- coding = utf-8 -*-
# @Time :2020/7/8 11:34 上午
# @Author: XZL
# @File : scheduleTest.py
# @Software: PyCharm
# !/usr/bin/env python2
# -*- coding: utf-8 -*-

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
import check_update
import logging
import datetime

db_path = 'sqlite:///96345.db?check_same_thread=False'
param = {"code": "server_content"}
base_url = "http://www.sx96345.com"
header = "/centre/life_service/"  # url后面跟着的一点


def sensor():
    """ Function for test purposes. """
    print("Scheduler is alive!", datetime.datetime.now())


def sensor2():
    print("alive 2 !")

# def update_feedback():
#     check_update.every_day_update_feedback(param, base_url, header, )


sched = BackgroundScheduler(daemon=True, timezone='UTC')
# sched.add_job(sensor, 'interval', seconds=2)
# sched.add_job(sensor, 'cron', day_of_week='0-6', hour='13-16')
sched.add_job(sensor, 'cron', day_of_week='0-6', second='*/5', id='sensor')
sched.add_job(sensor2, 'cron', day_of_week='0-6', second='*/10', id='sensor2')

# sched.add_job(sensor, 'cron', day_of_week='0-6', hour='8-23', second='10,20,30,40,50')


sched.start()

# # 每天一点运行插入新输入
# sched.add_job(sensor, 'cron', day_of_week='0-6', hour=1, minute=0, second=0)
# # 每天8点-12点 每两个小时update数据
# sched.add_job(sensor, 'cron', day_of_week='0-6', hour='0-23', minute='*/120')
app = Flask(__name__)


@app.route("/")
def home():
    """ Function for test purposes. """
    return "Welcome Home :) !"


if __name__ == "__main__":
    app.run()
