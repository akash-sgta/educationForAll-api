from django.db import models

from content_delivery.models import Post, Assignment
from auth_prime.models import User_Credential

# Create your models here.

class Diary(models.Model):
    diary_id = models.AutoField(primary_key=True, null=False, blank=False, unique=True)

    post_id = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    diary_name = models.CharField(max_length=512)
    diary_body = models.TextField()

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

    def __str__(self):
        return f"{self.submission_id} || {self.assignment_id} || {self.user_credential_id}"
