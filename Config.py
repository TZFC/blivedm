import json


class Config:
    userConfigs: dict
    streamInfos: dict
    ludengConfigName: str

    def __init__(self, ludengConfigName):
        self.ludengConfigName = ludengConfigName
        with open(ludengConfigName, 'r') as config:
            configFiles = json.loads(config.read())["configs"]
        userConfigs = {}
        streamInfos = {}
        for userConfig in configFiles:
            with open(userConfig, 'r', encoding="utf-8") as config:
                thisConfig = json.loads(config.read())
                userConfigs[thisConfig["ROOM_ID"]] = thisConfig
                streamInfos[thisConfig["ROOM_ID"]] = {'live_status': 0, 'live_time': '0', 'keyframe': '0',
                                                      'title': '0',
                                                      'last_comment_aids': {api: 0 for api in thisConfig["LUBO_API"]},
                                                      'danmu_file_name': '0', 'last_remind_hour': -1}
        self.userConfigs = userConfigs
        self.streamInfos = streamInfos

    def __str__(self):
        return "UserConfigs: {}, StreamInfos: {}".format(self.userConfigs.__str__(), self.streamInfos.__str__())

    def getConfigs(self):
        return self.userConfigs, self.streamInfos

    async def update(self):
        with open(self.ludengConfigName, 'r') as config:
            configFiles = json.loads(config.read())["configs"]
        for userConfig in configFiles:
            with open(userConfig, 'r', encoding="utf-8") as config:
                thisConfig = json.loads(config.read())
                if thisConfig["ROOM_ID"] not in self.streamInfos.keys():
                    self.streamInfos[thisConfig["ROOM_ID"]] = {'live_status': 0, 'live_time': '0', 'keyframe': '0',
                                                               'title': '0',
                                                               'danmu_file_name': '0', 'last_remind_hour': -1}
                self.userConfigs[thisConfig["ROOM_ID"]] = thisConfig
