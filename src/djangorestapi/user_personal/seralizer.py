from rest_framework import serializers

# ------------------------------------------------------------------

from user_personal.models import Diary
from user_personal.models import Submission

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
            'made_date'
        )
