from configLoader import loadConfig
from liveStatusUtil import updateLiveStatus, updateLiveStatus_loop

userConfigs, streamInfos = loadConfig()

import asyncio
import blivedm
import aiofiles

async def write_to_file(text, filename):
    async with aiofiles.open(filename, mode='a', encoding="utf-8") as f:
        await f.write(text + "\n")


def cleanMessage(message):
    return f"{message.timestamp};{message.uname};{message.uid};{message.dm_type};{message.medal_room_id};{message.medal_level};{message.msg}"


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
        if streamInfos[f'{client.room_id}']["live_status"] == 1:
            cleaned_message = cleanMessage(message)
            await write_to_file(f'{cleaned_message}', streamInfos[f'{client.room_id}']["danmu_file_name"])

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
    await updateLiveStatus(userConfigs, streamInfos)
    task_1 = asyncio.create_task(run_multi_clients())
    task_2 = asyncio.create_task(updateLiveStatus_loop(userConfigs, streamInfos))
    await task_1
    await task_2


if __name__ == '__main__':
    asyncio.run(main())
