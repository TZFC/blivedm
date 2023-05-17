from sendUtil import updateCredentials, sendText


async def renqiRemind(userConfig, streamInfo):
    updateCredentials()
    sendText(text="送送人气票喵~右上角有免费的人气票喵~", room=userConfig["ROOM_ID"])
