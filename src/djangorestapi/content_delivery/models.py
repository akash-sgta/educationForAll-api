from django.db import models

from auth_prime.models import User

# Create your models here.

# ----------------------------------------------


class Coordinator(models.Model):
    user_ref = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    prime = models.BooleanField(default=False)  # TODO : T =>

    def __str__(self):
        data = f"{self.user_ref} || C [{self.pk} {self.prime}]"
        return data


class Subject(models.Model):
    name = models.CharField(max_length=128, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    prime = models.BooleanField(default=False)  # TODO : T => TO be shown to only logged users

    def __str__(self):
        data = f"S [{self.pk} {self.name}]"
        return data


# TODO : Subject <=M======N=> Coordinator
class Subject_Coordinator(models.Model):
    subject_ref = models.ForeignKey(Subject, on_delete=models.CASCADE)
    coordinator_ref = models.ForeignKey(Coordinator, on_delete=models.CASCADE)

    def __str__(self):
        data = f"{self.subject_ref} || {self.coordinator_ref}"
        return data


# --------------------------------------------------------------------------------------------


class Video(models.Model):
    url = models.URLField(max_length=256, null=False, blank=False)

    def __str__(self):
        data = f"V [{self.pk}, {self.url}]"
        return data


class Forum(models.Model):
    def __str__(self):
        data = f"F [{self.pk}]"
        return data


class Lecture(models.Model):
    body = models.TextField(default="", null=False, blank=False)
    external_url_1 = models.URLField(max_length=255, null=True, blank=True)
    external_url_2 = models.URLField(max_length=255, null=True, blank=True)

    def __str__(self):
        data = f"L [{self.pk}]"
        return data


class Assignment(models.Model):
    body = models.TextField(null=False, blank=False)
    external_url_1 = models.URLField(max_length=255, null=True, blank=True)
    external_url_2 = models.URLField(max_length=255, null=True, blank=True)
    total_score = models.PositiveSmallIntegerField(default=100, null=True, blank=True)

    def __str__(self):
        data = f"A [{self.pk}]"
        return data


class AssignmentMCQ(models.Model):
    body = models.JSONField(null=False, blank=False)
    total_score = models.PositiveSmallIntegerField(default=100, null=True, blank=True)

    def delete(self, *args, **kwargs):
        self.testdoc.delete()
        super().delete(*args, **kwargs)

    def __str__(self):
        data = f"A [{self.pk}]"
        return data


class Post(models.Model):
    user_ref = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    subject_ref = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.CASCADE)
    lecture_ref = models.ForeignKey(Lecture, null=True, blank=True, on_delete=models.SET_NULL)
    forum_ref = models.ForeignKey(Forum, null=True, blank=True, on_delete=models.SET_NULL)
    assignment_ref = models.ForeignKey(Assignment, null=True, blank=True, on_delete=models.SET_NULL)
    assignmentMCQ_ref = models.ForeignKey(AssignmentMCQ, null=True, blank=True, on_delete=models.SET_NULL)
    video_ref = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)

    name = models.CharField(max_length=128, null=False, blank=False)
    body = models.TextField(null=False, blank=False)

    views = models.PositiveBigIntegerField(default=0)
    up = models.IntegerField(default=0)
    down = models.IntegerField(default=0)

    made_date = models.DateTimeField(auto_now=True)
    prime = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        data = f"P [{self.pk}] || {self.user_ref} ||{self.subject_ref} || {self.lecture_ref} || {self.forum_ref} || {self.assignment_ref} || {self.video_ref}"
        return data


# --------------------------------------------------------------------------------------------

# TODO : Post <=1======N=> Reply
class Reply(models.Model):
    forum_ref = models.ForeignKey(Forum, null=True, blank=True, on_delete=models.CASCADE)
    user_ref = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    body = models.TextField(null=False, blank=False)
    up = models.IntegerField(default=0, null=True, blank=True)
    down = models.IntegerField(default=0, null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = f"R [{self.pk}] || {self.user_ref} || {self.forum_ref}"
        return data


# TODO : Reply <=1======N=> Reply2
class ReplyToReply(models.Model):
    reply_ref = models.ForeignKey(Reply, null=True, blank=True, on_delete=models.CASCADE)
    user_ref = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    body = models.TextField(null=False, blank=False)
    up = models.IntegerField(default=0, null=True, blank=True)
    down = models.IntegerField(default=0, null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = f"R2 [{self.id}] || {self.user_ref} || {self.reply_ref}"
        return data


# --------------------------------------------------------------------------------------------
