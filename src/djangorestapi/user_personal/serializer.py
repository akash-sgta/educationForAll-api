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
        fields = (
            "subject_id",
            "user_credential_id",
            "made_date",
        )


class User_Notification_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Notification
        fields = ("notification_id", "user_credential_id", "made_date", "prime_1", "prime_2", "tries")
