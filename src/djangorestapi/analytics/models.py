from django.db import models

from auth_prime.models import User_Credential
from auth_prime.models import Api_Token_Table

# Create your models here.

class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)

    ticket_body = models.TextField(null=False, blank=False)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)
    made_date = models.CharField(default="-", max_length=32)
    prime = models.BooleanField(default=False) # solved tickets

    def __str__(self):
        return f"{self.ticket_id} | {self.ticket_body.split()[:10]}..."

class Log(models.Model):
    log_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)

    log_body = models.TextField(null=False, blank=False)
    api_token_id = models.ForeignKey(Api_Token_Table, blank=False, null=True, on_delete=models.CASCADE)
    made_date = models.CharField(default="-", max_length=32)

    def __str__(self):
        return f"{self.log_id} | {self.log_body.split()[:10]}..."