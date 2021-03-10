from rest_framework import serializers

from content_delivery.models import Coordinator, Subject, Video, Forum, Reply, Lecture, Assignment, Post


# ----------------------------------------------

class Coordinator_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinator
        fields = (
            'coordinator_id',
            'user_credential_id',
            'prime',
            )

class Subject_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = (
            'subject_id',
            'subject_name',
            'subject_description',
            'prime',
        )

# ----------------------------------------------

class Video_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
            'video_id',
            'video_name',
            'video_url',
            'made_date'
        )

class Forum_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = (
            'forum_id',
            'forum_name',
            'made_date'
        )

class Reply_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = (
            'reply_id',
            'forum_id',
            'user_credential_id',
            'reply_body',
            'reply_upvote',
            'reply_downvote',
            'made_date'
        )

class Lecture_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = (
            'lecture_id',
            'lecture_name',
            'lecture_body',
            'lecture_external_url_1',
            'lecture_external_url_2',
            'made_date'
        )

class Assignment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            'assignment_id',
            'assignment_name',
            'assignment_body',
            'assignment_external_url_1',
            'assignment_external_url_2',
            'made_date'
        )

# ----------------------------------------------

class Post_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            'post_id',
            'user_credential_id',
            'subject_id',
            'video_id',
            'forum_id',
            'lecture_id',
            'assignment_id',
            'post_name',
            'post_body',
            'post_views',
            'post_upvote',
            'post_downvote',
            'prime',
            'made_date'
        )