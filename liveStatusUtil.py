import asyncio

import requests

from emailUtil import send_start_email, send_ludeng


def liveStartActions(userConfigs, streamInfos, ROOM_ID, res):
    streamInfos[ROOM_ID]['title'] = res["data"]["title"]
    streamInfos[ROOM_ID]['live_time'] = res["data"]["live_time"]
    streamInfos[ROOM_ID]['keyframe'] = res["data"]["keyframe"]
    if userConfigs[ROOM_ID]["SEND_LIVE_NOTICE"] == 1:
        send_start_email(userConfigs[ROOM_ID], streamInfos[ROOM_ID])
    streamInfos[ROOM_ID]['danmu_file_name'] = "danmu/{}/{}{}路灯.txt".format(
        userConfigs[ROOM_ID]["ROOM_NAME"],
        streamInfos[ROOM_ID]['live_time'].replace(" ", "-").replace(":", "-"),
        streamInfos[ROOM_ID]['title'])
    with open(streamInfos[ROOM_ID]['danmu_file_name'], "a", encoding="utf-8") as ludeng:
        ludeng.write(
            "{}于{}开始直播\n".format(userConfigs[ROOM_ID]["ROOM_NAME"], streamInfos[ROOM_ID]['live_time']))


def liveEndActions(userConfigs, streamInfos, ROOM_ID, res):
    send_ludeng(userConfigs[ROOM_ID], streamInfos[ROOM_ID])
    streamInfos[ROOM_ID]['title'] = res["data"]["title"]
    streamInfos[ROOM_ID]['live_time'] = res["data"]["live_time"]
    streamInfos[ROOM_ID]['keyframe'] = res["data"]["keyframe"]


async def updateLiveStatus(userConfigs, streamInfos):  # 获取直播间开播状态信息
    url = "http://api.live.bilibili.com/room/v1/Room/get_info?room_id="
    for ROOM_ID in streamInfos.keys():
        res = requests.get(url + ROOM_ID).json()
        if (streamInfos[ROOM_ID]['live_status'] == 0 or streamInfos[ROOM_ID]['live_status'] == 2) and res["data"][
            "live_status"] == 1:  # 刚刚开播
            liveStartActions(userConfigs, streamInfos, ROOM_ID, res)
        elif streamInfos[ROOM_ID]['live_status'] == 1 and (
                res["data"]["live_status"] == 0 or res["data"]["live_status"] == 2):  # 刚刚下播
            liveEndActions(userConfigs, streamInfos, ROOM_ID, res)
        else:
            return
        streamInfos[ROOM_ID]['live_status'] = res["data"]["live_status"]  # 0: 未开播 1: 直播中 2: 轮播中


async def updateLiveStatus_loop(userConfigs, streamInfos):
    while True:
        await asyncio.sleep(3)
        await updateLiveStatus(userConfigs, streamInfos)
