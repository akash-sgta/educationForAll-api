from rest_framework import serializers

# ------------------------------------------------------------------

from user_personal.models import (
        Diary,
        Submission,
        Notification,
        Enroll,
        User_Notification_Int,
        Assignment_Submission_Int
    )

# ------------------------------------------------------------------

class Diary_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = "__all__"

class Submission_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = "__all__"

class Assignment_Submission_Int_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment_Submission_Int
        fields = (
            "marks",
            "assignment_id",
            "submission_id"
        )

class Notification_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

class Enroll_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Enroll
        fields = (
            'subject_id',
            'user_credential_id',
            'made_date',
        )

class User_Notification_Int_Serializer(serializers.ModelSerializer):
    class Meta:
        model = User_Notification_Int
        fields = (
            'notification_id',
            'user_credential_id',
            'made_date',
            'prime_1',
            'prime_2',
            'tries'
        )