import os
import re

import requests

from sendUtil import updateCredentials, sendText, sendComment


async def renqiRemind(userConfig):
    updateCredentials()
    sendText(text="送送人气票喵~上方有免费的人气票喵~", room=userConfig["ROOM_ID"])


async def luboComment(userConfig, streamInfo):
    if userConfig["LUBO_API"] == []:
        return
    lesser_file = "9"
    for repo in userConfig["LUBO_API"]:
        try:
            latest = requests.get(repo).json()["data"]['archives'][0]
        except:
            with open("exception.txt", "a", encoding="utf-8") as log:
                log.write("{} has no archive".format(repo))
            continue
        filename = translateTitle(latest["title"])
        if filename == "invalid title":
            streamInfo["last_comment_titles"][repo] = latest["title"]
            continue
        if filename < lesser_file:
            lesser_file = filename
        if latest["title"] == streamInfo["last_comment_titles"][repo]:
            continue
        else:
            try:
                with open("danmu/{}/{}".format(userConfig["ROOM_NAME"], filename), "r",
                          encoding="utf-8") as commentFile:
                    commentText = commentFile.read()
                updateCredentials()
                sendComment(commentText, latest["aid"])
            except:
                with open("exception.txt", "a", encoding="utf-8") as log:
                    log.write("{} not found for {}\n".format(filename, latest["title"]))
        streamInfo["last_comment_titles"][repo] = latest["title"]
    if lesser_file == "9": # in case api returns unexpected response
        return
    for file in os.listdir("danmu/{}".format(userConfig["ROOM_NAME"])):
        if file <= lesser_file:
            os.remove("danmu/{}/{}".format(userConfig["ROOM_NAME"], file))


def translateTitle(luboTitle) -> str:
    # expect lubo Title to have 非数字内容<year>年<month>月<date>日<hour>非数字内容 as the last 4 separated integer segments
    pattern = r'[^0-9]*([0-9]+)年([0-9]+)月([0-9]+)日([0-9]+)[^0-9]*'
    found = re.findall(pattern, luboTitle)
    if len(found)==1:
        segments = found[0]
    else:
        return "invalid title"
    filled_segments = [x if len(x) > 1 else "0" + x for x in segments]
    return "-".join(filled_segments) + ".txt"
