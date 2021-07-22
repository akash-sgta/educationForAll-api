import os
from datetime import datetime, timedelta
from pathlib import Path

from analytics.models import Permalink
from analytics.serializer import Permalink_Serializer
from auth_prime.models import User_Token, Profile
from content_delivery.models import Assignment, Lecture
from user_personal.models import Submission, User_Notification

from cronjobs.bot import bot

BASE_DIR = Path(__file__).resolve().parent.parent
FILE = os.path.join(BASE_DIR, "log", "cronlog.log")

# ---------------------------------------------------------


def telegram_notification():
    print("\n---------------------------")
    print("TELEGRAM_NOTIFICATION")
    log_data = list()
    now = datetime.now()

    if bot.run():
        notifications = User_Notification.objects.filter(prime_1=False)[:50]
        count = 0
        for notif in notifications:
            tg_id = notif.user_ref.telegram_id
            if tg_id == None:
                notif.tries += 1
                notif.save()
            else:
                notif_main = notif.pk.body
                bot.send_notifications(tg_id, notif_main)
                notif.prime_1 = True
                notif.save()
                count += 1
        log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: NOTIFICATION CRONJOB\t\t:: [.] Notification Sent {count}")

    else:
        log_data.append(
            f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: NOTIFICATION CRONJOB\t\t:: [*] Notification - Could Not Start"
        )

    with open(FILE, "a") as log_file:
        log_file.writelines(log_data)


def token_checker():
    print("\n---------------------------")
    print("TOKEN_CHECKER")
    log_data = list()
    now = datetime.now()

    token_ref = User_Token.objects.all().exclude(pk=22).order_by("id")[:10]  # TODO : Exclude test user for testcase
    token_delete_count = 0
    for token in token_ref:
        then = datetime.strptime(str(token.start).split(".")[0], "%Y-%m-%d %H:%M:%S") + timedelta(hours=48)
        if then < now:
            token.delete()
            token_delete_count += 1
    log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TOKEN CRONJOB\t\t:: [.] Tokens expired : {token_delete_count}")
    with open(FILE, "a") as log_file:
        log_file.writelines(log_data)


def clear_permalinks():
    print("\n---------------------------")
    print("PERMALINK_CHECKER")
    log_data = list()
    now = datetime.now()
    count = 0

    permalinks = Permalink.objects.all().order_by("-pk")[:100]
    for perm in permalinks:
        serialized = Permalink_Serializer(perm, many=False).data
        if "Profile" in serialized["body"]["class"]:
            try:
                Profile.objects.get(pk=serialized["body"]["pk"])
            except Profile.DoesNotExist:
                perm.delete()
                count += 1
        elif "Lecture" in serialized["body"]["class"]:
            try:
                Lecture.objects.get(pk=serialized["body"]["pk"])
            except Lecture.DoesNotExist:
                perm.delete()
                count += 1
        elif "Assignment" in serialized["body"]["class"]:
            try:
                Assignment.objects.get(pk=serialized["body"]["pk"])
            except Assignment.DoesNotExist:
                perm.delete()
                count += 1
        elif "Submission" in serialized["body"]["class"]:
            try:
                Submission.objects.get(pk=serialized["body"]["pk"])
            except Submission.DoesNotExist:
                perm.delete()
                count += 1
        else:
            perm.delete()
            count += 1
    log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: PERMALINK CRONJOB\t\t:: [.] Links expired : {count}")
    with open(FILE, "a") as log_file:
        log_file.writelines(log_data)


def test():
    print("\n---------------------------")
    print("TEST")
    now = datetime.now()
    log_data = list()

    log_data.append(f"\n{now.strftime('%Y-%m-%d %H:%M:%S')} :: TEST CRONJOB\t\t:: [*] POPPED")
    with open(FILE, "a") as log_file:
        log_file.writelines(log_data)
