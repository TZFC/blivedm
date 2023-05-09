import json

with open('ludengConfig.json', 'r') as config:
    ludengConfig = json.loads(config.read())

userConfigs = {}
streaminfos = {}
for userConfig in ludengConfig["configs"]:
    with open(userConfig, 'r', encoding="utf-8") as config:
        thisConfig = json.loads(config.read())
        userConfigs[thisConfig["ROOM_ID"]] = thisConfig
        streaminfos[thisConfig["ROOM_ID"]] = {'live_status': 0, 'live_time': '0', 'keyframe': '0', 'title': '0',
                                              'danmu_file_name': '0'}

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import smtplib


def send_start_email(config, streamInfo):
    # send start notification with after-live gift summary to subscribers
    msg = MIMEMultipart()
    msg["From"] = config["FROM_ADDRESS"]
    msg["To"] = ",".join(config["NOTIFY_USER"].values())
    msg["Subject"] = "{}开始直播{}".format(config['ROOM_NAME'], streamInfo['title'])
    body = "{}开始直播{}".format(config['ROOM_NAME'], streamInfo['title'])
    msg.attach(MIMEText(body, "plain"))
    email_session = smtplib.SMTP("smtp.gmail.com", 587)
    email_session.starttls()
    email_session.login(config["FROM_ADDRESS"], config["PASSWORD"])
    text = msg.as_string()
    email_session.sendmail(config["FROM_ADDRESS"], config["NOTIFY_USER"].values(), text)
    email_session.quit()


def send_ludeng(config, streamInfo):
    msg = MIMEMultipart()
    msg["From"] = config["FROM_ADDRESS"]
    msg["To"] = ",".join(config["LUDENG_USER"].values())
    msg["Subject"] = "{}于{}".format(config['ROOM_NAME'], streamInfo["danmu_file_name"][:-4])
    body, attachFile = getDeng(config, streamInfo)
    msg.attach(MIMEText(body, "plain"))
    p = MIMEBase("application", "octet-stream")
    with open(attachFile, "rb") as attachment:
        p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "attachment", filename=attachFile)
    msg.attach(p)  # 邮件附件是 filename
    email_session = smtplib.SMTP("smtp.gmail.com", 587)
    email_session.starttls()
    email_session.login(config["FROM_ADDRESS"], config["PASSWORD"])
    text = msg.as_string()
    email_session.sendmail(config["FROM_ADDRESS"], config["LUDENG_USER"].values(), text)
    email_session.quit()


import requests


async def updateLiveStatus():  # 获取直播间开播状态信息
    url = "http://api.live.bilibili.com/room/v1/Room/get_info?room_id="
    for ROOM_ID in streaminfos.keys():
        res = requests.get(url + ROOM_ID).json()
        streaminfos[ROOM_ID]['title'] = res["data"]["title"]
        streaminfos[ROOM_ID]['live_time'] = res["data"]["live_time"]
        streaminfos[ROOM_ID]['keyframe'] = res["data"]["keyframe"]
        if streaminfos[ROOM_ID]['live_status'] == 0 and res["data"]["live_status"] == 1:  # 刚刚开播
            send_start_email(userConfigs[ROOM_ID], streaminfos[ROOM_ID])
            streaminfos[ROOM_ID]['danmu_file_name'] = "{}{}路灯.txt".format(
                streaminfos[ROOM_ID]['live_time'].replace(" ", "-").replace(":", "-"), streaminfos[ROOM_ID]['title'])
        elif streaminfos[ROOM_ID]['live_status'] == 1 and (
                res["data"]["live_status"] == 0 or res["data"]["live_status"] == 2):  # 刚刚下播
            send_ludeng(userConfigs[ROOM_ID], streaminfos[ROOM_ID])
        streaminfos[ROOM_ID]['live_status'] = res["data"]["live_status"]  # 0: 未开播 1: 直播中 2: 轮播中

async def updateLiveStatus_loop():
    while True:
        await asyncio.sleep(1)
        await updateLiveStatus()


def getDeng(config, streamInfo):
    # TODO: use config to process Danmu
    with open(streamInfo["danmu_file_name"], "r") as luDeng:
        luDengText = luDeng.read()
    return luDengText


import asyncio
import blivedm
import aiofiles


async def run_multi_clients():
    clients = [blivedm.BLiveClient(room_id) for room_id in userConfigs.keys()]
    handler = MyHandler()
    for client in clients:
        client.add_handler(handler)
        client.start()

    try:
        await asyncio.gather(*(
            client.join() for client in clients
        ))
    finally:
        await asyncio.gather(*(
            client.stop_and_close() for client in clients
        ))


async def write_to_file(text, filename):
    async with aiofiles.open(filename, mode='a', encoding="utf-8") as f:
        await f.write(text+"\n")

def cleanMessage(message):
    return f"{message.timestamp};{message.uname};{message.uid};{message.dm_type};{message.medal_room_id};{message.medal_level};{message.msg}"

class MyHandler(blivedm.BaseHandler):
    # # 演示如何添加自定义回调
    # _CMD_CALLBACK_DICT = blivedm.BaseHandler._CMD_CALLBACK_DICT.copy()
    #
    # # 入场消息回调
    # async def __interact_word_callback(self, client: blivedm.BLiveClient, command: dict):
    #     print(f"[{client.room_id}] INTERACT_WORD: self_type={type(self).__name__}, room_id={client.room_id},"
    #           f" uname={command['data']['uname']}")
    # _CMD_CALLBACK_DICT['INTERACT_WORD'] = __interact_word_callback  # noqa

    async def _on_heartbeat(self, client: blivedm.BLiveClient, message: blivedm.HeartbeatMessage):
        pass
        #print(f'[{client.room_id}] 当前人气值：{message}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        global streamInfo
        if streaminfos[f'{client.room_id}']["live_status"] ==1:
            cleaned_message = cleanMessage(message)
            await write_to_file(f'{cleaned_message}', streaminfos[f'{client.room_id}']["danmu_file_name"])
        print(f'[{client.room_id}] 弹幕：{message}')

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        pass
        #print(f'[{client.room_id}] 礼物：{message}')

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        pass
        #print(f'[{client.room_id}] 上舰：{message}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        pass
        #print(f'[{client.room_id}] 醒目留言 {message}')


async def main():
    await updateLiveStatus()
    task_1 = asyncio.create_task(run_multi_clients())
    task_2 = asyncio.create_task(updateLiveStatus_loop())
    await task_1
    await task_2

if __name__ == '__main__':
    asyncio.run(main())
