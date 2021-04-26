from django.db import models

from django.core.validators import RegexValidator


import datetime

# Create your models here.

# ---------------------------------------------------------------------------------------------------------------------------------------

class Image(models.Model):
    image_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    image = models.ImageField(max_length=255, null=True, upload_to ='uploads/%Y/%m/%d/')

    def delete(self, *args, **kwargs):
        self.image.delete()
        super().delete(*args, **kwargs)


    def __str__(self):
        return f"{self.image_id} | {self.image}"

# ---------------------------------------------------------------------------------------------------------------------------------------

class User_Profile(models.Model):
    user_profile_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    user_profile_headline = models.TextField(max_length=512, null=False, blank=False)
    user_bio = models.TextField(null=True, blank=True)
    user_english_efficiency = models.PositiveSmallIntegerField(choices=((1,"BEGINNER"), (2,"INTERMEDIATE"), (3,"ADVANCED")), default=1)
    user_git_profile = models.URLField(max_length=256, null=True, blank=True)
    user_linkedin_profile = models.URLField(max_length=256, null=True, blank=True)
    user_roll_number = models.CharField(max_length=14, validators=[
            RegexValidator(
                regex=r'^[1-9]{1}[0-9]{11}$',
                message='12 Digit University Roll Number.',
                code='invalid_roll_number'
            )
        ], null=True, blank=True)
    
    prime = models.BooleanField(default=True) # is student ?
    made_date = models.DateTimeField(auto_now_add=True)

    user_profile_pic = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.user_profile_id} | {self.prime} | {self.user_roll_number}"

class User_Credential(models.Model):
    user_credential_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)
    
    user_profile_id = models.ForeignKey(User_Profile, on_delete=models.SET_NULL, null=True, blank=True)

    user_f_name = models.CharField(max_length=32, null=False, blank=False)
    user_m_name = models.CharField(max_length=32, null=True, blank=True)
    user_l_name = models.CharField(max_length=32, null=False, blank=False)
    user_email = models.EmailField(max_length=255, null=False, blank=False, unique=True)
    user_password = models.TextField(null=False, blank=False)
    user_tg_id = models.TextField(max_length=512, null=True, blank=True)
    user_security_question = models.TextField(null=True, blank=True)
    user_security_answer = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_credential_id} | {self.user_profile_id} | {self.user_f_name} | {self.user_email} | {self.user_tg_id}"

class User_Token_Table(models.Model):
    token_id = models.BigAutoField(primary_key=True)

    user_credential_id = models.ForeignKey(User_Credential, null=True, blank=True, on_delete=models.CASCADE)

    token_hash = models.TextField(default='')
    token_start = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.token_id} | {self.token_start}"

# ---------------------------------------------------------------------------------------------------------------------------------------

class Admin_Privilege(models.Model):
    admin_privilege_id = models.BigAutoField(primary_key=True)
    
    admin_privilege_name = models.CharField(max_length=32)
    admin_privilege_description = models.TextField()

    def __str__(self):
        return f"{self.admin_privilege_id} | {self.admin_privilege_name}"

class Admin_Credential(models.Model):
    admin_credential_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)
    
    user_credential_id = models.ForeignKey(User_Credential, on_delete=models.CASCADE) # automated referential integrity constraint placed

    prime = models.BooleanField(default=False) # is super admin ?
    
    def __str__(self):
        return f'''{self.admin_credential_id} | 
                   {self.user_credential_id.user_credential_id} | 
                   {self.user_credential_id.user_f_name} | 
                   {self.prime}'''

class Admin_Cred_Admin_Prev_Int(models.Model):
    admin_credential_id = models.ForeignKey(Admin_Credential, on_delete=models.CASCADE)
    admin_privilege_id = models.ForeignKey(Admin_Privilege, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.admin_credential_id} | {self.admin_privilege_id}"

# ---------------------------------------------------------------------------------------------------------------------------------------

class Api_Token_Table(models.Model):
    user_name = models.CharField(max_length=255, null=False, blank=False)
    user_email =  models.EmailField(null=False, blank=False)
    user_password = models.CharField(max_length=255, null=False, blank=False)

    user_key_private = models.CharField(max_length=255, null=False, blank=False)
    api_endpoint = models.PositiveSmallIntegerField(choices=((1,"Web Development"), (2,"Android App Development"), (3,"Apple App Development"), (4,"Windows Software Development"), (5,"Linux Software Development"), (6,"Others")), default=1)

    def __str__(self):
        return f'{self.user_name} | {self.user_email}'

# ---------------------------------------------------------------------------------------------------------------------------------------