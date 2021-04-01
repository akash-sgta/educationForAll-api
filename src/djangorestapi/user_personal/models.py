from django.db import models

from content_delivery.models import Post
from content_delivery.models import Assignment
from content_delivery.models import Subject

from auth_prime.models import User_Credential

# Create your models here.

class Diary(models.Model):
    diary_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)

    post_id = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    diary_name = models.CharField(max_length=512)
    diary_body = models.TextField()

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        if(self.post_id == None):
            post_id = 'NULL'
        else:
            post_id = self.post_id

        return f"{self.diary_id} || {post_id} || {self.user_credential_id}"

class Submission(models.Model):
    submission_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)

    assignment_id = models.ForeignKey(Post, null=False, blank=False, on_delete=models.CASCADE)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    submission_name = models.CharField(max_length=512)
    submission_body = models.TextField(null=False, blank=False)
    
    submission_external_url_1 = models.URLField(null=True, blank=True)
    submission_external_url_2 = models.URLField(null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.submission_id} || {self.assignment_id} || {self.user_credential_id}"

class Enroll(models.Model):
    subject_id = models.ForeignKey(Subject, null=False, blank=False, on_delete=models.CASCADE)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    made_date = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject_id.subject_name} | {self.user_credential_id.user_f_name}"

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)

    post_id = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

    notification_body = models.TextField(null=False, blank=False)
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.notification_id} | {' '.join(self.notification_body.split()[:10])}..."

class User_Notification_Int(models.Model):
    notification_id = models.ForeignKey(Notification, null=False, blank=False, on_delete=models.CASCADE)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    made_date = models.DateTimeField(auto_now=True)
    prime_1 = models.BooleanField(default=False) # Sent
    prime_2 = models.BooleanField(default=False) # Seen
    
    def __str__(self):
        return f"{self.notification_id.notification_id} | {self.user_credential_id.user_f_name} | {self.prime_1} | {self.prime_2}"
