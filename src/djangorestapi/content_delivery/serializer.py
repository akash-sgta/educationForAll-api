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
            'coordinator_id_1',
            'coordinator_id_2',
            'coordinator_id_3',
            'coordinator_id_4',
            'coordinator_id_5',
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
            'video_url'
        )

class Forum_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = (
            'forum_id',
            'forum_name'
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
            'reply_downvote'
        )

class Lecture_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = (
            'lecture_id',
            'lecture_name',
            'lecture_body_1',
            'lecture_body_2',
            'lecture_external_url'
        )

class Assignment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = (
            'assignment_id',
            'assignment_name',
            'assignment_body_1',
            'assignment_body_2',
            'assignment_external_url'
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
            'post_downvote'
        )