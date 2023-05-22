# blivedm

Python获取bilibili直播弹幕的库，使用WebSocket协议

[协议解释](https://blog.csdn.net/xfgryujk/article/details/80306776)（有点过时了，总体是没错的）

基于本库开发的一个应用：[blivechat](https://github.com/xfgryujk/blivechat)

## 使用说明

1. 需要Python 3.8及以上版本
2. 安装依赖

    ```sh
    pip install -r requirements.txt
    ```
3. 创建路径 danmu/与配置文件相同的主播昵称
4. 运行 ludeng.py
5. 若需要发送弹幕/评论的功能，运行refreshEdge.bat
```
python3 ludeng.py
```

## 路灯说明

新监听房间：
1. 以sampleUserConfig.json为模板，为每个房间分别编写配置文件
    ```
    {
    "FROM_ADDRESS":"发送路灯邮件的邮箱，要求gmail",
    "PASSWORD" : "gmail的[临时密码](https://support.google.com/accounts/answer/185833?hl=en)",
    "ROOM_ID" : "房间号",
    "ROOM_NAME" : "主播昵称",
    "LVL_LIMIT" : 最低记录路灯的牌子等级（含）,
    "KEYWORD" : "标记路灯的关键词",
    "HIGHLIGHT_KEYWORDS" : {"?":["？？", "??"], "关键词":["关键词的变体", "关键词的变体","关键词的变体"]},
    "HIGHLIGHT_TIMEFRAME" : 在这个时间段内,
    "HIGHLIGHT_THRESHOLD" : 超过这个次数被记录,
    "LUDENG_USER" : {"<uid>": "email@email.com"}, 这些人会收到下播是的弹幕邮件
    "NOTIFY_USER" : {"<uid>": "email@email.com"}, 这些人会收到开播时的通知邮件
    "SEND_LIVE_NOTICE" : 1, (是否发送开播通知。1：是，0：否)
    "RENQI_REMIND": -1, (提醒人气票的分钟，不启用设置成-1；启用将使用在edge浏览器登录的账号)
    "LUBO_API": ["https://api.bilibili.com/x/series/archives?mid=<UID>&series_id=<SID>&only_normal=true&sort=desc&pn=1&ps=30",
                "https://api.bilibili.com/x/polymer/space/seasons_archives_list?mid=<UID>&season_id=<SID>&sort_reverse=true&page_num=1&page_size=30"](SID 可以在合集url里找到)
    } 
    ```
2. 将配置文件名加入ludengConfig.json

弹幕存储格式：
时间戳（unix时间）;用户名;UID;是否为表情包;牌子房间号;牌子等级;弹幕内容
