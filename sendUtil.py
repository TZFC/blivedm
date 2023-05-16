import time

import browser_cookie3
import requests.utils

# Assumed Edge browser with bilibili logged in
cookies = requests.utils.dict_from_cookiejar(browser_cookie3.edge(domain_name='.bilibili.com'))
SESSDATA = cookies["SESSDATA"]
CSRF = cookies["bili_jct"]
UID = cookies["DedeUserID"]

COOKIE = '''DedeUserID={};SESSDATA={}; bili_jct={};'''.format(UID, SESSDATA, CSRF)


def updateCredentials():
    global COOKIE
    cookies = requests.utils.dict_from_cookiejar(browser_cookie3.edge(domain_name='.bilibili.com'))
    SESSDATA = cookies["SESSDATA"]
    CSRF = cookies["bili_jct"]
    UID = cookies["DedeUserID"]
    COOKIE = '''DedeUserID={};SESSDATA={}; bili_jct={};'''.format(UID, SESSDATA, CSRF)


def sendText(text, room, cookie=COOKIE, csrf=CSRF):
    url = 'https://api.live.bilibili.com/msg/send'
    data = {
        'color': '14893055',  # 颜色
        'fontsize': '25',  # 字体大小
        'mode': '1',  # 模式
        'msg': text,  # 消息内容
        'rnd': str(int(time.time())),  # 这个是时间戳
        'roomid': room,  # 这个是直播房间的id号
        'bubble': '0',
        'csrf_token': csrf,
        'csrf': csrf,
    }
    with requests.Session() as session:
        session.cookies.set('Cookie', cookie)
        response = session.post(url, data=data)
    return response


def send_emoji(emoji, room, mode=4, bubble=5, dm_type=1, cookie=COOKIE, csrf=CSRF):
    url = 'https://api.live.bilibili.com/msg/send'
    data = {
        'color': '16772431',  # 颜色
        'fontsize': '25',  # 字体大小
        'mode': mode,  # 模式
        'msg': emoji,  # 消息内容
        'rnd': str(int(time.time())),  # 这个是时间戳
        'roomid': room,  # 这个是直播房间的id号
        'bubble': bubble,
        'dm_type': dm_type,
        'csrf_token': csrf,
        'csrf': csrf,
    }
    with requests.Session() as session:
        session.cookies.set('Cookie', cookie)
        response = session.post(url, data=data)
    return response
