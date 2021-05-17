from django.db import models

from auth_prime.models import User

# Create your models here.

# ----------------------------------------------


class Coordinator(models.Model):
    coordinator_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    user_ref = models.ForeignKey(
        User, null=False, blank=False, on_delete=models.CASCADE
    )
    prime = models.BooleanField(default=False)  # TODO : T =>

    def __str__(self):
        data = f"{self.user_ref} || C [{self.coordinator_id} {self.prime}]"
        return data


class Subject(models.Model):
    subject_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    name = models.TextField(null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    prime = models.BooleanField(
        default=False
    )  # TODO : T => TO be shown to only logged users

    def __str__(self):
        data = f"S [{self.subject_id} {self.subject_name}]"
        return data


# TODO : Subject <=1======1=> Coordinator
class Subject_Coordinator(models.Model):
    subject_ref = models.ForeignKey(Subject, on_delete=models.CASCADE)
    coordinator_ref = models.ForeignKey(Coordinator, on_delete=models.CASCADE)

    def __str__(self):
        data = f"{self.subject_ref} || {self.coordinator_ref}"
        return data


# --------------------------------------------------------------------------------------------


class Post(models.Model):
    post_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    user_ref = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    subject_id = models.ForeignKey(
        Subject, null=True, blank=True, on_delete=models.SET_NULL
    )

    # Video
    v_url = models.URLField(max_length=1024, null=True, blank=True)
    # Forum
    f_id = models.PositiveBigIntegerField(
        default=None, null=True, blank=True, unique=True
    )
    # Lecture
    l_body = models.TextField(default="", null=True, blank=True)
    l_url_1 = models.URLField(null=True, blank=True)
    l_url_2 = models.URLField(null=True, blank=True)
    # Assignment
    a_body = models.TextField(null=False, blank=False)
    a_url_1 = models.URLField(null=True, blank=True)
    a_url_2 = models.URLField(null=True, blank=True)
    a_score = models.PositiveSmallIntegerField(default=100, null=True, blank=True)
    # Post
    p_name = models.CharField(max_length=128, null=False, blank=False)
    p_body = models.TextField(null=False, blank=False)

    views = models.PositiveBigIntegerField(default=0)
    up = models.IntegerField(default=0)
    down = models.IntegerField(default=0)

    made_date = models.DateTimeField(auto_now=True)
    prime = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        data = (
            f"P [{self.post_id}, {self.p_name}] || {self.user_ref} ||{self.subject_id}"
        )
        return data


# --------------------------------------------------------------------------------------------

# TODO : Post <=1======N=> Reply
class Reply(models.Model):
    reply_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    post_ref = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    user_ref = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    body = models.TextField(null=False, blank=False)
    up = models.IntegerField(default=0, null=True, blank=True)
    down = models.IntegerField(default=0, null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = f"R [{self.reply_id}] || {self.user_ref} || {self.post_ref}"
        return data


# TODO : Reply <=1======N=> Reply2
class ReplyToReply(models.Model):
    reply_id = models.BigAutoField(
        primary_key=True, null=False, blank=False, unique=True
    )

    reply_ref = models.ForeignKey(
        Reply, null=True, blank=True, on_delete=models.CASCADE
    )
    user_ref = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    body = models.TextField(null=False, blank=False)
    up = models.IntegerField(default=0, null=True, blank=True)
    down = models.IntegerField(default=0, null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = f"R2 [{self.reply_id}] || {self.user_ref} || {self.reply_ref}"
        return data


# --------------------------------------------------------------------------------------------
