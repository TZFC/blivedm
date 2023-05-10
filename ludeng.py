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
    # send start notification
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
    # send current ludeng with attached danmu record
    msg = MIMEMultipart()
    msg["From"] = config["FROM_ADDRESS"]
    msg["To"] = ",".join(config["LUDENG_USER"].values())
    msg["Subject"] = "{}于{}".format(config['ROOM_NAME'], streamInfo["danmu_file_name"][:-4])
    body = getDeng(config, streamInfo)
    msg.attach(MIMEText(body, "plain"))
    p = MIMEBase("application", "octet-stream")
    with open(streamInfo["danmu_file_name"], "rb") as attachment:
        p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header("Content-Disposition", "attachment", filename=streamInfo["danmu_file_name"])
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
        if streaminfos[ROOM_ID]['live_status'] == 0 and res["data"]["live_status"] == 1:  # 刚刚开播
            streaminfos[ROOM_ID]['title'] = res["data"]["title"]
            streaminfos[ROOM_ID]['live_time'] = res["data"]["live_time"]
            streaminfos[ROOM_ID]['keyframe'] = res["data"]["keyframe"]
            if userConfigs[ROOM_ID]["SEND_LIVE_NOTICE"] == 1:
                send_start_email(userConfigs[ROOM_ID], streaminfos[ROOM_ID])
            streaminfos[ROOM_ID]['danmu_file_name'] = "{}{}路灯.txt".format(
                streaminfos[ROOM_ID]['live_time'].replace(" ", "-").replace(":", "-"), streaminfos[ROOM_ID]['title'])
            with open(streaminfos[ROOM_ID]['danmu_file_name'], "a", encoding="utf-8") as ludeng:
                ludeng.write(
                    "{}于{}开始直播\n".format(userConfigs[ROOM_ID]["ROOM_NAME"], streaminfos[ROOM_ID]['live_time']))
        elif streaminfos[ROOM_ID]['live_status'] == 1 and (
                res["data"]["live_status"] == 0 or res["data"]["live_status"] == 2):  # 刚刚下播
            send_ludeng(userConfigs[ROOM_ID], streaminfos[ROOM_ID])
            streaminfos[ROOM_ID]['title'] = res["data"]["title"]
            streaminfos[ROOM_ID]['live_time'] = res["data"]["live_time"]
            streaminfos[ROOM_ID]['keyframe'] = res["data"]["keyframe"]
        streaminfos[ROOM_ID]['live_status'] = res["data"]["live_status"]  # 0: 未开播 1: 直播中 2: 轮播中


async def updateLiveStatus_loop():
    while True:
        await asyncio.sleep(3)
        await updateLiveStatus()


import datetime

cntimezone = datetime.timezone(datetime.timedelta(hours=8))


def unix2Datetime(unixString):
    return datetime.datetime.fromtimestamp(int(unixString) / 1000, datetime.timezone.utc).replace(microsecond=0)


def cn2Datetime(cnString):
    cntimezone = datetime.timezone(datetime.timedelta(hours=8))
    return datetime.datetime.strptime(cnString, '%Y-%m-%d %H:%M:%S').replace(tzinfo=cntimezone).replace(microsecond=0)


def getDeng(config, streamInfo):
    with open(streamInfo["danmu_file_name"], "r", encoding="utf-8") as danmu:
        danmuText = danmu.readlines()
    start_time = cn2Datetime(streamInfo['live_time'])
    keyword_timestamps = {}  # keyword:[unix timestamp in integers]
    for keyword in config["HIGHLIGHT_KEYWORDS"].keys():
        keyword_timestamps[keyword] = []
    luDeng = danmuText[0]
    tiaoZhuan = ""
    for line in danmuText[1:]:
        timestamp, uname, uid, dm_type, medal_room, medal_level, text = line.split(";", maxsplit=6)
        send_time = unix2Datetime(timestamp)
        timediff = send_time - start_time
        # luDeng extraction
        if dm_type == "0" \
            and medal_room == config["ROOM_ID"] \
            and int(medal_level) >= config["LVL_LIMIT"] \
            and text[:len(config["KEYWORD"])] == config["KEYWORD"]:
            luDeng += "{} {} {}\n".format(send_time.astimezone(cntimezone).replace(tzinfo=None),
                                          text[len(config["KEYWORD"]):], uname)
            tiaoZhuan += "{} {}\n".format(timediff, text[len(config["KEYWORD"]):])
        # frequency record
        for keyword in keyword_timestamps.keys():
            for variance in config["HIGHLIGHT_KEYWORDS"][keyword]:
                if variance in text:
                    keyword_timestamps[keyword].append(int(timestamp))
    # frequency analysis
    frequency_result = ""
    for keyword in keyword_timestamps.keys():
        idx = 0
        density = config["HIGHLIGHT_TIMEFRAME"] * 1000 / config["HIGHLIGHT_THRESHOLD"]
        frequency_periods = {}
        while idx <= len(keyword_timestamps[keyword]) - config["HIGHLIGHT_THRESHOLD"]:
            end_idx = idx + config["HIGHLIGHT_THRESHOLD"]  # not included
            if keyword_timestamps[keyword][end_idx - 1] - keyword_timestamps[keyword][idx] >= int(
                    config["HIGHLIGHT_TIMEFRAME"]) * 1000:
                # did not meet threshold
                idx += 1
                continue
            # meet the highlight threshold in timeframe
            while end_idx < len(keyword_timestamps[keyword]):
                if keyword_timestamps[keyword][end_idx] - keyword_timestamps[keyword][end_idx - 1] >= density:
                    if keyword in frequency_periods.keys():
                        frequency_periods[keyword].append((idx, end_idx))
                    else:
                        frequency_periods[keyword] = [(idx, end_idx)]
                    break
                # keep elongating index range while interval is less than density
                end_idx += 1
            if end_idx == len(keyword_timestamps[keyword]):
                if keyword in frequency_periods.keys():
                    frequency_periods[keyword].append((idx, end_idx))
                else:
                    frequency_periods[keyword] = [(idx, end_idx)]
            idx = end_idx
        if keyword in frequency_periods.keys():
            frequency_result += "{} 在 ".format(keyword)
            for (start, end) in frequency_periods[keyword]:
                frequency_result += "{}({}条), ".format(
                    unix2Datetime(str(keyword_timestamps[keyword][start])).astimezone(cntimezone).replace(tzinfo=None),
                    end - start)
            frequency_result += "\n"
    # Compose Ludeng
    body = luDeng + "\n" + tiaoZhuan + "\n" + frequency_result
    return body


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
        await f.write(text + "\n")


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
        # print(f'[{client.room_id}] 当前人气值：{message}')

    async def _on_danmaku(self, client: blivedm.BLiveClient, message: blivedm.DanmakuMessage):
        global streamInfo
        if streaminfos[f'{client.room_id}']["live_status"] == 1:
            cleaned_message = cleanMessage(message)
            await write_to_file(f'{cleaned_message}', streaminfos[f'{client.room_id}']["danmu_file_name"])
        print(f'[{client.room_id}] 弹幕：{message}')

    async def _on_gift(self, client: blivedm.BLiveClient, message: blivedm.GiftMessage):
        pass
        # print(f'[{client.room_id}] 礼物：{message}')

    async def _on_buy_guard(self, client: blivedm.BLiveClient, message: blivedm.GuardBuyMessage):
        pass
        # print(f'[{client.room_id}] 上舰：{message}')

    async def _on_super_chat(self, client: blivedm.BLiveClient, message: blivedm.SuperChatMessage):
        pass
        # print(f'[{client.room_id}] 醒目留言 {message}')


async def main():
    await updateLiveStatus()
    task_1 = asyncio.create_task(run_multi_clients())
    task_2 = asyncio.create_task(updateLiveStatus_loop())
    await task_1
    await task_2


if __name__ == '__main__':
    asyncio.run(main())
