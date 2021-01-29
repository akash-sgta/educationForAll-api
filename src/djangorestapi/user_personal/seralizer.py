from rest_framework import serializers

from user_personal.models import Diary, Submission

class Diary_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Diary
        fields = (
            'diary_id',
            'post_id',
            'user_credential_id',
            'diary_name',
            'diary_body'
        )

class Submission_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = (
            'submission_id',
            'assignment_id',
            'user_credential_id',
            'submission_name',
            'submission_body_1',
            'submission_body_2',
            'submission_external_url'
        )
