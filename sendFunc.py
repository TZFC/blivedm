import sendUtil

async def renqiRemind(userConfig, streamInfo):
    sendUtil.sendText(text = "送送人气票喵~右上角有免费的人气票喵~", room=userConfig["ROOM_ID"])
