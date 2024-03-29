from auth_prime.models import User
from content_delivery.models import Assignment, AssignmentMCQ, Post, Subject
from django.db import models

# Create your models here.

# TODO : Post <=1======N=> Diary
# TODO : User <=1======N=> Diary
class Diary(models.Model):
    post_ref = models.ForeignKey(Post, null=True, blank=True, on_delete=models.SET_NULL)
    user_ref = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    body = models.TextField()

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = f"D [{self.pk}] || {self.post_ref} || {self.user_ref}"
        return data


# TODO : Assignment <=1======N=> Submission
# TODO : User       <=1======N=> Submission
class Submission(models.Model):
    user_ref = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    assignment_ref = models.ForeignKey(Assignment, null=True, blank=False, on_delete=models.SET_NULL)

    body = models.TextField(null=False, blank=False)
    external_url_1 = models.CharField(max_length=128, null=True, blank=True)
    external_url_2 = models.CharField(max_length=128, null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    marks = models.PositiveSmallIntegerField(default=0)  # TODO : Only accessible by Coordinator
    checked = models.BooleanField(default=False)  # TODO : Only accessible by Coordinator

    def __str__(self):
        data = f"S [{self.pk}] || {self.user_ref} || {self.assignment_ref}"
        return data


# TODO : Assignment <=1======N=> SubmissionCode
# TODO : User       <=1======N=> SubmissionCode
class SubmissionMCQ(models.Model):
    user_ref = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    assignment_ref = models.ForeignKey(AssignmentMCQ, null=True, blank=False, on_delete=models.SET_NULL)

    body = models.JSONField(null=False, blank=False)

    made_date = models.DateTimeField(auto_now=True)

    marks = models.PositiveSmallIntegerField(default=0)  # TODO : Only accessible by Coordinator
    checked = models.BooleanField(default=False)  # TODO : Only accessible by Coordinator

    def __str__(self):
        data = f"S [{self.pk}] || {self.user_ref} || {self.assignment_ref}"
        return data


# TODO : User <=M======N=> Subject
class Enroll(models.Model):
    subject_ref = models.ForeignKey(Subject, null=False, blank=False, on_delete=models.CASCADE)
    user_ref = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    made_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        data = f"{self.subject_ref} || {self.user_ref}"
        return data


# TODO : Post <=1======N=> Notification
class Notification(models.Model):
    post_ref = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)

    body = models.TextField(null=False, blank=False)
    made_date = models.DateTimeField(auto_now_add=True)

    prime = models.BooleanField(default=False)  # TODO : T -> Pinned Messages for show

    def __str__(self):
        data = f"N [{self.pk}] || {self.post_ref}"
        return data


# TODO : User_Credential <=M======N=> Notification
class User_Notification(models.Model):
    notification_ref = models.ForeignKey(Notification, null=False, blank=False, on_delete=models.CASCADE)
    user_ref = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)

    prime_1 = models.BooleanField(default=False)  # TODO : T -> Sent
    prime_2 = models.BooleanField(default=False)  # TODO : T -> Seen
    tries = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        data = f"{self.notification_ref} || {self.user_ref}"
        return data
