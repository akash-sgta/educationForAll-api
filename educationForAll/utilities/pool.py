from django.conf import settings

import hashlib
import string
import random
from datetime import datetime, timedelta

## ============================================================================= ##
# Pool functions here


def string2hashHex(*args):
    if len(args) == 0:
        raise KeyError("No arguments passed")
    else:
        data = settings.SECRET_KEY.join(args)
        return "md5_" + hashlib.md5(data.encode()).hexdigest()


def randomGenerator(length=225, onlyNum=False):
    num = string.digits
    if onlyNum:
        choices = list(num)
    else:
        lower = string.ascii_lowercase
        upper = string.ascii_uppercase
        # symbols = string.punctuation
        choices = list(num + lower + upper)

    return "".join([random.choice(choices) for _ in range(length)])


def datetime2epochms(dt, add_hours=0, add_minutes=0, add_seconds=0, add_Days=0, add_Months=0, add_Years=0):
    if type(dt) != type(datetime.now()):
        raise TypeError("Argument should be : datetime.datetime.now()")
    else:
        ms_from_epoch = dt
        tdelta = list()
        if add_hours > 0:
            tdelta.append(timedelta(hours=add_hours))
        if add_minutes > 0:
            tdelta.append(timedelta(minutes=add_minutes))
        if add_seconds > 0:
            tdelta.append(timedelta(seconds=add_seconds))
        if add_Days > 0:
            tdelta.append(timedelta(days=add_Days))
        if add_Months > 0:
            tdelta.append(timedelta(days=add_Months * 30))
        if add_Years > 0:
            tdelta.append(timedelta(days=add_Years * 365))

        for td in tdelta:
            ms_from_epoch += td

        return int(ms_from_epoch.timestamp() * 1000)


def epochms2datetime(epoch):
    return datetime.fromtimestamp(epoch // 1000)
