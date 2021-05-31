from rest_framework import serializers

from content_delivery.models import (
    Coordinator,
    Subject,
    Video,
    Forum,
    Reply,
    ReplyToReply,
    Lecture,
    Assignment,
    AssignmentMCQ,
    Post,
)

# ----------------------------------------------


class Coordinator_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinator
        fields = "__all__"


class Subject_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


# ----------------------------------------------


class Video_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = "__all__"


class Forum_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Forum
        fields = "__all__"


class Reply_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = "__all__"


class ReplyToReply_Serializer(serializers.ModelSerializer):
    class Meta:
        model = ReplyToReply
        fields = "__all__"


class Lecture_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Lecture
        fields = "__all__"


class Assignment_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = "__all__"


class AssignmentMCQ_Serializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentMCQ
        fields = "__all__"


# ----------------------------------------------


class Post_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"
