import asyncio
import traceback
from datetime import datetime

import requests

from emailUtil import send_start_email, send_ludeng
from sendFunc import renqiRemind, luboComment


def liveStartActions(userConfig, streamInfo, res):
    streamInfo['title'] = res["title"]
    streamInfo['live_time'] = res["live_time"]
    streamInfo['keyframe'] = res["keyframe"]
    if userConfig["SEND_LIVE_NOTICE"] == 1:
        send_start_email(userConfig, streamInfo)
    streamInfo['danmu_file_name'] = "danmu/{}/{}{}路灯.txt".format(
        userConfig["ROOM_NAME"],
        streamInfo['live_time'].replace(" ", "-").replace(":", "-"),
        streamInfo['title'])
    streamInfo['last_remind_hour'] = datetime.now().hour  # do not send reminder on the live start hour
    with open(streamInfo['danmu_file_name'], "a", encoding="utf-8") as ludeng:
        ludeng.write(
            "{}于{}开始直播\n".format(userConfig["ROOM_NAME"], streamInfo['live_time']))


def liveEndActions(userConfig, streamInfo, res):
    send_ludeng(userConfig, streamInfo)
    streamInfo['title'] = res["title"]
    streamInfo['live_time'] = res["live_time"]
    streamInfo['keyframe'] = res["keyframe"]


async def updateLiveStatus(userConfigs, streamInfos):  # 获取直播间开播状态信息
    url = "http://api.live.bilibili.com/room/v1/Room/get_info?room_id="
    for ROOM_ID in streamInfos.keys():
        res = requests.get(url + ROOM_ID).json()["data"]
        if (streamInfos[ROOM_ID]['live_status'] == 0 or streamInfos[ROOM_ID]['live_status'] == 2) and res[
            "live_status"] == 1:  # 刚刚开播
            liveStartActions(userConfigs[ROOM_ID], streamInfos[ROOM_ID], res)
        elif streamInfos[ROOM_ID]['live_status'] == 1 and (
                res["live_status"] == 0 or res["live_status"] == 2):  # 刚刚下播
            liveEndActions(userConfigs[ROOM_ID], streamInfos[ROOM_ID], res)
        elif streamInfos[ROOM_ID]['live_status'] == 1 and res["live_status"] == 1:  # 正在直播
            if datetime.now().minute == userConfigs[ROOM_ID]["RENQI_REMIND"] and datetime.now().hour != \
                    streamInfos[ROOM_ID]['last_remind_hour']:
                streamInfos[ROOM_ID]['last_remind_hour'] = datetime.now().hour
                await renqiRemind(userConfigs[ROOM_ID])
        streamInfos[ROOM_ID]['live_status'] = res["live_status"]  # 0: 未开播 1: 直播中 2: 轮播中
        await luboComment(userConfigs[ROOM_ID], streamInfos[ROOM_ID])


async def updateLiveStatus_loop(myConfig):
    while True:
        try:
            await asyncio.sleep(3)
            await myConfig.update()
            await updateLiveStatus(*myConfig.getConfigs())
        except Exception:
            with open("exception.txt", "a", encoding="utf-8") as log:
                log.write(traceback.format_exc())
