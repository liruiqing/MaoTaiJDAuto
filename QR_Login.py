#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# Author:曹敬贺

import requests
import json
import os
import pickle
import re
import random
import time
# from log import logger
from timer import Timer
from bs4 import BeautifulSoup
from util import *
from JDException import JDException

class JDLogin(object):
    def __init__(self):
        self.session = requests.session()
        # 以后加上随机UA
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        self.headers = {'User-Agent': self.user_agent}
        self.nick_name = ''
        self.isLogin = self.JD_LoadCookie();

    def JD_RQ_login(self):
        if self.isLogin:
            return True
        self.get_login_page();
        if not self.get_QRcode():
            raise JDException("获取失败");

        ticket = None
        retry_times = 85
        for _ in range(retry_times):
            ticket = self.JD_GetQRcodeScanResult()
            if ticket:
                break
            time.sleep(2)
        else:
            raise JDException('二维码过期，请重新获取扫描')

        if not self.JD_Validate_QRcodeResult(ticket):
            raise  JDException("二维码信息校验失败")
        print("二维码登录成功")
        self.nick_name = self.JD_GetUserInfo();
        self.JD_SaveCookie();


    def JD_GetQRcodeScanResult(self):
        url = 'https://qr.m.jd.com/check'
        payload = {
            'appid': '133',
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            'token': self.session.cookies.get('wlfstk_smdl'),
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://passport.jd.com/new/login.aspx',
        }
        resp = self.session.get(url=url, headers=headers, params=payload)

        if not self.response_status(resp):
            print('获取二维码扫描结果异常')
            return False

        resp_json = parse_json(resp.text)
        if resp_json['code'] != 200:
            print('Code: %s, Message: %s', resp_json['code'], resp_json['msg'])
            return None
        else:
            print('已完成手机客户端确认')
            return resp_json['ticket']

    def JD_Validate_QRcodeResult(self,ticket):
        url = 'https://passport.jd.com/uc/qrCodeTicketValidation'
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://passport.jd.com/uc/login?ltype=logout',
        }
        resp = self.session.get(url=url, headers=headers, params={'t': ticket})

        if not self.response_status(resp):
            return False

        resp_json = json.loads(resp.text)
        if resp_json['returnCode'] == 0:
            return True
        else:
            print(resp_json)
            return False


# 获取登录页面
    def get_login_page(self):
        url = "https://passport.jd.com/new/login.aspx"
        page = self.session.get(url, headers=self.headers)
        print("获取登录页面成功")
        return page

    def get_QRcode(self):
        url = 'https://qr.m.jd.com/show'
        payload = {
            'appid': 133,
            'size': 147,
            't': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://passport.jd.com/new/login.aspx',
        }
        resp = self.session.get(url=url, headers=headers, params=payload)
        print(resp);
        if not self.response_status(resp):
            print('获取二维码失败')
            return False
        QRCode_file = 'QRcode.png'
        with open(QRCode_file, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                f.write(chunk)
#        logger.info('二维码获取成功，请打开京东APP扫描')
        open_image(QRCode_file)
        return True

    def JD_GetUserInfo(self):
        """获取用户信息
        :return: 用户名
        """
        url = 'https://passport.jd.com/user/petName/getUserInfoForMiniJd.action'
        payload = {
            'callback': 'jQuery{}'.format(random.randint(1000000, 9999999)),
            '_': str(int(time.time() * 1000)),
        }
        headers = {
            'User-Agent': self.user_agent,
            'Referer': 'https://order.jd.com/center/list.action',
        }
        try:
            resp = self.session.get(url=url, params=payload, headers=headers)
            resp_json = parse_json(resp.text)
            # many user info are included in response, now return nick name in it
            # jQuery2381773({"imgUrl":"//storage.360buyimg.com/i.imageUpload/xxx.jpg","lastLoginTime":"","nickName":"xxx","plusStatus":"0","realName":"xxx","userLevel":x,"userScoreVO":{"accountScore":xx,"activityScore":xx,"consumptionScore":xxxxx,"default":false,"financeScore":xxx,"pin":"xxx","riskScore":x,"totalScore":xxxxx}})
            return resp_json.get('nickName') or 'jd'
        except Exception:
            return 'jd'

    def JD_SaveCookie(self):
        cookies_file = './cookies/{0}.cookies'.format(self.nick_name)
        directory = os.path.dirname(cookies_file)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(cookies_file, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def JD_ValidateCookie(self):
        """验证cookies是否有效（是否登陆）
                通过访问用户订单列表页进行判断：若未登录，将会重定向到登陆页面。
                :return: cookies是否有效 True/False
                """
        url = 'https://order.jd.com/center/list.action'
        payload = {
            'rid': str(int(time.time() * 1000)),
        }
        try:
            resp = self.session.get(url=url, params=payload, allow_redirects=False)
            if resp.status_code == requests.codes.OK:
                return True
        except Exception as e:
            print(e)
        self.session = requests.session()
        return False

    def JD_LoadCookie(self):
        cookies_file = ''
        for name in os.listdir('./cookies'):
            if name.endswith('.cookies'):
                cookies_file = './cookies/{0}'.format(name)
                break
        with open(cookies_file, 'rb') as f:
            local_cookies = pickle.load(f)
        self.session.cookies.update(local_cookies)
        print("是否登录？ %d" % self.JD_ValidateCookie())
        return self.JD_ValidateCookie();


    def response_status(self,resp):
        if resp.status_code != requests.codes.OK:
            print('Status: %u, Url: %s' % (resp.status_code, resp.url))
            return False
        return True
