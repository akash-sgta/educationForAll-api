from django.db import models

from auth_prime.models import User

from auth_prime.models import Api_Token

# Create your models here.
# TODO : User <=1======N=> Ticket
class Ticket(models.Model):
    ticket_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    ticket_body = models.TextField(null=False, blank=False)
    user_ref = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE
    )
    made_date = models.DateTimeField(auto_now_add=True)
    prime = models.BooleanField(default=False)  # solved tickets

    def __str__(self):
        data = """T [{}] || {}""".format(self.ticket_id, self.user_credential_id)
        return data


# TODO : API <=1======N=> Log
class Log(models.Model):
    log_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    log_body = models.TextField(null=False, blank=False)
    api_token_id = models.ForeignKey(
        Api_Token, blank=False, null=True, on_delete=models.CASCADE
    )
    made_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        data = """L [{}] || {}""".format(self.log_id, self.api_token_id)
        return data
