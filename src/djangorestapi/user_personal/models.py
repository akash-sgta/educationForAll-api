from django.db import models

from content_delivery.models import (
    Post,
    Assignment,
    Subject
)

from auth_prime.models import (
    User_Credential,
)

# Create your models here.

class Diary(models.Model):
    diary_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    post_id = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    diary_name = models.TextField()
    diary_body = models.TextField()
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''{} || D [{}, {}]'''.format(
            self.post_id,
            self.diary_id,
            self.diary_name
        )
        return data

class Submission(models.Model):
    submission_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    submission_name = models.TextField()
    submission_body = models.TextField(null=False, blank=False)
    submission_external_url_1 = models.URLField(null=True, blank=True)
    submission_external_url_2 = models.URLField(null=True, blank=True)
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''SUB [{}, {}] || {}'''.format(
            self.submission_id,
            self.submission_name,
            self.user_credential_id
        )
        return data

class Assignment_Submission_Int(models.Model):
    assignment_id = models.ForeignKey(Assignment, null=False, blank=False, on_delete=models.CASCADE)
    submission_id = models.ForeignKey(Submission, null=False, blank=False, on_delete=models.CASCADE)

    marks = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        data = '''{} || {} || {}'''.format(
            self.assignment_id,
            self.submission_id,
            self.marks
        )
        return data

class Enroll(models.Model):
    subject_id = models.ForeignKey(Subject, null=False, blank=False, on_delete=models.CASCADE)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    made_date = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        data = '''{} || {}'''.format(
            self.subject_id,
            self.user_credential_id
        )
        return data

class Notification(models.Model):
    notification_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    post_id = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

    notification_body = models.TextField(null=False, blank=False)
    made_date = models.DateTimeField(auto_now_add=True)

    prime = models.BooleanField(default=False) # pinned Notification

    def __str__(self):
        data = '''N [{},{}] || {}'''.format(
            self.notification_id,
            self.prime,
            self.post_id
        )
        return data

class User_Notification_Int(models.Model):
    notification_id = models.ForeignKey(Notification, null=False, blank=False, on_delete=models.CASCADE)
    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    made_date = models.DateTimeField(auto_now_add=True)
    prime_1 = models.BooleanField(default=False) # Sent
    prime_2 = models.BooleanField(default=False) # Seen
    tries = models.PositiveBigIntegerField(default=0)
    
    def __str__(self):
        data = '''{} || {} || UNI[{}]'''.format(
            self.notification_id,
            self.user_credential_id,
            self.tries
        )
        return data
