import datetime

CN_TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))


def unix2Datetime(unixString):
    return datetime.datetime.fromtimestamp(int(unixString) / 1000, datetime.timezone.utc).replace(microsecond=0)


def cn2Datetime(cnString):
    return datetime.datetime.strptime(cnString, '%Y-%m-%d %H:%M:%S').replace(tzinfo=CN_TIMEZONE).replace(microsecond=0)
