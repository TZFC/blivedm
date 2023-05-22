import traceback

from datetimeUtil import unix2Datetime, cn2Datetime, CN_TIMEZONE


def getDeng(config, streamInfo):
    try:
        with open(streamInfo["danmu_file_name"], "r", encoding="utf-8") as danmu:
            danmuText = danmu.readlines()
        start_time = cn2Datetime(streamInfo['live_time'])
        keyword_timestamps = {}  # keyword:[unix timestamp in integers]
        for keyword in config["HIGHLIGHT_KEYWORDS"].keys():
            keyword_timestamps[keyword] = []
        luDeng = danmuText[0]  # 于 <时间> 开始直播
        tiaoZhuan = ""
        for line in danmuText[1:]:
            try:
                timestamp, uname, uid, dm_type, medal_room, medal_level, text = line.split(";", maxsplit=6)
            except:
                continue
            send_time = unix2Datetime(timestamp)
            timediff = send_time - start_time
            # luDeng extraction
            if dm_type == "0" \
                    and medal_room == config["ROOM_ID"] \
                    and int(medal_level) >= config["LVL_LIMIT"] \
                    and text[:len(config["KEYWORD"])] == config["KEYWORD"]:
                luDeng += "{} {} {}\n".format(send_time.astimezone(CN_TIMEZONE).replace(tzinfo=None),
                                              text[len(config["KEYWORD"]):-1], uname)
                tiaoZhuan += "{} {}\n".format(timediff, text[len(config["KEYWORD"]):-1])
            # frequency record
            for keyword in keyword_timestamps.keys():
                for variance in config["HIGHLIGHT_KEYWORDS"][keyword]:
                    if variance in text:
                        keyword_timestamps[keyword].append(int(timestamp))
        # frequency analysis
        frequency_result = ""
        for keyword in keyword_timestamps.keys():
            idx = 0
            density = config["HIGHLIGHT_TIMEFRAME"] * 1000 / config["HIGHLIGHT_THRESHOLD"]
            frequency_periods = {}
            while idx <= len(keyword_timestamps[keyword]) - config["HIGHLIGHT_THRESHOLD"]:
                end_idx = idx + config["HIGHLIGHT_THRESHOLD"]  # not included
                if keyword_timestamps[keyword][end_idx - 1] - keyword_timestamps[keyword][idx] >= int(
                        config["HIGHLIGHT_TIMEFRAME"]) * 1000:
                    # did not meet threshold
                    idx += 1
                    continue
                # meet the highlight threshold in timeframe
                while end_idx < len(keyword_timestamps[keyword]):
                    if keyword_timestamps[keyword][end_idx] - keyword_timestamps[keyword][end_idx - 1] >= density:
                        if keyword in frequency_periods.keys():
                            frequency_periods[keyword].append((idx, end_idx))
                        else:
                            frequency_periods[keyword] = [(idx, end_idx)]
                        break
                    # keep elongating index range while interval is less than density
                    end_idx += 1
                if end_idx == len(keyword_timestamps[keyword]):
                    if keyword in frequency_periods.keys():
                        frequency_periods[keyword].append((idx, end_idx))
                    else:
                        frequency_periods[keyword] = [(idx, end_idx)]
                idx = end_idx
            if keyword in frequency_periods.keys():
                frequency_result += "{} 在 ".format(keyword)
                for (start, end) in frequency_periods[keyword]:
                    frequency_result += "{}({}条), ".format(
                        unix2Datetime(str(keyword_timestamps[keyword][start])).astimezone(CN_TIMEZONE).replace(
                            tzinfo=None),
                        end - start)
                frequency_result += "\n"
        # Compose Ludeng
        body = "路灯：\n" + luDeng + "\n" + "录播跳转：\n" + tiaoZhuan + "\n" + frequency_result + "\n"
        with open("danmu/{}/{}{}.txt".format(
                config["ROOM_NAME"],
                streamInfo['live_time'].replace(" ", "-").replace(":", "-")[:13],
                streamInfo['title']), "a", encoding="utf-8") as tiaoZhuanFile:
            tiaoZhuanFile.write(tiaoZhuan)
        return body
    except Exception:
        with open("exception.txt", "a", encoding="utf-8") as log:
            log.write(traceback.format_exc())
        return ""
