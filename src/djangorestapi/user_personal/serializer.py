from rest_framework import serializers

# ------------------------------------------------------------------

from user_personal.models import Diary, Submission, Notification, Enroll, User_Notification

# ------------------------------------------------------------------


class Diary_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = "__all__"


class Submission_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"


class Notification_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class Enroll_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = "__all__"


class User_Notification_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Notification
        fields = "__all__"
