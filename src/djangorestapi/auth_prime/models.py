from django.db import models

import datetime

# Create your models here.

class User_Profile(models.Model):
    user_profile_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)

    user_profile_headline = models.CharField(max_length=512, null=False, blank=False)
    user_bio = models.TextField()
    user_english_efficiency = models.PositiveSmallIntegerField(choices=((1,"BEGINNER"), (2,"INTERMEDIATE"), (3,"ADVANCED")), default=1)
    user_git_profile = models.URLField(max_length=256, null=True, blank=True)
    user_linkedin_profile = models.URLField(max_length=256, null=True, blank=True)
    user_profile_pic_url = models.CharField(max_length=1024)
    user_roll_number = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.user_profile_id} | {self.user_profile_pic_url}"

class User_Credential(models.Model):
    user_credential_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)
    
    user_profile_id = models.ForeignKey(User_Profile, on_delete=models.SET_NULL, null=True, blank=True)

    user_f_name = models.CharField(max_length=32, null=False, blank=False)
    user_m_name = models.CharField(max_length=32, null=True, blank=True)
    user_l_name = models.CharField(max_length=32, null=False, blank=False)
    user_email = models.EmailField(max_length=256, null=False, blank=False, unique=True)
    user_password = models.CharField(max_length=512, null=False, blank=False)
    user_security_question = models.CharField(max_length=512, null=False, blank=False)
    user_security_answer = models.CharField(max_length=512, null=False, blank=False)

    def __str__(self):
        return f"{self.user_credential_id} | {self.user_f_name[0]}.{self.user_l_name}"

class Admin_Privilege(models.Model):
    admin_privilege_id = models.AutoField(primary_key=True)
    
    admin_privilege_name = models.CharField(max_length=32)
    admin_privilege_description = models.CharField(max_length=1024)

    def __str__(self):
        return f"{self.admin_privilege_id} | {self.admin_privilege_name}"

class Admin_Credential(models.Model):
    admin_credential_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)
    
    user_credential_id = models.ForeignKey(User_Credential, on_delete=models.CASCADE) # automated referential integrity constraint placed
    privilege_id_1 = models.ForeignKey(Admin_Privilege, related_name='privilege_id_1', null=True, blank=True, on_delete=models.SET_NULL) # automated referential integrity constraint placed
    privilege_id_2 = models.ForeignKey(Admin_Privilege, related_name='privilege_id_2', null=True, blank=True, on_delete=models.SET_NULL)
    privilege_id_3 = models.ForeignKey(Admin_Privilege, related_name='privilege_id_3', null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"{self.admin_credential_id} | {self.user_credential_id.user_f_name[0]}.{self.user_credential_id.user_l_name}"

class Token_Table(models.Model):
    token_id = models.AutoField(primary_key=True)

    user_credential_id = models.ForeignKey(User_Credential, null=True, blank=True, on_delete=models.CASCADE)

    token_hash = models.CharField(default='', max_length=512)
    token_start = models.CharField(default='dd-mm-yyyy HH:MM:SS', max_length=32)
    token_end = models.CharField(default='dd-mm-yyyy HH:MM:SS', max_length=32)

    def __str__(self):
        return f"{self.token_id} | {self.token_hash}"