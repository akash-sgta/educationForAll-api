from auth_prime.models import Api_Token, User
from django.db import models


# Create your models here.
# TODO : User <=1======N=> Ticket
class Ticket(models.Model):
    body = models.JSONField(null=False, blank=False)
    user_ref = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    made_date = models.DateTimeField(auto_now_add=True)
    prime = models.BooleanField(default=False)  # solved tickets

    def __str__(self):
        data = f"T [{self.pk}] || {self.user_ref}"
        return data


# TODO : API <=1======N=> Log
class Log(models.Model):
    body = models.JSONField(null=False, blank=False)
    api_token_ref = models.ForeignKey(Api_Token, blank=False, null=True, on_delete=models.CASCADE)
    made_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        data = f"L [{self.pk}] || {self.api_token_ref}"
        return data


class Permalink(models.Model):
    ref = models.JSONField() # FIX : Set cronjob
    name = models.CharField(max_length=32, null=False, blank=False)
    body = models.URLField(null=False, blank=False)

    def __str__(self):
        data = f"PL [{self.pk} | {self.name} | {self.body[:32]}]"
        return data
