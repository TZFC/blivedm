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

3. 例程看[sample.py](./sample.py)

## 路灯说明

新监听房间：
1. 以sampleUserConfig.json为模板编写配置文件
2. 将配置文件名加入ludengConfig.json
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
    "BLOCKED_USER" : [], 这些人的路灯不会被记录 （因为没有这个需求, 暂未实现）
    "SEND_LIVE_NOTICE" : 1 (是否发送开播通知。1：是，0：否)
    }
    ```
弹幕存储格式：
时间戳（unix时间）;用户名;UID;是否为表情包;牌子房间号;牌子等级;弹幕内容
