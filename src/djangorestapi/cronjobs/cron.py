import os
from django.conf import settings
from datetime import datetime, timedelta

#-----------------------------------------------

def telegram_notification():

  from cronjobs.automatron import TG_BOT
  
  from user_personal.models import (
    User_Notification_Int,
    Notification,
  )
  from auth_prime.models import (
    User_Credential,
  )

  with open(os.path.join(BASE_DIR, 'config', 'ambiguous', 'TG_KEY.txt'), 'r') as key:
    TG_TOKEN = key.read().strip()[:-2]
  
  bot = TG_BOT(TG_TOKEN)
  if(bot.run()):
    many_notification = User_Notification_Int.objects.filter(prime_1=False)[:100]
    if(len(many_notification) < 1):
      print("[Notification Count] : 0")
    else:
      print(f"[Notification Count] : {len(many_notification)}")
      for single_notification in many_notification:
        try:
          user_cred_ref = User_Credential.object.get(user_credential_id = single_notification.user_credential_id.user_credential_id)
        except User_Credential.DoesNotExist:
          pass
        else:
          if(user_cred_ref.user_tg_id in (None, "")):
            single_notification.tries += 1
            single_notification.save()
          else:
            notify = single_notification.notification_id
            date = notify.made_date.split("T")[0]
            body = " ".join(notify.notification_body.split(" ")[:10])
            text = f"{date}\n\n{body}...[Read More]"
            bot.send_notifications(user_cred_ref.user_tg_id, text)
  else:
    print("[TELEGRAM BOT NOT FUNCTIONAL]")

def token_cleaner():
  from auth_prime.models import (
    User_Token_Table,
  )
  
  now = datetime.strptime(datetime.now().strftime("%y-%m-%d %H:%M:%S"), "%y-%m-%d %H:%M:%S")
  user_tokens = User_Token_Table.objects.all().order_by('token_id')[:100]
  if(len(user_tokens) < 1)
    print("[Hash Count] : 0")
  else:
    print(f"[Hash Count] : {len(user_tokens)}")
    for token in user_tokens:
      then = datetime.strptime(token.token_start.strftime("%y-%m-%d %H:%M:%S"), "%y-%m-%d %H:%M:%S") +timedelta(hours=48)
      if(now < then):
        token.delete()
