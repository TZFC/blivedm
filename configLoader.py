import json

CONFIG_FILE_NAME = "ludengConfig.json"


def loadConfig():
    with open(CONFIG_FILE_NAME, 'r') as config:
        ludengConfig = json.loads(config.read())

    userConfigs = {}
    streamInfos = {}
    for userConfig in ludengConfig["configs"]:
        with open(userConfig, 'r', encoding="utf-8") as config:
            thisConfig = json.loads(config.read())
            userConfigs[thisConfig["ROOM_ID"]] = thisConfig
            streamInfos[thisConfig["ROOM_ID"]] = {'live_status': 0, 'live_time': '0', 'keyframe': '0', 'title': '0',
                                                  'danmu_file_name': '0'}
    return userConfigs, streamInfos
