from django.db import models
from django.core.validators import RegexValidator
import datetime

# Create your models here.

class User_Table(models.Model):
    user_id = models.AutoField(primary_key=True)

    user_f_name = models.CharField(max_length=32)
    user_m_name = models.CharField(max_length=32, null=True, blank=True)
    user_l_name = models.CharField(max_length=32)
    user_email = models.EmailField(max_length=256, unique=True)
    user_password = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.user_id} | {self.user_f_name[0]}.{self.user_l_name}"

class Admin_Privilege(models.Model):
    privilege_id = models.AutoField(primary_key=True)
    
    privilege_name = models.CharField(max_length=32)
    privilege_description = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.privilege_id} | {self.privilege_name}"

class Admin_Table(models.Model):
    admin_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User_Table, on_delete=models.CASCADE) # automated referential integrity constraint placed
    privilege_id = models.ForeignKey(Admin_Privilege, null=True, on_delete=models.SET_NULL) # automated referential integrity constraint placed

    def __str__(self):
        return f"{self.admin_id} | {self.user_id.user_f_name[0]}.{self.user_id.user_l_name}"

VALID_DATE = RegexValidator(r'^(3[01]|[12][0-9]|0[1-9])-(1[0-2]|0[1-9])-[0-9]{4}$')
def get_date():
    day = datetime.date.day
    month = datetime.date.month
    year = datetime.date.year
    exp = f'{day}-{month}-{year}'

    return exp

class Token_Table(models.Model):
    token_id = models.AutoField(primary_key=True)

    token_hash = models.CharField(default='', max_length=512)
    token_date_start = models.CharField(default=get_date(), validators=[VALID_DATE], max_length=10)
    token_date_end = models.CharField(default=get_date(), validators=[VALID_DATE], max_length=10)

    def __str__(self):
        return f"{self.token_id} | {self.token_hash}"