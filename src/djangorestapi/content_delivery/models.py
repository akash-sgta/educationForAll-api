from django.db import models

from auth_prime.models import User_Credential

# Create your models here.

# ----------------------------------------------

class Coordinator(models.Model):
    coordinator_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    user_credential_id = models.ForeignKey(User_Credential, null=False, blank=False, on_delete=models.CASCADE)

    prime = models.BooleanField(default=False)

    def __str__(self):
        data = '''C [{}] | U [{} , {}]'''.format(
            self.coordinator_id,
            self.user_credential_id.user_credential_id,
            self.user_credential_id.user_f_name,
        )
        return data

class Subject(models.Model):
    subject_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    subject_name = models.TextField(null=False, blank=False)
    subject_description = models.TextField(null=False, blank=False)

    prime = models.BooleanField(default=False) # prime only to be shown to logged in users

    def __str__(self):
        data = '''S [{}, {}]'''.format(
            self.subject_id,
            self.subject_name
        )
        return data

class Subject_Coordinator_Int(models.Model):

    subject_id = models.ForeignKey(Subject, on_delete=models.CASCADE)
    coordinator_id = models.ForeignKey(Coordinator, on_delete=models.CASCADE)

    def __str__(self):
        data = '''S [{}, {}] | C [{}, {}]'''.format(
            self.subject_id.subject_id,
            self.subject_id.subject_name,
            self.coordinator_id.coordinator_id,
            self.coordinator_id.user_credential_id.user_f_name
        )
        return data

# --------------------------------------------------------------------------------------------

class Video(models.Model):
    video_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    video_name = models.TextField(null=False, blank=False)
    video_url = models.URLField(max_length=1024, null=False, blank=False)
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''V [{}, {}]'''.format(
            self.video_id,
            self.video_name
        )
        return data

class Forum(models.Model):
    forum_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    forum_name = models.TextField(null=False, blank=False)
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''F [{}, {}]'''.format(
            self.forum_id,
            self.forum_name
        )
        return data

class Reply(models.Model):
    reply_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    forum_id = models.ForeignKey(Forum, null=True, blank=True, on_delete=models.CASCADE)
    user_credential_id = models.ForeignKey(User_Credential, null=True, blank=True, on_delete=models.SET_NULL)

    reply_body = models.TextField()
    upvote = models.IntegerField(default=0, null=True, blank=True)
    downvote = models.IntegerField(default=0, null=True, blank=True)

    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''R [{}] | F [{}, {}]'''.format(
            self.reply_id,
            self.forum_id.forum_id,
            self.forum_id.forum_name
        )
        if(self.user_credential_id == None):
            data += ''' | U [Null, Anonymous]'''
        else:
            data += ''' | U [{}, {}]'''.format(
                self.user_credential_id.user_credential_id,
                self.user_credential_id.user_f_name
            )
        return data

class ReplyToReply(models.Model):
    reply_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    reply_to_id = models.ForeignKey(Reply, null=True, blank=True, on_delete=models.CASCADE)
    user_credential_id = models.ForeignKey(User_Credential, null=True, blank=True, on_delete=models.SET_NULL)

    reply_body = models.TextField()
    upvote = models.IntegerField(default=0, null=True, blank=True)
    downvote = models.IntegerField(default=0, null=True, blank=True)
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''R [{}] | R2 [{}]'''.format(
            self.reply_id,
            self.reply_to_id.reply_id
        )
        if(self.user_credential_id == None):
            data += ''' | U [Null, Anonymous]'''
        else:
            data += ''' | U [{}, {}]'''.format(
                self.user_credential_id.user_credential_id,
                self.user_credential_id.user_f_name
            )
        return data

class Lecture(models.Model):
    lecture_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    lecture_name = models.TextField(null=False, blank=False)
    lecture_body = models.TextField(default="", null=False, blank=False)
    lecture_external_url_1 = models.URLField(null=True, blank=True)
    lecture_external_url_2 = models.URLField(null=True, blank=True)
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''L [{}, {}]'''.format(
            self.lecture_id,
            self.lecture_name
        )
        return data

class Assignment(models.Model):
    assignment_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    assignment_name = models.TextField()
    assignment_body = models.TextField(null=False, blank=False)
    assignment_external_url_1 = models.URLField(null=True, blank=True)
    assignment_external_url_2 = models.URLField(null=True, blank=True)
    score = models.PositiveSmallIntegerField(default=100)
    made_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        data = '''A [{}, {}]'''.format(
            self.assignment_id,
            self.assignment_name
        )
        return data

# --------------------------------------------------------------------------------------------

class Post(models.Model):
    post_id = models.BigAutoField(primary_key=True, null=False, blank=False, unique=True)

    user_credential_id = models.ForeignKey(User_Credential, null=True, blank=True, on_delete=models.SET_NULL)
    subject_id = models.ForeignKey(Subject, null=True, blank=True, on_delete=models.SET_NULL)
    
    video_id = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)
    forum_id = models.ForeignKey(Forum, null=True, blank=True, on_delete=models.SET_NULL)
    lecture_id = models.ForeignKey(Lecture, null=True, blank=True, on_delete=models.SET_NULL)
    assignment_id = models.ForeignKey(Assignment, null=True, blank=True, on_delete=models.SET_NULL)

    post_name = models.TextField()
    post_body = models.TextField()
    post_views = models.PositiveBigIntegerField(default=0)
    upvote = models.IntegerField(default=0)
    downvote = models.IntegerField(default=0)
    made_date = models.DateTimeField(auto_now=True)
    prime = models.BooleanField(default=False, null=False, blank=False)

    def __str__(self):
        data = '''P [{}, {}]'''.format(
            self.post_id,
            self.post_name
        )
        if(self.user_credential_id in (None, "")):
            data += '''| U [{}, {}]'''.format("Null", "Abmiguous")
        else:
            data += '''| U [{}, {}]'''.format(self.user_credential_id.user_credential_id, self.user_credential_id.user_f_name)
        data += ''' || {} || {} || {} || {} || {}'''.format(
            self.subject_id,
            self.video_id,
            self.forum_id,
            self.lecture_id,
            self.assignment_id
        )
        return data

# --------------------------------------------------------------------------------------------