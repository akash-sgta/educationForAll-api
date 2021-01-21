from django.db import models
from django.core.validators import RegexValidator
import datetime

# Create your models here.

class User_Table(models.Model):
    user_id = models.AutoField(primary_key=True)

    user_f_name = models.CharField(max_length=32)
    user_m_name = models.CharField(max_length=32, null=True)
    user_l_name = models.CharField(max_length=32)
    user_email = models.EmailField(max_length=256)
    user_password = models.CharField(max_length=1024)

class Admin_Table(models.Model):
    admin_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_Table, on_delete=models.CASCADE)

VALID_DATE = RegexValidator(r'^(3[01]|[12][0-9]|0[1-9])-(1[0-2]|0[1-9])-[0-9]{4}$')
def get_date():
    day = datetime.date.day
    month = datetime.date.month
    year = datetime.date.year
    exp = f'{day}-{month}-{year}'

    return exp

class Token_Table(models.Model):
    token_id = models.AutoField(primary_key=True)
    token_date_start = models.CharField(default=get_date(), validators=[VALID_DATE], max_length=10)
    token_date_end = models.CharField(default=get_date(), validators=[VALID_DATE], max_length=10)