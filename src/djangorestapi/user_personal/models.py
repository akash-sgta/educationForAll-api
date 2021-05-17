from django.db import models

from content_delivery.models import (
    Post,
    Subject,
)

from auth_prime.models import (
    User,
)

# Create your models here.

# TODO : Post <=1======N=> Diary
# TODO : User <=1======N=> Diary
class Diary(models.Model):
    diary_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    post_ref = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    user_ref = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE
    )

    body = models.TextField()

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = f"D [{self.diary_id}] || {self.post_ref} || {self.user_ref}"
        return data


# TODO : Assignment <=1======N=> Submission
# TODO : User       <=1======N=> Submission
class Submission(models.Model):
    submission_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    user_ref = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE
    )
    post_ref = models.ForeignKey(
        Post, null=True, blank=False, on_delete=models.SET_NULL
    )

    body = models.TextField(null=False, blank=False)
    url_1 = models.URLField(null=True, blank=True)
    url_2 = models.URLField(null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    marks = models.PositiveSmallIntegerField(
        default=0
    )  # TODO : Only accessible by Coordinator

    def __str__(self):
        data = f"S [{self.submission_id}] || {self.user_ref} || {self.post_ref}"
        return data


# TODO : User <=M======N=> Subject
class Enroll(models.Model):
    subject_ref = models.ForeignKey(
        Subject, null=False, blank=False, on_delete=models.CASCADE
    )
    user_ref = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE
    )

    made_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        data = f"{self.subject_ref} || {self.user_ref}"
        return data


# TODO : Post <=1======N=> Notification
class Notification(models.Model):
    notification_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    post_ref = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

    body = models.TextField(null=False, blank=False)
    made_date = models.DateTimeField(auto_now_add=True)

    prime = models.BooleanField(default=False)  # TODO : T -> Pinned Messages for show

    def __str__(self):
        data = f"N [{self.notification_id}] || {self.post_ref}"
        return data


# TODO : User_Credential <=M======N=> Notification
class User_Notification_Int(models.Model):
    notification_ref = models.ForeignKey(
        Notification, null=False, blank=False, on_delete=models.CASCADE
    )
    user_ref = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE
    )

    prime_1 = models.BooleanField(default=False)  # TODO : T -> Sent
    prime_2 = models.BooleanField(default=False)  # TODO : T -> Seen
    tries = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        data = f"{self.notification_ref} || {self.user_ref}"
        return data
