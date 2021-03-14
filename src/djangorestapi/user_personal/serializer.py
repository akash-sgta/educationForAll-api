from rest_framework import serializers

# ------------------------------------------------------------------

from user_personal.models import Diary
from user_personal.models import Submission
from user_personal.models import Notification
from user_personal.models import Enroll
from user_personal.models import User_Notification_Int

# ------------------------------------------------------------------

class Diary_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = (
            'diary_id',
            'post_id',
            'user_credential_id',
            'diary_name',
            'diary_body',
            'made_date'
        )

class Submission_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = (
            'submission_id',
            'assignment_id',
            'user_credential_id',
            'submission_name',
            'submission_body',
            "submission_external_url_1",
            "submission_external_url_2",
            'made_date',
        )

class Notification_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'notification_id',
            'post_id',
            'notification_body',
            'made_date',
        )

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
            'post_id',
            'user_credential_id',
            'made_date',
            'prime_1',
            'prime_2',
        )